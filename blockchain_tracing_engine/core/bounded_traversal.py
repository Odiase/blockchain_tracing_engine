"""Bounded, deterministic traversal of ERC-20 transfer events.

The module is provider-agnostic: callers supply a function that returns transfer
records for a wallet. It deliberately records observed transfer connectivity;
it does not claim to track fungible token units or wallet ownership.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


@dataclass
class TraversalResult:
    """Result and audit metadata for one bounded graph expansion."""

    root_address: str
    max_depth: int
    nodes: set[str] = field(default_factory=set)
    edges: list[dict[str, Any]] = field(default_factory=list)
    node_depths: dict[str, int] = field(default_factory=dict)
    expanded_addresses: list[str] = field(default_factory=list)
    api_calls: int = 0
    stop_reasons: list[str] = field(default_factory=list)


def _address(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Transfer event contains an invalid wallet address")
    return value.strip().lower()


def _event_order(event: dict[str, Any]) -> tuple[int, int, int, str]:
    """Order by block/log position; timestamp and hash are deterministic fallbacks."""
    return (
        int(event.get("blockNumber") or 0),
        int(event.get("logIndex") or 0),
        int(event.get("timeStamp") or 0),
        str(event.get("hash") or "").lower(),
    )


def _event_identity(event: dict[str, Any]) -> tuple[str, str]:
    tx_hash = str(event.get("hash") or "").lower()
    log_index = event.get("logIndex")
    if not tx_hash:
        raise ValueError("Transfer event is missing its transaction hash")
    # A transaction can contain multiple Transfer logs; include logIndex when present.
    return tx_hash, str(log_index) if log_index is not None else "no-log-index"


def trace_bounded(
    root_address: str,
    fetch_transfers: Callable[[str], Iterable[dict[str, Any]]],
    *,
    max_depth: int = 2,
    max_nodes: int = 250,
    max_edges: int = 1_000,
    max_api_calls: int = 250,
) -> TraversalResult:
    """Breadth-first expansion of outgoing transfer events within explicit budgets.

    Depth 0 is the root wallet. A recipient discovered from a depth-d wallet is
    assigned depth d+1. Each address is expanded at most once. The fetch callback
    should apply the configured chain, token contract, and investigation time range.
    """
    if max_depth < 0:
        raise ValueError("max_depth must be zero or greater")
    if min(max_nodes, max_edges, max_api_calls) < 1:
        raise ValueError("node, edge, and API-call budgets must be positive")

    root = _address(root_address)
    result = TraversalResult(root_address=root, max_depth=max_depth)
    result.nodes.add(root)
    result.node_depths[root] = 0

    queue = deque([root])
    expanded: set[str] = set()
    seen_events: set[tuple[str, str]] = set()

    while queue:
        current = queue.popleft()
        depth = result.node_depths[current]

        if current in expanded:
            continue
        if depth >= max_depth:
            result.stop_reasons.append(f"depth_limit:{current}")
            continue
        if result.api_calls >= max_api_calls:
            result.stop_reasons.append("api_call_budget")
            break

        expanded.add(current)
        result.expanded_addresses.append(current)
        result.api_calls += 1

        events = list(fetch_transfers(current) or [])
        events.sort(key=_event_order)

        for raw_event in events:
            sender = _address(raw_event.get("from"))
            recipient = _address(raw_event.get("to"))
            if sender != current:
                continue
            if sender == recipient:
                continue

            identity = _event_identity(raw_event)
            if identity in seen_events:
                continue
            seen_events.add(identity)

            if len(result.edges) >= max_edges:
                result.stop_reasons.append("edge_budget")
                return result

            if recipient not in result.nodes:
                if len(result.nodes) >= max_nodes:
                    result.stop_reasons.append("node_budget")
                    return result
                result.nodes.add(recipient)
                result.node_depths[recipient] = depth + 1
                if depth + 1 < max_depth:
                    queue.append(recipient)

            event = dict(raw_event)
            event["from"] = sender
            event["to"] = recipient
            event["depth"] = depth + 1
            result.edges.append(event)

    return result
