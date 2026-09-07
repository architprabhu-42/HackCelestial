"""Record the deterministic T29 impact-and-recovery benchmark."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event, calculate_impacts
from resilitrip.domain.planner import plan_recovery
from resilitrip.infrastructure.fixture_loader import load_fixture


def _memory_bytes() -> int | None:
    if os.name != "nt":
        return None
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
                    ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
                    ("total_page_file", ctypes.c_ulonglong), ("available_page_file", ctypes.c_ulonglong),
                    ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                    ("available_extended_virtual", ctypes.c_ulonglong)]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    return status.total_physical if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)) else None


def _run(fixture) -> tuple[str, str]:
    baseline = create_initial_trip(fixture)
    delayed = apply_timing_event(baseline, fixture.replay_events[0])
    impacts = calculate_impacts(baseline, delayed, fixture.catalog, fixture.replay_events[0])
    result = plan_recovery(delayed, fixture.catalog)
    payload = {"impacts": [item.model_dump(mode="json") for item in impacts], "planner": result.model_dump(mode="json")}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return result.result_status.value, digest


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    fixture = load_fixture(root)
    for _ in range(5):
        _run(fixture)
    durations_ms: list[float] = []
    statuses: list[str] = []
    hashes: list[str] = []
    for _ in range(100):
        started = perf_counter_ns()
        status, digest = _run(fixture)
        durations_ms.append((perf_counter_ns() - started) / 1_000_000)
        statuses.append(status)
        hashes.append(digest)
    ordered = sorted(durations_ms)
    report = {
        "schema_version": "resilitrip-performance-1.0",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "scenario_id": fixture.scenario.id,
        "method": "real fixture → D1 timing event → shared impact evaluator → bounded recovery planner → canonical serialization",
        "warmup_runs": 5,
        "measured_runs": 100,
        "duration_ms": {"p50": median(ordered), "p95": ordered[94], "max": max(ordered)},
        "target_p95_ms": 1000.0,
        "target_passed": ordered[94] < 1000.0,
        "result_status_counts": {"complete": statuses.count("complete"), "partial_search": statuses.count("partial_search")},
        "canonical_output_hash": hashes[0],
        "all_output_hashes_identical": len(set(hashes)) == 1,
        "runtime": {"python": sys.version, "implementation": platform.python_implementation(), "os": platform.platform(),
                    "machine": platform.machine(), "processor": platform.processor() or None, "cpu_count": os.cpu_count(),
                    "physical_memory_bytes": _memory_bytes()},
        "catalog": {"services": len(fixture.catalog.services), "transfer_templates": len(fixture.catalog.transfer_templates),
                    "max_new_fixed_legs": fixture.constraints.max_new_fixed_legs, "max_transfer_legs": fixture.constraints.max_transfer_legs,
                    "horizon_end": fixture.constraints.horizon_end.isoformat()},
    }
    output = root / "artifacts" / "performance" / "hero-benchmark.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"T29 p50={report['duration_ms']['p50']:.3f}ms p95={report['duration_ms']['p95']:.3f}ms max={report['duration_ms']['max']:.3f}ms")
    if not report["target_passed"] or not report["all_output_hashes_identical"] or report["result_status_counts"]["complete"] != 100:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
