#!/usr/bin/env python3
"""Generate libraries.txt from config/toolchain.json.

Usage:
    python tools/generate_libraries.py          # print generated content
    python tools/generate_libraries.py --write  # update libraries.txt
    python tools/generate_libraries.py --check  # fail if stale
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_PATH = ROOT / "config" / "toolchain.json"
OUTPUT_PATH = ROOT / "libraries.txt"


def load_toolchain() -> dict:
    with TOOLCHAIN_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def render_libraries(toolchain: dict) -> str:
    libraries = toolchain.get("libraries", [])
    seen: set[str] = set()
    lines: list[str] = []

    for item in libraries:
        name = item["name"].strip()
        version = item["version"].strip()
        if not name or not version:
            raise ValueError("Library name/version must be non-empty")
        if name in seen:
            raise ValueError(f"Duplicate library in toolchain.json: {name}")
        seen.add(name)
        lines.append(f"{name}@{version}")

    return "\n".join(lines) + ("\n" if lines else "")


def render_from_repository() -> str:
    return render_libraries(load_toolchain())


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = render_from_repository()

    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Updated {OUTPUT_PATH.relative_to(ROOT)}")
        return 0

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"Missing generated file: {OUTPUT_PATH.relative_to(ROOT)}")
            return 1
        actual = OUTPUT_PATH.read_text(encoding="utf-8")
        if actual != expected:
            print(
                "Generated library list is stale. Run: "
                "python tools/generate_libraries.py --write"
            )
            return 1
        print("libraries.txt is up to date.")
        return 0

    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
