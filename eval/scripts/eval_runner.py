#!/usr/bin/env python3
"""Local evaluation runner for Gozar research scenarios.

The runner intentionally uses only the Python standard library plus the existing
Docker Compose stack. That keeps evaluations reproducible on a fresh checkout and
avoids pulling in benchmarking dependencies before the methodology has stabilized.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_DIR = REPO_ROOT / "eval" / "results" / "latest"
ADMIN_TOKEN = os.environ.get("GOZAR_ADMIN_TOKEN", "gozar-admin-token")
CONTROL_BASE_URL = os.environ.get("GOZAR_CONTROL_BASE_URL", "http://127.0.0.1:8080")
CLIENT_HOST = os.environ.get("GOZAR_EVAL_CLIENT_HOST", "127.0.0.1")
CLIENT_PORT = int(os.environ.get("GOZAR_EVAL_CLIENT_PORT", "7000"))
DEFAULT_REQUESTS = int(os.environ.get("GOZAR_EVAL_REQUESTS", "20"))


@dataclass
class RequestMeasurement:
    index: int
    ok: bool
    latency_ms: float
    connection_setup_ms: float
    selected_path: str | None
    response_bytes: int
    error_category: str | None = None
    timestamp_unix: float = field(default_factory=time.time)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local Gozar evaluation scenarios.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_all = subparsers.add_parser("run-all", help="Run all scenario YAML files.")
    run_all.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    run_all.add_argument("--ci-safe", action="store_true")
    run_all.add_argument("--no-start", action="store_true")

    run_scenario = subparsers.add_parser("run-scenario", help="Run one scenario YAML file.")
    run_scenario.add_argument("scenario")
    run_scenario.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    run_scenario.add_argument("--ci-safe", action="store_true")
    run_scenario.add_argument("--no-start", action="store_true")

    baseline = subparsers.add_parser("run-baseline", help="Run direct and relay baselines.")
    baseline.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    baseline.add_argument("--no-start", action="store_true")

    adaptive = subparsers.add_parser("run-adaptive", help="Run adaptive failover scenario.")
    adaptive.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    adaptive.add_argument("--ci-safe", action="store_true")
    adaptive.add_argument("--no-start", action="store_true")

    smoke = subparsers.add_parser("smoke", help="Run a CI-safe smoke evaluation.")
    smoke.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    smoke.add_argument("--no-start", action="store_true")

    clean = subparsers.add_parser("clean", help="Clear impairments and stop the local stack.")
    clean.add_argument("--keep-stack", action="store_true")

    args = parser.parse_args()

    if args.command == "clean":
        clear_impairments()
        if not args.keep_stack:
            compose(["down", "-v", "--remove-orphans"], check=False)
        return 0

    validate_commands(["docker"])

    if args.command == "run-all":
        scenarios = ordered_scenarios()
        return run_scenarios(scenarios, Path(args.results_dir), args.ci_safe, args.no_start)
    if args.command == "run-scenario":
        return run_scenarios([Path(args.scenario)], Path(args.results_dir), args.ci_safe, args.no_start)
    if args.command == "run-baseline":
        scenarios = [
            REPO_ROOT / "eval" / "scenarios" / "baseline-direct.yaml",
            REPO_ROOT / "eval" / "scenarios" / "baseline-relay.yaml",
        ]
        return run_scenarios(scenarios, Path(args.results_dir), False, args.no_start)
    if args.command == "run-adaptive":
        scenario = REPO_ROOT / "eval" / "scenarios" / "adaptive-failover.yaml"
        return run_scenarios([scenario], Path(args.results_dir), args.ci_safe, args.no_start)
    if args.command == "smoke":
        scenarios = [
            REPO_ROOT / "eval" / "scenarios" / "baseline-direct.yaml",
            REPO_ROOT / "eval" / "scenarios" / "baseline-relay.yaml",
            REPO_ROOT / "eval" / "scenarios" / "adaptive-failover.yaml",
        ]
        return run_scenarios(scenarios, Path(args.results_dir), True, args.no_start)

    parser.error(f"unknown command {args.command}")
    return 2



def ordered_scenarios() -> list[Path]:
    # Keep baselines first so every full run has clean reference values before
    # disruptive outage scenarios mutate the local Docker stack.
    scenario_dir = REPO_ROOT / "eval" / "scenarios"
    names = [
        "baseline-direct.yaml",
        "baseline-relay.yaml",
        "latency-200ms.yaml",
        "packet-loss-5pct.yaml",
        "packet-loss-15pct.yaml",
        "bandwidth-512kbps.yaml",
        "relay-blocked.yaml",
        "gateway-restart.yaml",
        "intermittent-connectivity.yaml",
        "adaptive-failover.yaml",
    ]
    return [scenario_dir / name for name in names]


def run_scenarios(
    scenario_paths: list[Path],
    results_dir: Path,
    ci_safe: bool,
    no_start: bool,
) -> int:
    results_dir.mkdir(parents=True, exist_ok=True)
    clear_impairments()

    if not no_start:
        log("building and starting local Docker Compose stack")
        compose(["up", "--build", "-d"])

    wait_for_health()
    wait_for_nodes()

    run_started = utc_now()
    scenario_results: list[dict[str, Any]] = []
    try:
        for scenario_path in scenario_paths:
            scenario = load_scenario(scenario_path)
            if ci_safe and not scenario.get("ci_safe", False):
                log(f"skipping {scenario_path.name}: requires privileged/local netem behavior")
                continue
            scenario_results.append(run_one_scenario(scenario, ci_safe))
    finally:
        clear_impairments()

    payload = {
        "generated_at": utc_now(),
        "run_started_at": run_started,
        "run_finished_at": utc_now(),
        "ci_safe": ci_safe,
        "scenario_count": len(scenario_results),
        "scenarios": scenario_results,
    }
    (results_dir / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (results_dir / "summary.md").write_text(render_summary(payload), encoding="utf-8")
    log(f"wrote {results_dir / 'results.json'}")
    log(f"wrote {results_dir / 'summary.md'}")
    return 0


def run_one_scenario(scenario: dict[str, Any], ci_safe: bool) -> dict[str, Any]:
    name = str(scenario["name"])
    log(f"starting scenario: {name}")
    clear_impairments()

    initial_path = str(scenario.get("initial_preferred_path") or scenario.get("preferred_path") or "direct")
    set_preferred_path(initial_path, f"evaluation scenario {name} initial path")
    time.sleep(float(scenario.get("settle_seconds", 3)))

    wait_for_path_selection(initial_path, float(scenario.get("path_warmup_seconds", 30)))

    start_time = time.time()
    scenario_started_at = utc_now()
    impairment_started_at: float | None = None
    first_error_at: float | None = None
    first_recovery_at: float | None = None
    switch_requested_at: float | None = None
    previous_path: str | None = initial_path
    path_switches = 0
    selected_path_over_time: list[dict[str, Any]] = [
        {
            "request_index": -1,
            "path": initial_path,
            "timestamp_unix": start_time,
        }
    ]
    errors_by_category: dict[str, int] = {}
    measurements: list[RequestMeasurement] = []

    if scenario.get("impairment_type") not in {"none", None}:
        impairment_started_at = time.time()
        apply_impairment(scenario, ci_safe)

    request_count = int(scenario.get("request_count", DEFAULT_REQUESTS))
    request_interval = float(scenario.get("request_interval_seconds", 0.25))
    fallback_path = scenario.get("fallback_path")
    adaptive = str(scenario.get("mode", "")).lower() == "adaptive"

    for index in range(request_count):
        measurement = send_eval_request(name, index)
        measurements.append(measurement)

        if measurement.selected_path and measurement.selected_path != previous_path:
            if previous_path is not None:
                path_switches += 1
            previous_path = measurement.selected_path
            selected_path_over_time.append(
                {
                    "request_index": index,
                    "path": measurement.selected_path,
                    "timestamp_unix": measurement.timestamp_unix,
                }
            )

        if not measurement.ok:
            category = measurement.error_category or "unknown"
            errors_by_category[category] = errors_by_category.get(category, 0) + 1
            first_error_at = first_error_at or time.time()
            if adaptive and fallback_path and switch_requested_at is None:
                switch_requested_at = time.time()
                set_preferred_path(str(fallback_path), f"adaptive fallback for scenario {name}")
        elif first_error_at is not None and first_recovery_at is None:
            first_recovery_at = time.time()

        time.sleep(request_interval)

    clear_impairments()
    recovery_wait_seconds = float(scenario.get("recovery_wait_seconds", 2))
    if recovery_wait_seconds > 0:
        time.sleep(recovery_wait_seconds)

    scenario_finished_at = utc_now()
    metrics = summarize_measurements(
        measurements=measurements,
        scenario_start=start_time,
        scenario_finish=time.time(),
        first_error_at=first_error_at,
        first_recovery_at=first_recovery_at,
        impairment_started_at=impairment_started_at,
        switch_requested_at=switch_requested_at,
        path_switches=path_switches,
        selected_path_over_time=selected_path_over_time,
        errors_by_category=errors_by_category,
    )

    result = {
        "name": name,
        "description": scenario.get("description", ""),
        "mode": scenario.get("mode", "static-direct"),
        "affected_service": scenario.get("affected_service", "none"),
        "affected_path": scenario.get("affected_path", "none"),
        "impairment_type": scenario.get("impairment_type", "none"),
        "expected_behavior": scenario.get("expected_behavior", ""),
        "scenario_started_at": scenario_started_at,
        "scenario_finished_at": scenario_finished_at,
        "metrics": metrics,
        "ci_safe": bool(scenario.get("ci_safe", False)),
    }
    log(f"finished scenario: {name} success_rate={metrics['request_success_rate']:.3f}")
    return result


def wait_for_path_selection(path: str, timeout_seconds: float) -> None:
    # Control updates are polled by the desktop client, so this warmup prevents
    # setup delay from being misclassified as path performance.
    deadline = time.time() + timeout_seconds
    last_seen = "none"
    while time.time() < deadline:
        measurement = send_eval_request("warmup", 0)
        if measurement.selected_path:
            last_seen = measurement.selected_path
        if measurement.ok and measurement.selected_path == path:
            log(f"client selected requested path={path}")
            return
        time.sleep(2)
    log(f"warning: path warmup timed out waiting for path={path}; last_seen={last_seen}")


def summarize_measurements(
    measurements: list[RequestMeasurement],
    scenario_start: float,
    scenario_finish: float,
    first_error_at: float | None,
    first_recovery_at: float | None,
    impairment_started_at: float | None,
    switch_requested_at: float | None,
    path_switches: int,
    selected_path_over_time: list[dict[str, Any]],
    errors_by_category: dict[str, int],
) -> dict[str, Any]:
    successes = [item for item in measurements if item.ok]
    latencies = [item.latency_ms for item in successes]
    setup_times = [item.connection_setup_ms for item in measurements]
    response_bytes = sum(item.response_bytes for item in successes)
    elapsed = max(scenario_finish - scenario_start, 0.001)
    first_success = next((item for item in measurements if item.ok), None)

    return {
        "connection_setup_time_ms": round(median(setup_times), 3),
        "time_to_first_success_ms": round((first_success.timestamp_unix - scenario_start) * 1000, 3)
        if first_success
        else None,
        "request_success_rate": round(len(successes) / max(len(measurements), 1), 4),
        "requests_total": len(measurements),
        "requests_successful": len(successes),
        "median_latency_ms": round(median(latencies), 3) if latencies else None,
        "p95_latency_ms": round(percentile(latencies, 95), 3) if latencies else None,
        "throughput_estimate_bytes_per_second": round(response_bytes / elapsed, 3),
        "failover_time_ms": round((first_recovery_at - switch_requested_at) * 1000, 3)
        if first_recovery_at and switch_requested_at
        else None,
        "recovery_time_ms": round((first_recovery_at - first_error_at) * 1000, 3)
        if first_recovery_at and first_error_at
        else None,
        "disruption_detection_time_ms": round((first_error_at - impairment_started_at) * 1000, 3)
        if first_error_at and impairment_started_at
        else None,
        "number_of_path_switches": path_switches,
        "selected_path_over_time": selected_path_over_time,
        "error_counts_by_category": errors_by_category,
        "scenario_start_timestamp_unix": scenario_start,
        "scenario_end_timestamp_unix": scenario_finish,
    }


def send_eval_request(scenario_name: str, index: int) -> RequestMeasurement:
    message = f"eval:{scenario_name}:{index}:{time.time_ns()}"
    setup_start = time.perf_counter()
    try:
        sock = socket.create_connection((CLIENT_HOST, CLIENT_PORT), timeout=4)
        setup_ms = (time.perf_counter() - setup_start) * 1000
        request_start = time.perf_counter()
        sock.settimeout(5)
        sock.sendall((message + "\n").encode("utf-8"))
        response = sock.makefile("rb").readline().decode("utf-8", errors="replace").strip()
        latency_ms = (time.perf_counter() - request_start) * 1000
        sock.close()
        selected_path = parse_selected_path(response)
        ok = "payload=" in response and "error=" not in response
        return RequestMeasurement(
            index=index,
            ok=ok,
            latency_ms=latency_ms,
            connection_setup_ms=setup_ms,
            selected_path=selected_path,
            response_bytes=len(response.encode("utf-8")),
            error_category=None if ok else categorize_error(response),
        )
    except (OSError, TimeoutError) as error:
        return RequestMeasurement(
            index=index,
            ok=False,
            latency_ms=0.0,
            connection_setup_ms=(time.perf_counter() - setup_start) * 1000,
            selected_path=None,
            response_bytes=0,
            error_category=categorize_error(str(error)),
        )


def apply_impairment(scenario: dict[str, Any], ci_safe: bool) -> None:
    impairment = str(scenario.get("impairment_type", "none"))
    service = str(scenario.get("affected_service", "relay"))
    duration = str(scenario.get("duration_seconds", "10"))

    if ci_safe and impairment in {"latency", "jitter", "packet_loss", "bandwidth"}:
        log(f"ci-safe mode skipping privileged impairment: {impairment}")
        return

    if impairment == "latency":
        run_script("apply-netem.sh", service, "latency", str(scenario.get("latency_ms", 200)))
    elif impairment == "jitter":
        run_script(
            "apply-netem.sh",
            service,
            "jitter",
            str(scenario.get("latency_ms", 100)),
            str(scenario.get("jitter_ms", 30)),
        )
    elif impairment == "packet_loss":
        run_script("apply-netem.sh", service, "loss", str(scenario.get("packet_loss_percent", 5)))
    elif impairment == "bandwidth":
        run_script("apply-netem.sh", service, "bandwidth", str(scenario.get("bandwidth", "512kbit")))
    elif impairment == "relay_outage":
        compose(["stop", "relay"])
    elif impairment == "gateway_outage":
        compose(["restart", "gateway"])
    elif impairment == "path_block":
        compose(["pause", service])
    elif impairment == "dns_failure":
        log("dns_failure is represented as an application-level failed target in this local runner")
    elif impairment == "intermittent":
        log(f"starting intermittent connectivity cycle for {service}")
        subprocess.Popen(
            [
                "bash",
                str(REPO_ROOT / "eval" / "scripts" / "intermittent-connectivity.sh"),
                service,
                duration,
                str(scenario.get("cycle_seconds", 3)),
            ],
            cwd=REPO_ROOT,
        )
    elif impairment == "none":
        return
    else:
        raise SystemExit(f"unsupported impairment_type: {impairment}")


def clear_impairments() -> None:
    for service in ("relay", "gateway", "desktop-client"):
        run_script("clear-netem.sh", service, check=False)
        compose(["unpause", service], check=False)
    compose(["start", "gateway"], check=False)
    compose(["start", "relay"], check=False)


def run_script(name: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    script = REPO_ROOT / "eval" / "scripts" / name
    command = ["bash", str(script), *args]
    return run(command, check=check)


def set_preferred_path(path: str, reason: str) -> None:
    body = json.dumps({"preferred_path": path, "switch_reason": reason}).encode("utf-8")
    request = urllib.request.Request(
        f"{CONTROL_BASE_URL}/api/v1/admin/preferred-path",
        data=body,
        headers={
            "content-type": "application/json",
            "x-gozar-admin-token": ADMIN_TOKEN,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def wait_for_health() -> None:
    deadline = time.time() + 90
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{CONTROL_BASE_URL}/healthz", timeout=3) as response:
                if response.status == 200:
                    return
        except urllib.error.URLError:
            time.sleep(2)
    raise SystemExit("control plane did not become healthy")


def wait_for_nodes() -> None:
    deadline = time.time() + 90
    required = {"desktop-client-1", "relay-1", "gateway-1"}
    while time.time() < deadline:
        try:
            request = urllib.request.Request(
                f"{CONTROL_BASE_URL}/api/v1/state",
                headers={"x-gozar-admin-token": ADMIN_TOKEN},
            )
            with urllib.request.urlopen(request, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
            nodes = {node["node_id"] for node in data.get("nodes", [])}
            if required.issubset(nodes):
                return
        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            pass
        time.sleep(2)
    raise SystemExit("control plane did not observe all expected nodes")


def compose(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["docker", "compose", *args], check=check)


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    log("$ " + " ".join(command))
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=check,
    )


def validate_commands(commands: list[str]) -> None:
    missing = [command for command in commands if shutil.which(command) is None]
    if missing:
        raise SystemExit(f"missing required command(s): {', '.join(missing)}")


def load_scenario(path: Path) -> dict[str, Any]:
    if not path.is_absolute():
        path = REPO_ROOT / path
    data: dict[str, Any] = {}
    list_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and list_key:
            data.setdefault(list_key, []).append(coerce_scalar(stripped[2:].strip()))
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            list_key = key
        else:
            data[key] = coerce_scalar(value)
            list_key = None
    if "name" not in data:
        raise SystemExit(f"scenario {path} is missing name")
    return data


def coerce_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_selected_path(response: str) -> str | None:
    match = re.search(r"\bpath=([a-zA-Z0-9_-]+)", response)
    return match.group(1) if match else None


def categorize_error(message: str) -> str:
    lowered = message.lower()
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    if "connection refused" in lowered:
        return "connection_refused"
    if "name or service" in lowered or "dns" in lowered:
        return "dns"
    if "error=" in lowered:
        return "overlay_error"
    return "other"


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((pct / 100) * (len(ordered) - 1))))
    return ordered[index]


def render_summary(payload: dict[str, Any]) -> str:
    lines = [
        "# Gozar Evaluation Summary",
        "",
        f"Generated at: `{payload['generated_at']}`",
        f"CI-safe mode: `{payload['ci_safe']}`",
        "",
        "| Scenario | Mode | Impairment | Success Rate | Median Latency (ms) | P95 Latency (ms) | Path Switches |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for scenario in payload["scenarios"]:
        metrics = scenario["metrics"]
        lines.append(
            "| {name} | {mode} | {impairment} | {success:.3f} | {median} | {p95} | {switches} |".format(
                name=scenario["name"],
                mode=scenario["mode"],
                impairment=scenario["impairment_type"],
                success=metrics["request_success_rate"],
                median=metrics["median_latency_ms"],
                p95=metrics["p95_latency_ms"],
                switches=metrics["number_of_path_switches"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- Values are measured from the local Docker Compose lab stack.",
            "- `None` latency values mean no request succeeded in that scenario.",
            "- Results support comparison across scenarios; they are not production claims.",
            "",
        ]
    )
    return "\n".join(lines)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    print(f"[eval] {message}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
