// BROKEN ON PURPOSE — see README.md in this directory.
//
// Two files anywhere in the require graph — lib/a.ts and lib/b.ts below,
// neither of which is this entry script — each declare a top-level binding
// named `log` for the same shared dependency. On a real AutoJs6 device this
// crashes the whole script the instant the second one loads:
//   TypeError: redeclaration of var log. (jvm-npm.js#67)
//
// `just find-errors` documents this without fixing it. Unlike the other
// three broken examples, this one is NOT reproducible via
// tools/rhino_check.py (a bare Rhino shell) — see README.md for why, and
// what a real device run actually shows.
declare function require(id: string): any;

const a: typeof import("./lib/a.js") = require("./lib/a.js");
const b: typeof import("./lib/b.js") = require("./lib/b.js");

toast("repro ok: " + a.tag + " " + b.tag);
