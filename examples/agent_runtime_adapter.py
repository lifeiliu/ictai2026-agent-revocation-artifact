"""Tiny agent-runtime adapter example for the revocation contract API.

Run from the artifact root with:

    PYTHONPATH=src python examples/agent_runtime_adapter.py
"""

from __future__ import annotations

import json
from pathlib import Path

from revocation import FrameworkRevocationAdapter, load_jsonl_events


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "experiments/e19_crewai_executable_demo/traces/normalized_events.jsonl"


def main() -> None:
    events = load_jsonl_events(TRACE)
    adapter = FrameworkRevocationAdapter(
        framework="crewai",
        workflow="e19-adapter-example",
        epoch_id=str(events[0].get("epoch_id", "e19-crewai-executable-demo")),
    )
    for event in events:
        recorded = adapter.record_handoff(
            caller=str(event["caller"]),
            callee=str(event["callee"]),
            parent_domain=str(event["parent_domain"]),
            child_domain=str(event["child_domain"]),
            permission=dict(event["permission"]),
            trace_id=str(event["trace_id"]),
            source_task=str(event.get("source_task", "")),
            target_task=str(event.get("target_task", "")),
            edge_id=str(event["edge_id"]),
        )
        adapter.accept_edge(str(recorded["edge_id"]))
    revoked_edge = adapter.accepted_events[-1]["edge_id"]
    bundle = adapter.revoke_edge(str(revoked_edge), revoked_at=1.0)
    print(
        json.dumps(
            {
                "trace": str(TRACE.relative_to(ROOT)),
                "accepted_edges": len(adapter.accepted_events),
                "revoked_edge": revoked_edge,
                "target": bundle.target,
                "verified_without_graph": adapter.verify_revocation_bundle(bundle),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
