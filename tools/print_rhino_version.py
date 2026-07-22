#!/usr/bin/env python3
"""Print the exact version string a Rhino jar reports at runtime.

Context#getImplementationVersion() — the same string src/runtime-guard.ts
checks the on-device engine against. Run this once against a fork's jar
(see find_rhino_jar.py) and hardcode the result as the `expected` argument
passed to verifyRhinoRuntime() in your own main.ts.

Usage: print_rhino_version.py <path-to-rhino.jar>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: print_rhino_version.py <path-to-rhino.jar>", file=sys.stderr)
        return 2

    jar = Path(args[0]).expanduser()
    if not jar.is_file():
        print(f"error: rhino jar not found: {jar}", file=sys.stderr)
        return 2

    proc = subprocess.run(
        [
            "java",
            "-cp",
            str(jar),
            "org.mozilla.javascript.tools.shell.Main",
            "-e",
            "print(Packages.org.mozilla.javascript.Context.enter().getImplementationVersion());",
        ],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
