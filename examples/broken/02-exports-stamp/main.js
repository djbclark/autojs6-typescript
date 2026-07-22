"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// BROKEN ON PURPOSE — see README.md in this directory.
//
// This entry script uses TypeScript's `import x = require(...)` syntax.
// Any file with import/export syntax anywhere in it gets tsc's CommonJS
// interop stamp — `Object.defineProperty(exports, "__esModule", ...)` — as
// its first compiled statement, unconditionally. That's correct for a file
// meant to be require()'d (it gets a real `exports` object from its
// caller's module wrapper) but wrong for an entry script: AutoJs6 executes
// main.js directly, never via require(), so there is no `exports` object in
// scope — this throws immediately:
//   ReferenceError: "exports" is not defined.
const config = require("./lib/config.js");
toast("interval: " + config.INTERVAL_MS);
