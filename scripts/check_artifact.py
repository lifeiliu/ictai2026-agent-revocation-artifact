"""Dependency-free consistency checks for the anonymous artifact."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    with (ROOT / path).open() as handle:
        return json.load(handle)


def expect(name: str, actual, expected) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def expect_close(name: str, actual: float, expected: float, tol: float = 0.01) -> None:
    if abs(actual - expected) > tol:
        raise AssertionError(f"{name}: expected {expected}, got {actual}")


def expect_file(path: str) -> None:
    if not (ROOT / path).exists():
        raise AssertionError(f"missing required artifact file: {path}")


def main() -> None:
    expect_file("requirements-framework.txt")
    expect_file("experiments/e19_crewai_executable_demo/requirements.txt")

    e4 = load("experiments/e4_ba_scale/e4_results.json")
    expect_close("E4 BA min mean collateral", e4["headline"]["tree_overrev_mean_min_nodes"], 5.87)
    expect_close("E4 BA max mean collateral", e4["headline"]["tree_overrev_mean_max_nodes"], 79.67)
    expect_close("E4 tree failure minimum", e4["headline"]["tree_prev_pct_min"], 100.0)

    e16 = load("experiments/e16_framework_trace_replay/e16_results.json")
    expect("E16 traces", e16["collection"]["trace_units"], 500)
    expect("E16 raw events", e16["collection"]["raw_events"], 10500)
    expect("E16 signed decisions", e16["normalization"]["signed_delegation_events"], 2000)
    expect("E16 valid signed decisions", e16["normalization"]["valid_signed_delegation_events"], 2000)
    expect("E16 proof checks", e16["outcomes"]["proof_verified"], {"passed": 500, "total": 500})
    expect("E16 unauthorized checks", e16["outcomes"]["unauthorized_rejected"], {"passed": 500, "total": 500})
    expect("E16 omission checks", e16["outcomes"]["omission_rejected"], {"passed": 260, "total": 260})
    expect(
        "E16 AP conformance",
        e16["outcomes"]["single_edge_conformance"],
        {"cases": 320, "semantic_survivors": 320, "tree_wrongly_revoked": 320},
    )

    e16b = load("experiments/e16_framework_trace_replay/e16_baseline_expressiveness.json")
    expect("E16 baseline cases", e16b["all_edge_revocation_cases"], 1960)
    expect("E16 baseline AP cases", e16b["alternate_parent_cases"], 320)
    expect("E16 cross-domain target cases", e16b["cross_domain_target_cases"]["cases"], 880)
    expect("E16 scoped under cases", e16b["cross_domain_target_cases"]["scoped_under_cases"], 880)

    aggregate = {
        "trace_units": 0,
        "signed_delegation_events": 0,
        "valid_signed_delegation_events": 0,
        "alternate_parent_cases": 0,
        "alternate_parent_preserved_by_edge_target": 0,
        "alternate_parent_wrongly_revoked_by_tree": 0,
        "cross_domain_target_cases": 0,
        "cross_domain_under_revoked_by_scoped": 0,
    }
    for path in [
        "experiments/e17_a2a_protocol_demo/e17_results.json",
        "experiments/e18_cross_framework_agent_demo/e18_results.json",
        "experiments/e19_crewai_executable_demo/e19_results.json",
    ]:
        row = load(path)
        for key in aggregate:
            aggregate[key] += row.get(key, 0)
    expect("E17-E19 aggregate", aggregate, {
        "trace_units": 9,
        "signed_delegation_events": 53,
        "valid_signed_delegation_events": 53,
        "alternate_parent_cases": 8,
        "alternate_parent_preserved_by_edge_target": 8,
        "alternate_parent_wrongly_revoked_by_tree": 8,
        "cross_domain_target_cases": 19,
        "cross_domain_under_revoked_by_scoped": 19,
    })

    e6 = load("results/e6_semantic_stress.json")["batch_random"]
    expect("E6 graphs", e6["graphs"], 200)
    expect("E6 sampled sets", e6["sampled_sets"], 39991)
    expect_close("E6 failure percent", e6["mean_graph_failure_pct"], 21.25)
    expect_close("E6 mean missed", e6["mean_graph_missed_nodes"], 0.24)
    expect("E6 max missed", e6["max_missed_nodes"], 5)

    e8 = load("results/e8_protocol_results.json")
    expect("E8 attack total", sum(row["generated"] for row in e8["attack_matrix"].values()), 1100)
    expect("E8 attack rejected", sum(row["rejected"] for row in e8["attack_matrix"].values()), 1100)
    scaling = {row["nodes"]: row for row in e8["scaling"]}
    expect_close("E8 200-node target ms", scaling[200]["target_ms"]["median"], 0.17)
    expect_close("E8 2000-node target ms", scaling[2000]["target_ms"]["median"], 2.15)
    expect_close("E8 200-node wire ratio", 100 * scaling[200]["wire_ratio"]["median"], 64.7, tol=0.05)
    expect_close("E8 2000-node wire ratio", 100 * scaling[2000]["wire_ratio"]["median"], 69.0, tol=0.05)

    e11 = load("experiments/e11_oss_corpus/e11_results.json")
    e11_all = e11["all_extracted"]
    e11_acyclic = e11["acyclic_analysis"]
    expect("E11 extracted graphs", e11_all["graphs"], 47)
    expect("E11 extracted nodes", e11_all["nodes"], 382)
    expect("E11 extracted edges", e11_all["edges"], 384)
    expect("E11 extracted graphs with multi-parent", e11_all["graphs_with_mp"], 31)
    expect("E11 excluded cyclic graphs", e11["excluded_cyclic_graphs"], 29)
    expect("E11 acyclic graphs", e11_acyclic["graphs"], 18)
    expect("E11 acyclic nodes", e11_acyclic["nodes"], 123)
    expect("E11 acyclic edges", e11_acyclic["edges"], 102)
    expect("E11 acyclic graphs with multi-parent", e11_acyclic["graphs_with_mp"], 8)
    expect_close("E11 acyclic tree deviation", e11_acyclic["tree_over_fail_pct"], 54.9, tol=0.05)
    expect("E11 acyclic batch gaps", e11_acyclic["batch_fail_count"], 8)
    expect("E11 acyclic batch pairs", e11_acyclic["batch_pairs"], 33)

    print("artifact checks passed")


if __name__ == "__main__":
    main()
