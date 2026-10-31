import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from blockchain_tracing_engine.core.chain_trace import (
    fetch_transactions,
    filter_transactions_by_time,
    build_edges,
    build_graph,
    expand_graph
)

@patch("blockchain_tracing_engine.core.chain_trace.requests.get")
@patch("blockchain_tracing_engine.core.chain_trace.os.getenv")
def test_fetch_transactions_success(mock_getenv, mock_get):
    mock_getenv.return_value = "fake-api-key"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "1",
        "result": [{"hash": "0x123"}]
    }

    mock_get.return_value = mock_response

    result = fetch_transactions(
        "Ethereum Mainnet",
        "0xabc",
        "0xcontract"
    )

    assert isinstance(result, list)
    assert result[0]["hash"] == "0x123"


@patch("blockchain_tracing_engine.core.chain_trace.requests.get")
def test_fetch_transactions_no_data(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "0",
        "result": []
    }

    mock_get.return_value = mock_response

    result = fetch_transactions("Ethereum Mainnet", "0xabc", "0xcontract")

    assert result == []


def test_filter_transactions_by_time():
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 10)

    txs = [
        {
            "timeStamp": str(int(datetime(2024, 1, 5).timestamp())),
            "hash": "1",
            "from": "a",
            "to": "b",
            "tokenName": "USDT",
            "tokenSymbol": "USDT",
            "value": "100"
        },
        {
            "timeStamp": str(int(datetime(2023, 1, 1).timestamp())),
            "hash": "2",
            "from": "a",
            "to": "b",
            "tokenName": "USDT",
            "tokenSymbol": "USDT",
            "value": "100"
        }
    ]

    result = filter_transactions_by_time(start, end, txs)

    assert len(result) == 1
    assert result[0]["hash"] == "1"


def test_build_edges():
    txs = [
        {
            "from": "A",
            "to": "B",
            "hash": "123",
            "tokenName": "USDT",
            "tokenSymbol": "USDT",
            "value": "100",
            "timeStamp": str(int(datetime(2024, 1, 1).timestamp()))
        }
    ]

    edges = build_edges(txs)

    assert len(edges) == 1
    assert edges[0]["from"] == "A"
    assert edges[0]["to"] == "B"


def test_build_graph():
    edges = [
        {
            "from": "A",
            "to": "B",
            "hash": "1",
            "tokenName": "USDT",
            "tokenSymbol": "USDT",
            "value": "100",
            "timeStamp": datetime.utcnow()
        }
    ]

    graph = build_graph(edges)

    assert "A" in graph
    assert graph["A"][0]["to"] == "B"


@patch("blockchain_tracing_engine.core.chain_trace.time.sleep", return_value=None)
@patch("blockchain_tracing_engine.core.chain_trace.fetch_transactions")
def test_expand_graph(mock_fetch, mock_sleep):
    mock_fetch.return_value = [
        {
            "from": "0xa",
            "to": "0xb",
            "hash": "tx1",
            "tokenName": "USDT",
            "tokenSymbol": "USDT",
            "value": "100",
            "timeStamp": str(int(datetime(2024, 1, 1).timestamp()))
        }
    ]

    graph = {}

    result = expand_graph(
        graph=graph,
        address="0xa",
        depth=2,
        start_datetime=datetime(2024, 1, 1),
        end_datetime=datetime(2024, 12, 31)
    )

    assert "0xa" in result
    assert len(result["0xa"]) > 0