import pytest

from blockchain_tracing_engine.core.bounded_traversal import trace_bounded


def event(tx_hash, sender, recipient, block, log=0):
    return {
        "hash": tx_hash,
        "from": sender,
        "to": recipient,
        "blockNumber": str(block),
        "logIndex": str(log),
        "timeStamp": str(block * 12),
        "value": "1000000",
    }


def test_traces_outgoing_transfers_breadth_first_and_normalises_addresses():
    graph = {
        "0xa": [event("tx1", "0xA", "0xB", 1)],
        "0xb": [event("tx2", "0xb", "0xc", 2)],
        "0xc": [event("tx3", "0xc", "0xd", 3)],
    }
    calls = []

    result = trace_bounded(
        "0xA",
        lambda address: calls.append(address) or graph.get(address, []),
        max_depth=2,
    )

    assert result.nodes == {"0xa", "0xb", "0xc"}
    assert [(edge["from"], edge["to"]) for edge in result.edges] == [
        ("0xa", "0xb"),
        ("0xb", "0xc"),
    ]
    assert calls == ["0xa", "0xb"]
    assert result.node_depths == {"0xa": 0, "0xb": 1, "0xc": 2}


def test_prevents_cycles_and_duplicate_transfer_events():
    graph = {
        "0xa": [
            event("tx1", "0xa", "0xb", 1),
            event("tx1", "0xa", "0xb", 1),
        ],
        "0xb": [event("tx2", "0xb", "0xa", 2)],
    }
    result = trace_bounded("0xa", lambda address: graph.get(address, []), max_depth=4)

    assert len(result.edges) == 2
    assert result.nodes == {"0xa", "0xb"}


def test_respects_api_call_budget():
    graph = {
        "0xa": [event("tx1", "0xa", "0xb", 1)],
        "0xb": [event("tx2", "0xb", "0xc", 2)],
    }
    result = trace_bounded(
        "0xa",
        lambda address: graph.get(address, []),
        max_depth=4,
        max_api_calls=1,
    )

    assert result.api_calls == 1
    assert "api_call_budget" in result.stop_reasons


def test_rejects_invalid_budgets():
    with pytest.raises(ValueError):
        trace_bounded("0xa", lambda _: [], max_depth=-1)
