#!/usr/bin/env python3
"""Verify every .ts file has a compiled .js twin — a missing one means
`just build` wasn't run (or failed) before committing/testing.

Usage: check_build.py <dir> [<dir> ...]
"""

from __future__ import annotations

import sys
from pathlib import Path


def missing_js(root: Path) -> list[Path]:
    missing = []
    for ts_file in root.rglob("*.ts"):
        if ts_file.name.endswith(".d.ts"):
            continue
        js_file = ts_file.with_suffix(".js")
        if not js_file.is_file():
            missing.append(ts_file)
    return missing


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: check_build.py <dir> [<dir> ...]", file=sys.stderr)
        return 2

    all_missing: list[Path] = []
    for raw_dir in args:
        all_missing.extend(missing_js(Path(raw_dir)))

    if all_missing:
        print("Missing compiled .js for:", file=sys.stderr)
        for f in sorted(all_missing):
            print(f"  {f}", file=sys.stderr)
        print("Run 'just build'.", file=sys.stderr)
        return 1

    print("OK: every .ts file has a compiled .js twin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
