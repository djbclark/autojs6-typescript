#!/usr/bin/env python3
"""Run every broken example through a real Rhino build and report each
error — WITHOUT fixing anything. Demonstrates what breaks and why; see each
examples/broken/*/README.md for the actual fix.

Usage: find_errors.py <path-to-rhino.jar> <examples/broken-dir>
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rhino_check import check_file  # noqa: E402

RUNTIME_ERROR_MARKER = "uncaught javascript runtime exception"


def classify(is_syntax_error: bool, out: str) -> str:
    if is_syntax_error:
        return "SYNTAX-ERROR"
    if RUNTIME_ERROR_MARKER in out.lower():
        # Expected here: a ReferenceError for a missing AutoJs6 global (e.g.
        # `context`, `files`) means the file parsed fine and started running
        # — that's not the bug this example demonstrates. The specific
        # error each broken example is ABOUT (e.g. "exports is not
        # defined") is also a runtime exception and looks identical at this
        # level; read the indented output below to tell them apart.
        return "RUNTIME-ERROR"
    return "OK"


NOT_LOCALLY_REPRODUCIBLE = {
    "01-redeclaration": (
        "NOT reproducible this way — see its README.md for why "
        "(it depends on AutoJs6's own Kotlin-side require() wiring, not "
        "just the jar's bare CLI behavior), and how it was verified on a "
        "real device instead."
    ),
}


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print("usage: find_errors.py <path-to-rhino.jar> <examples/broken-dir>", file=sys.stderr)
        return 2

    jar = Path(args[0]).expanduser()
    broken_root = Path(args[1])
    if not jar.is_file():
        print(f"error: rhino jar not found: {jar}", file=sys.stderr)
        return 2
    if not broken_root.is_dir():
        print(f"error: not a directory: {broken_root}", file=sys.stderr)
        return 2

    for example_dir in sorted(p for p in broken_root.iterdir() if p.is_dir()):
        print(f"=== {example_dir.name} ===")
        note = NOT_LOCALLY_REPRODUCIBLE.get(example_dir.name)
        if note:
            print(f"note: {note}\n")
            continue
        js_files = sorted(example_dir.rglob("*.js"))
        if not js_files:
            print("(no compiled .js files — run 'just build' first)\n")
            continue
        for js_file in js_files:
            is_syntax_error, out = check_file(jar, js_file)
            label = classify(is_syntax_error, out)
            print(f"{label}: {js_file}")
            for line in out.splitlines():
                print(f"    {line}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
