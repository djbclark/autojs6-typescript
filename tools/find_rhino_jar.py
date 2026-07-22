#!/usr/bin/env python3
"""Locate the Rhino jar an AutoJs6 fork actually bundles.

Tests need to run against the SAME engine the fork ships — not whatever
mainline Rhino happens to be installed system-wide. Mainline drifts
independently of any given fork and can silently stop reproducing that
fork's bugs (confirmed: mainline Rhino 1.9.1 no longer reproduces the
for...of bug this toolkit documents, even though the fork's own bundled
2.0.0-SNAPSHOT jar does).

Usage:
    find_rhino_jar.py <path>

<path> a .jar               -> printed as-is
<path> a directory (a clone -> searched recursively for a "*rhino*.jar" —
       of an AutoJs6 fork)     the conventional app/libs/*.jar location
                                AutoJs6 forks vendor a source-patched Rhino
                                build under.

Prints the resolved jar path on stdout, or exits 1 with a diagnostic on
stderr if none was found (most likely meaning the target fork vendors its
Rhino jar somewhere non-conventional — pass the .jar path directly instead).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _is_build_intermediate(path: Path) -> bool:
    # Gradle/Android build output can contain incidental "*rhino*.jar"
    # matches (e.g. a zipped doc asset) that are NOT the actual bundled
    # engine jar — only ever search real source-tree locations.
    return "build" in path.parts


def find_rhino_jar(target: Path) -> Path:
    if target.is_file():
        if target.suffix == ".jar":
            return target
        raise ValueError(f"{target} is a file but not a .jar")

    if not target.is_dir():
        raise ValueError(f"{target} is neither a .jar file nor a directory")

    candidates = [p for p in target.rglob("*.jar") if "rhino" in p.name.lower() and not _is_build_intermediate(p)]
    if not candidates:
        raise FileNotFoundError(
            f"no *rhino*.jar found under {target} (outside build/ output)\n"
            "       AutoJs6 forks conventionally vendor it under app/libs/ — if\n"
            "       this fork puts it somewhere else, pass the .jar path directly."
        )

    # Prefer a conventional libs/ location if more than one candidate exists.
    in_libs = [p for p in candidates if "libs" in p.parts]
    return sorted(in_libs or candidates)[0]


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: find_rhino_jar.py <path-to-fork-checkout-or-jar>", file=sys.stderr)
        return 2

    try:
        jar = find_rhino_jar(Path(args[0]).expanduser())
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(jar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
