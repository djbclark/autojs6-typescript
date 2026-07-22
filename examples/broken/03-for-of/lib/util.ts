// BROKEN ON PURPOSE — see ../README.md.
//
// This Rhino build's interpreted mode doesn't implement the for...of
// iterator protocol, despite the engine being configured for ES6
// (Context.VERSION_ES6 / languageVersion = VERSION_ES6). tsc's ES2015
// target (the floor — recent tsc versions have removed the ES5/ES3 targets
// that used to downlevel for...of to a plain indexed loop automatically)
// emits it as-is, so nothing catches this before it reaches a device:
//   EvaluatorException: syntax error
// — a parse-time error, not a runtime one, and specifically tied to
// `"use strict"` being present (which every tsc-compiled file has).
export function ensureDirs(dirs: string[]): void {
  for (const d of dirs) {
    console.log("ensure: " + d);
  }
}
