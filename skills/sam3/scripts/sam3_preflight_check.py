#!/usr/bin/env python3
"""Preflight checker for SAM3 environments."""

from __future__ import annotations

import argparse
import importlib
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CheckResult:
    level: str
    name: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate key prerequisites for facebookresearch/sam3 workflows."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to a local SAM3 repo checkout (default: current directory).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 1 when any FAIL or WARN checks are present.",
    )
    return parser.parse_args()


def check_python() -> CheckResult:
    version = sys.version_info
    detail = f"{version.major}.{version.minor}.{version.micro}"
    if version >= (3, 12):
        return CheckResult("PASS", "Python version", detail)
    if version >= (3, 8):
        return CheckResult(
            "WARN",
            "Python version",
            f"{detail} detected; SAM3 docs recommend Python 3.12+.",
        )
    return CheckResult(
        "FAIL",
        "Python version",
        f"{detail} detected; upgrade to Python 3.8+ (3.12+ recommended).",
    )


def check_module(name: str) -> CheckResult:
    if importlib.util.find_spec(name) is None:
        return CheckResult("FAIL", f"Module '{name}'", "not installed")
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        return CheckResult("FAIL", f"Module '{name}'", f"import failed: {exc}")
    version = getattr(module, "__version__", "unknown")
    return CheckResult("PASS", f"Module '{name}'", f"installed (version: {version})")


def check_torch_cuda() -> CheckResult:
    if importlib.util.find_spec("torch") is None:
        return CheckResult("FAIL", "Torch CUDA", "torch is not installed")

    try:
        torch = importlib.import_module("torch")
    except Exception as exc:
        return CheckResult("FAIL", "Torch CUDA", f"torch import failed: {exc}")
    cuda_available = bool(torch.cuda.is_available())
    cuda_version = getattr(torch.version, "cuda", None) or "unknown"

    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        return CheckResult(
            "PASS",
            "Torch CUDA",
            f"CUDA available ({device_name}), torch CUDA build: {cuda_version}",
        )
    return CheckResult(
        "WARN",
        "Torch CUDA",
        f"CUDA not available; SAM3 will run much slower on CPU (torch CUDA build: {cuda_version})",
    )


def check_hf_auth() -> CheckResult:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if token:
        return CheckResult(
            "PASS",
            "Hugging Face auth",
            "token found in environment variables",
        )

    if importlib.util.find_spec("huggingface_hub") is None:
        return CheckResult(
            "WARN",
            "Hugging Face auth",
            "huggingface_hub not installed; install and run `hf auth login`",
        )

    try:
        hub = importlib.import_module("huggingface_hub")
    except Exception as exc:
        return CheckResult(
            "WARN",
            "Hugging Face auth",
            f"huggingface_hub import failed: {exc}",
        )
    get_token = getattr(hub, "get_token", None)
    if callable(get_token) and get_token():
        return CheckResult("PASS", "Hugging Face auth", "cached login token detected")

    return CheckResult(
        "WARN",
        "Hugging Face auth",
        "no token detected; request access to facebook/sam3 and run `hf auth login`",
    )


def check_repo_layout(repo_path: Path) -> CheckResult:
    markers = [
        repo_path / "pyproject.toml",
        repo_path / "sam3" / "model_builder.py",
        repo_path / "README.md",
    ]
    missing = [str(path.relative_to(repo_path)) for path in markers if not path.exists()]
    if missing:
        return CheckResult(
            "WARN",
            "SAM3 repository path",
            f"missing expected files: {', '.join(missing)}",
        )
    return CheckResult("PASS", "SAM3 repository path", str(repo_path.resolve()))


def print_report(results: List[CheckResult]) -> None:
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print("SAM3 preflight report")
    print("-" * 72)
    for item in results:
        print(f"[{item.level}] {item.name}: {item.detail}")


def should_fail(results: List[CheckResult], strict: bool) -> bool:
    failures = [r for r in results if r.level == "FAIL"]
    if failures:
        return True
    if strict:
        return any(r.level in {"FAIL", "WARN"} for r in results)
    return False


def main() -> int:
    args = parse_args()
    repo_path = Path(args.repo).expanduser()

    results = [
        check_python(),
        check_module("sam3"),
        check_module("huggingface_hub"),
        check_torch_cuda(),
        check_hf_auth(),
        check_repo_layout(repo_path),
    ]
    print_report(results)
    return 1 if should_fail(results, args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
