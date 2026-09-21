"""Behavior scorecard cho quant harness — output JSON versioned.
Y tuong tu harness-by-victoria evaluate-harness.sh; viet bang Python stdlib (khong can jq).
Chay: PYTHONPATH=. python scripts/evaluate-quant-harness.py [--seed 42]
Exit 0 neu moi case blocking pass/skip; exit 1 neu co blocking fail.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

VERSION = "quant-scorecard-v1"


def sh(cmd: list[str], env_extra: dict | None = None) -> tuple[int, str]:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd(), env=env)
    tail = (r.stdout + r.stderr)[-1500:]
    return r.returncode, tail


def _run_ok(cmd: list[str], env_extra: dict | None = None, needle: str | None = None) -> tuple[bool, str]:
    rc, out = sh(cmd, env_extra)
    ok = rc == 0 and (needle in out if needle else True)
    return ok, ("ok" if ok else out[-500:])


def case(id_: str, dim: str, cmd: str, blocking: bool, fn) -> dict:
    try:
        ok, proof = fn()
        status = "passed" if ok else "failed"
    except Exception as e:  # noqa: BLE001 — scorecard khong duoc crash
        ok, proof, status = False, f"exception: {e}", "failed"
    effective = status
    if status == "failed" and not blocking:
        effective = "failed-nonblocking"
    return {"id": id_, "dimension": dim, "command": cmd, "blocking": blocking,
            "status": effective, "proof": [proof],
            "next_action": "No action required." if ok else f"Run `{cmd}` to inspect."}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    env = {"PYTHONPATH": ".", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}

    def has_files(files: list[str]):
        missing = [f for f in files if not Path(f).exists()]
        return (not missing, "all present" if not missing else f"missing: {missing}")

    cases = [
        case("authority-entry", "authority", "ls AGENTS.md ARCHITECTURE.md", True,
             lambda: has_files(["AGENTS.md", "ARCHITECTURE.md"])),
        case("docs-map", "authority", "ls docs/", True,
             lambda: has_files(["docs/design-docs/index.md", "docs/product-specs/index.md",
                                "docs/exec-plans/tech-debt-tracker.md", "docs/decisions/README.md"])),
        case("linters", "validation", "python linters/run_all.py", True,
             lambda: _run_ok([sys.executable, "linters/run_all.py"])),
        case("tests", "validation", "pytest tests/ evals/", True,
             lambda: _run_ok([sys.executable, "-m", "pytest", "tests/", "evals/",
                              "-q", "-p", "no:cacheprovider"], env)),
        case("rust-control-plane", "validation",
             "cargo test --manifest-path crates/harness-cli/Cargo.toml", True,
             lambda: _run_ok(["cargo", "test", "--manifest-path", "crates/harness-cli/Cargo.toml"])),
        case("gate", "evaluation", f"scripts/run-eval.py --seed {a.seed}", True,
             lambda: _run_ok([sys.executable, "scripts/run-eval.py", "--seed", str(a.seed)],
                             env, needle='"verdict": "PASS"')),
        case("rust-conformance", "evaluation", "pytest tests/test_rust_core.py", False,
             lambda: _run_ok([sys.executable, "-m", "pytest", "tests/test_rust_core.py",
                              "-q", "-p", "no:cacheprovider"], env)),
        case("evidence", "evidence", "ls runs/<id>/manifest.json", False,
             lambda: has_files([f"runs/{os.environ.get('QUANT_RUN_ID', 'local')}/manifest.json"])),
        case("docs-fresh", "docs", "python scripts/doc-garden.py --scan", False,
             lambda: _run_ok([sys.executable, "scripts/doc-garden.py", "--scan"])),
    ]
    blocking_failed = [c for c in cases if c["blocking"] and c["status"] == "failed"]
    report = {"version": VERSION, "seed": a.seed,
              "overall": "PASS" if not blocking_failed else "FAIL", "cases": cases}
    print(json.dumps(report, indent=2))
    return 0 if not blocking_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
