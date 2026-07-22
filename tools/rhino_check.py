#!/usr/bin/env python3
"""Run compiled .js files through a real Rhino interpreter.

Uses the exact engine an AutoJs6 fork bundles, in the exact mode it runs
scripts in (-version 200 -interpreted matches Context.VERSION_ES6 +
isInterpretedMode = true, AutoJs6's own RhinoJavaScriptEngine setup).

This is a PARSE-and-START check, not full execution: files reference
AutoJs6-only globals (files, context, shizuku, app, ...) this script does
not stub, so a "ReferenceError: X is not defined" is the ordinary, expected
outcome here — it proves the file parsed cleanly and began running. Only a
genuine parse-time "syntax error" / "Compilation produced N syntax errors"
means the file is actually incompatible with this Rhino build.

Usage:
    rhino_check.py <path-to-rhino.jar> <file.js> [file2.js ...]

Prints one line per file (OK/SYNTAX-ERROR) and the interpreter's raw output
indented under it. Exits 1 if any file hit a real syntax error.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SYNTAX_ERROR_MARKERS = ("syntax error", "compilation produced")


def check_file(jar: Path, js_file: Path) -> tuple[bool, str]:
    """Returns (is_syntax_error, combined_output)."""
    proc = subprocess.run(
        [
            "java",
            "-cp",
            str(jar),
            "org.mozilla.javascript.tools.shell.Main",
            "-version",
            "200",
            "-interpreted",
            "-f",
            str(js_file),
        ],
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    is_syntax_error = any(marker in out.lower() for marker in SYNTAX_ERROR_MARKERS)
    return is_syntax_error, out


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print("usage: rhino_check.py <path-to-rhino.jar> <file.js> [file2.js ...]", file=sys.stderr)
        return 2

    jar = Path(args[0]).expanduser()
    if not jar.is_file():
        print(f"error: rhino jar not found: {jar}", file=sys.stderr)
        return 2

    any_bad = False
    for raw_path in args[1:]:
        js_file = Path(raw_path)
        is_bad, out = check_file(jar, js_file)
        label = "SYNTAX-ERROR" if is_bad else "OK"
        print(f"{label}: {js_file}")
        for line in out.splitlines():
            print(f"    {line}")
        any_bad = any_bad or is_bad

    return 1 if any_bad else 0


if __name__ == "__main__":
    sys.exit(main())
