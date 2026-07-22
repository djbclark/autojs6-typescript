# Broken example 3 — `for...of` is a runtime syntax error

## Symptom

```
js: "lib/util.js", line N: syntax error
js:   for (const d of dirs) {
js: ............^
InternalError: Compilation produced N syntax errors.
```

This is a **parse-time** error, not a runtime one — it fails before any
code in the file runs, and specifically requires `"use strict"` to be
present (every tsc-compiled file has it). A `for...of` loop with no
surrounding `"use strict"` parses and runs fine on the same engine; wrapped
in a function under `"use strict"` (exactly how tsc emits every compiled
file), it doesn't parse at all.

## What's actually broken

This Rhino build's interpreted mode (`isInterpretedMode = true` in
`RhinoJavaScriptEngine`) doesn't implement the `for...of` iterator protocol,
despite the engine otherwise being configured for ES6
(`languageVersion = Context.VERSION_ES6`). tsc's `ES2015` target — the
floor; recent tsc versions (7+) have removed the `ES5`/`ES3` targets that
used to downlevel `for...of` to a plain indexed loop automatically — emits
`for...of` exactly as written, so nothing at compile time catches this.

Likely-related-but-unconfirmed: anything else that depends on the iterator
protocol (array/object destructuring from an iterable, spread into an
array, generators, `Map`/`Set` iteration). None of those are exercised by
this toolkit — treat them as suspect and verify with `tools/rhino_check.py`
before relying on them in your own code.

## The fix

Use a plain indexed loop:

```ts
export function ensureDirs(dirs: string[]): void {
  for (let i = 0; i < dirs.length; i++) {
    console.log("ensure: " + dirs[i]);
  }
}
```

`Array.prototype.forEach` also works fine (it's an ES5 method — no
iterator protocol involved), if you prefer that style:

```ts
dirs.forEach((d) => console.log("ensure: " + d));
```

See `examples/clean/lib/greeter.ts` for a working indexed-loop version of
this exact pattern.

## Reproducing locally

```
just check-clean   # passes — the clean example avoids this
just find-errors   # includes this example's syntax error, unfixed
```
