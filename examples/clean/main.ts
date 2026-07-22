/**
 * Clean reference example — entry script.
 *
 * Gotcha #2 (see ../../docs/RHINO_GOTCHAS.md): the entry script AutoJs6
 * executes directly is never require()'d by anything, so it has no real
 * `exports`/`module` object — but tsc stamps `Object.defineProperty(exports,
 * "__esModule", ...)` onto ANY file using `import x = require(...)` syntax,
 * regardless of whether the file has real exports. Using plain `require()`
 * calls here instead (no import/export syntax anywhere in this file) makes
 * tsc compile it as a script, not a module, so it never gets that stamp.
 *
 * In a real deployed project, runtime-guard.ts ships alongside your own
 * lib/*.ts (AutoJs6 needs one project directory with everything under it) —
 * here it's required by relative path straight from src/ for the demo.
 */
declare function require(id: string): any;

const greeter: typeof import("./lib/greeter.js") = require("./lib/greeter.js");
const runtimeGuard: typeof import("../../src/runtime-guard.js") = require("../../src/runtime-guard.js");

// Get this once via tools/print_rhino_version.py against your fork's jar
// (tools/find_rhino_jar.py locates it from a source checkout).
const EXPECTED_RHINO_VERSION = "Rhino 2.0.0-SNAPSHOT";

runtimeGuard.verifyRhinoRuntime(EXPECTED_RHINO_VERSION);

const lines = greeter.greetAll([{ name: greeter.normalizeName(" Ada ") }, { name: "Grace" }]);
lines.forEach((line) => toast(line));
