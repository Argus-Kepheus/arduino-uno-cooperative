#!/usr/bin/env python3
"""Prepare and compile the integrated Arduino Uno firmware reproducibly.

The repository keeps sketch.ino for Wokwi. Arduino sketches require the
primary .ino filename to match the sketch directory, so this tool stages the
integrated source under build/ with a specification-compliant primary filename
and a pinned Arduino CLI build profile.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_PATH = ROOT / "config" / "toolchain.json"
SOURCE_SKETCH = ROOT / "sketch.ino"
CODE_SUFFIXES = {".h", ".hpp", ".hh", ".cpp", ".c", ".S", ".tpp", ".ipp"}


def load_toolchain() -> dict:
    with TOOLCHAIN_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def render_build_profile(toolchain: dict) -> str:
    build = toolchain["build"]
    core = toolchain["arduino_avr_core"]

    if not toolchain["arduino_cli"]["pinned"]:
        raise ValueError("arduino_cli must be pinned for reproducible builds")
    if not core["pinned"]:
        raise ValueError("arduino_avr_core must be pinned for reproducible builds")

    lines = [
        "profiles:",
        f"  {build['profile_name']}:",
        f"    fqbn: {toolchain['build_target']['fqbn']}",
        "    platforms:",
        f"      - platform: {core['package']} ({core['version']})",
        "    libraries:",
    ]
    for library in toolchain["libraries"]:
        lines.append(f"      - {library['name']} ({library['version']})")
    lines.extend([
        f"default_profile: {build['profile_name']}",
        "",
    ])
    return "\n".join(lines)


def stage_integrated_sketch(toolchain: dict) -> Path:
    build = toolchain["build"]
    stage = ROOT / build["staging_directory"]
    primary_name = build["primary_sketch_name"]

    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    shutil.copy2(SOURCE_SKETCH, stage / f"{primary_name}.ino")

    for path in sorted(ROOT.iterdir()):
        if path.is_file() and path.suffix in CODE_SUFFIXES:
            shutil.copy2(path, stage / path.name)

    (stage / "sketch.yaml").write_text(
        render_build_profile(toolchain),
        encoding="utf-8",
    )
    return stage


def detect_cli_version(executable: str) -> str:
    result = subprocess.run(
        [executable, "version"],
        check=True,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + "\n" + result.stderr).strip()

    match = re.search(r"Version:\s*v?([0-9]+\.[0-9]+\.[0-9]+)", output)
    if not match:
        match = re.search(r"\bv?([0-9]+\.[0-9]+\.[0-9]+)\b", output)
    if not match:
        raise RuntimeError(f"Cannot parse Arduino CLI version from: {output}")
    return match.group(1)


def compile_firmware(toolchain: dict, executable: str) -> int:
    expected_cli = toolchain["arduino_cli"]["version"]
    actual_cli = detect_cli_version(executable)
    if actual_cli != expected_cli:
        raise RuntimeError(
            f"Arduino CLI version mismatch: expected {expected_cli}, "
            f"found {actual_cli}"
        )

    stage = stage_integrated_sketch(toolchain)
    build = toolchain["build"]
    output = ROOT / build["output_directory"]
    output.mkdir(parents=True, exist_ok=True)

    command = [
        executable,
        "compile",
        "--profile",
        build["profile_name"],
        "--warnings",
        build["warnings"],
        "--output-dir",
        str(output),
        str(stage),
    ]
    print("Running:", " ".join(command))
    return subprocess.run(command, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cli",
        default="arduino-cli",
        help="Arduino CLI executable or path (default: arduino-cli)",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Stage the valid sketch/profile but do not compile",
    )
    parser.add_argument(
        "--print-profile",
        action="store_true",
        help="Print the generated sketch.yaml profile and exit",
    )
    args = parser.parse_args()

    toolchain = load_toolchain()

    if args.print_profile:
        print(render_build_profile(toolchain), end="")
        return 0

    if args.prepare_only:
        stage = stage_integrated_sketch(toolchain)
        print(stage.relative_to(ROOT))
        return 0

    try:
        return compile_firmware(toolchain, args.cli)
    except (FileNotFoundError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"Build setup failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
