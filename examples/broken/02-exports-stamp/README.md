# Broken example 2 — the `exports` stamp on an entry script

## Symptom

```
ReferenceError: "exports" is not defined.
```

Thrown on line 1 of the compiled output (`Object.defineProperty(exports, "__esModule", ...)`),
before any of your own code runs.

## What's actually broken

Any `.ts` file containing `import`/`export` syntax — including TypeScript's
own `import x = require(...)` — gets tsc's CommonJS interop stamp as its
first compiled statement, **unconditionally**, regardless of whether the
file has real exports. That's correct for `lib/*.ts` files: they're only
ever loaded _via_ `require()`, which gives them a real `module.exports`
object from their caller's module wrapper.

Your entry script is different. AutoJs6 executes it directly
(`script.exec(context, scriptable, scriptable)` in `RhinoJavaScriptEngine`),
never via `require()` — so it has no `exports` object in scope at all.

## The fix

Use plain `require()` calls in your entry script instead of
`import x = require(...)`:

```ts
declare function require(id: string): any;

const config: typeof import("./lib/config.js") = require("./lib/config.js");

toast("interval: " + config.INTERVAL_MS);
```

A file with **zero** `import`/`export` syntax anywhere in it is compiled by
tsc as a plain script, not a module — it never gets the `exports` stamp.
See `examples/clean/main.ts` for the working version of this exact pattern.

No compiler flag or lint rule catches this generically — if you reintroduce
real `import`/`export` syntax into your entry script later, you'll bring
this back. Review entry-script diffs by hand for that pattern.

## Reproducing locally

```
just check-clean   # passes — the clean example avoids this
just find-errors   # includes this example's ReferenceError, unfixed
```
