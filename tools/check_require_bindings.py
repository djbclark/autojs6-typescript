#!/usr/bin/env python3
"""Static regression guard for the two mechanically-detectable Rhino gotchas.

See docs/RHINO_GOTCHAS.md for the full writeup. This catches:

  1. for...of loops — Rhino's interpreted mode throws EvaluatorException at
     runtime (a parse-time error, not caught by tsc or Node-based tests).
  2. Duplicate top-level require() local binding names across a project's
     whole require graph — jvm-npm.js doesn't isolate each required file's
     top-level scope, so two files anywhere in the transitive require graph
     declaring the same local name crash with "redeclaration of var X" the
     moment both load, independent of const/let/var.

Usage:
    check_require_bindings.py <project-dir> [<project-dir> ...] [--exclude SUBSTRING ...]

Each <project-dir> is scanned recursively for *.js files. Prints one PASS/
FAIL line per check per project. Exits 1 if any check fails in any project.

--exclude SUBSTRING excludes any file whose path contains SUBSTRING —
repeatable. Useful for a directory containing standalone diagnostic/utility
scripts that are each launched on their own (never loaded together with the
project's real entry point or with each other): those can legitimately
reuse the same local binding names without ever colliding, so scanning them
for gotcha #2 (duplicate require() bindings) would be a false positive.
Gotcha #1 (for...of) has no such caveat — it's still checked everywhere.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FOR_OF_PATTERN = re.compile(r"\bfor\s*\(\s*(?:const|let|var)\s+\w+\s+of\s+")
REQUIRE_BINDING_PATTERN = re.compile(r"^(?:const|var|let)\s+(\w+)\s*=\s*require\(")
# A crude, deliberately conservative line-comment stripper: blanks a
# whole-line `//` comment, and truncates at a ` //` (space then //) inline
# comment. Doesn't handle `//` with no preceding space (rare in formatted
# output) or block comments — good enough to stop this file's own gotcha
# commentary (which mentions `for...of` and `require(...)` in prose) from
# producing false positives, without needing a real JS parser.
INLINE_COMMENT_PATTERN = re.compile(r"\s//.*$")


def strip_comment(line: str) -> str:
    if line.strip().startswith("//"):
        return ""
    return INLINE_COMMENT_PATTERN.sub("", line)


def find_js_files(root: Path, exclude: list[str]) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*.js")
        if "node_modules" not in p.parts and not any(substr in str(p) for substr in exclude)
    )


def check_for_of(js_files: list[Path]) -> list[str]:
    hits = []
    for f in js_files:
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if FOR_OF_PATTERN.search(strip_comment(line)):
                hits.append(f"{f}:{i}")
    return hits


def check_duplicate_bindings(js_files: list[Path]) -> dict[str, set[Path]]:
    by_name: dict[str, set[Path]] = {}
    for f in js_files:
        for line in f.read_text(encoding="utf-8").splitlines():
            m = REQUIRE_BINDING_PATTERN.match(strip_comment(line).strip())
            if not m:
                continue
            by_name.setdefault(m.group(1), set()).add(f)
    return {name: files for name, files in by_name.items() if len(files) > 1}


def check_project(project_dir: Path, exclude: list[str]) -> bool:
    all_js_files = find_js_files(project_dir, [])
    js_files = find_js_files(project_dir, exclude)
    excluded_count = len(all_js_files) - len(js_files)
    suffix = f", {excluded_count} excluded" if excluded_count else ""
    print(f"=== {project_dir} ({len(js_files)} compiled .js files{suffix}) ===")
    ok = True

    # for...of has no "never loaded together" exemption — check every file,
    # excluded or not.
    for_of_hits = check_for_of(all_js_files)
    if for_of_hits:
        print("FAIL: for...of found (Rhino interpreted mode can't run it):")
        for hit in for_of_hits:
            print(f"    {hit}")
        ok = False
    else:
        print("PASS: no for...of loops")

    duplicates = check_duplicate_bindings(js_files)
    if duplicates:
        print("FAIL: require() binding names must be globally unique — collisions:")
        for name, files in sorted(duplicates.items()):
            file_list = ", ".join(str(f) for f in sorted(files))
            print(f"    {name}: {file_list}")
        ok = False
    else:
        print("PASS: every require() local binding name is unique")

    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_dirs", nargs="+", metavar="project-dir")
    parser.add_argument("--exclude", action="append", default=[], metavar="SUBSTRING")
    args = parser.parse_args(argv)

    all_ok = True
    for raw_dir in args.project_dirs:
        project_dir = Path(raw_dir)
        if not project_dir.is_dir():
            print(f"error: not a directory: {project_dir}", file=sys.stderr)
            all_ok = False
            continue
        all_ok = check_project(project_dir, args.exclude) and all_ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
