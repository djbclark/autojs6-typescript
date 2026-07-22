# Broken example 1 — redeclaration across the require graph

## Symptom

```
org.mozilla.javascript.EcmaError: TypeError: redeclaration of var log. (file:///android_asset/modules/jvm-npm.js#67)
```

Two files anywhere in the require graph reachable from your entry script —
here, `lib/a.ts` and `lib/b.ts`, neither of which is the entry script itself —
each declare a top-level binding with the same name (`log`) for the same
dependency. The moment both load in the same run, the whole script crashes.

## What's actually broken

AutoJs6's `jvm-npm.js` require() shim does not give each required file its
own isolated top-level scope the way Node's module system does. This is
independent of `const`/`let`/`var`, independent of which file is the entry
script, and 100% reproducible on a real device — confirmed during
[stayturgid#34](https://github.com/djbclark/stayturgid/issues/34), where
nearly every module in a real multi-file project used the same local names
for `log`, `config`, `notify`, `termux`, `comonitor`, `repair` — hitting
**every** one of them, not just `log`.

## The fix

Give every file's local binding a name unique across the **whole** require
graph, not just among its direct siblings:

```ts
// lib/a.ts
import aLog = require("./log.js");
export const tag = "a:" + typeof aLog.append;

// lib/b.ts
import bLog = require("./log.js");
export const tag = "b:" + typeof bLog.append;
```

`just lint-rhino` (`tools/check_require_bindings.py`) catches this
**statically**, no jar or device needed — it asserts every top-level
`require()` local binding name is globally unique across your compiled
output. Run it against this very example and see for yourself:

```
python3 tools/check_require_bindings.py examples/broken/01-redeclaration
# FAIL: require() binding names must be globally unique — collisions:
#     log: examples/broken/01-redeclaration/lib/a.js, examples/broken/01-redeclaration/lib/b.js
```

This is arguably more valuable than a runtime repro: it catches the bug
_before you ever deploy_, which is exactly the gap that let this crash
reach a real device in the first place (see stayturgid#34).

## Why `just find-errors` can't demonstrate this one locally

The other three broken examples reproduce with `tools/rhino_check.py` — a
bare Rhino shell parsing/starting a single compiled file. This one doesn't,
and that's not a shortcut in the demo, it's a genuine unresolved gap:

Tracing AutoJs6's Kotlin source (`RhinoJavaScriptEngine.init()` →
`ScriptRuntime.rhinoRequireFunction`/`rhinoRequire()`) suggests `jvm-npm.js`
should ultimately delegate real file loading to Rhino's **official**
`commonjs.module.Require` (installed via `RequireBuilder` before jvm-npm.js
ever loads) — which, tested standalone, appears to isolate module scope
correctly. Two attempts to reproduce the crash without a device:

1. Running the Rhino CLI with `-require -modules <dir>`, then loading
   `jvm-npm.js` on top (copying the CLI's `require` binding onto
   `global.require` first, since jvm-npm's own `NativeRequire` fallback
   checks `this.require` as a property, not a scope binding) — **did not
   reproduce it**; both files loaded fine.
2. Manually constructing the exact same `RequireBuilder` /
   `SoftCachingModuleScriptProvider` chain `initRequireBuilder()` uses, via
   raw Java interop from a Rhino script — hit LiveConnect method-resolution
   errors (`Cannot find function install` on the `Require` instance
   `createRequire()` returned) that needed more time to untangle than this
   toolkit could spend on one example.

**If you get this reproducing outside a real device, please contribute a fix
back** — ideally by adding logging inside AutoJs6's `RhinoJavaScriptEngine`/
`ScriptRuntime` to see exactly which `require` implementation is live when
`Module._load`'s `NativeRequire.require(file)` call fires for a real
multi-file project, and whether `AssetAndUrlModuleSourceProvider`
(Android/asset-backed, what AutoJs6 actually uses) behaves differently from
a plain `UrlModuleSourceProvider` (what a standalone repro is stuck using)
in a way that breaks per-module scope isolation.

## Reproducing on a real device

Push this directory to `/sdcard/repro-01/` and run `main.js` from AutoJs6.
You'll see the exact `redeclaration of var log` error above (as a toast, and
in AutoJs6's own script log) within about 0.2 seconds of launch.
