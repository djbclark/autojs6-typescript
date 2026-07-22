# Rhino JS-engine gotchas

`device/autojs6`-style projects compile TypeScript to JavaScript that runs
on AutoJs6's bundled Rhino engine (`RhinoJavaScriptEngine`,
`isInterpretedMode = true`), **not** on Node/V8/QuickJS. tsc and ordinary
Node-based unit tests both happily accept code that Rhino cannot actually
run — these bugs are invisible until the compiled output executes on a real
device.

All four gotchas below were discovered in one debugging session
(2026-07-22, [stayturgid#34](https://github.com/djbclark/stayturgid/issues/34)):
a fix deployed cleanly, passed every test, and then the target device's
AutoJs6 watchdog crashed on every single launch attempt with no working
engine — until all four were found and fixed, one at a time, against a
live device (force-stop → cold start → read logcat → fix → redeploy).

`examples/broken/01..04/` in this repo are the exact, unfixed reproductions
of each. `tools/check_require_bindings.py` and `tools/rhino_check.py` catch
what's mechanically catchable (see below); the rest need code review.

## 1. Two files requiring the same module under the same local name crash — anywhere in the require graph

**Symptom:**

```
TypeError: redeclaration of var log. (file:///android_asset/modules/jvm-npm.js#67)
```

**Mechanism:** confirmed root cause — AutoJs6's `jvm-npm.js` (a fork of
[nodyn/jvm-npm](https://github.com/nodyn/jvm-npm)) rewrote `Module._load` to
drop upstream's `new Function(exports, module, require, __filename,
__dirname, body)` per-module isolation wrapper (genuine, JS-spec-guaranteed
function-local scoping — two modules' top-level `const`s can never collide,
full stop) in favor of delegating to `NativeRequire.require(file)` — AutoJs6's
own installed `org.mozilla.javascript.commonjs.module.Require`, a
Scriptable-scope/prototype-chain-based mechanism, not function-local scoping.
Checked upstream's own source directly: `NativeRequire.require` there is used
in exactly one place — a not-found/native-module fallback inside `Require()`,
never as a substitute for `Module._load`'s isolation. This is entirely
AutoJs6's own change, not an upstream jvm-npm limitation or design ambiguity.
Reported: [SuperMonster003/AutoJs6#564](https://github.com/SuperMonster003/AutoJs6/issues/564).

If two files — anywhere in the transitive require graph reachable from your
entry script, not just direct siblings — each declare a top-level binding
with the same name for a shared dependency (`const log = require("./log.js")`
in two different files, say), the _second_ one to load crashes the whole
script. This reproduces with a minimal repro independent of any specific
project's code (`examples/broken/01-redeclaration/`), is independent of
`const`/`let`/`var`, and is independent of which file is the entry script.

Because nearly any real project logs from more than one file, and shares
config/notify/whatever-else across modules, this tends to hit **every**
commonly-shared module name, not just one.

**Fix:** give every file's local binding a name unique across the **whole**
require graph — `guardLog`, `watchdogConfig`, `comonitorNotify`, not `log`/
`config`/`notify` everywhere. This is a workaround, not a real fix — the
actual fix (restoring `Module._load`'s Function-wrapper isolation, or
otherwise verifying the delegation path isolates `const`/`let` correctly) is
AutoJs6's to make; see the issue above.

**Caught by:** `tools/check_require_bindings.py` (`just lint-rhino`) —
statically, no jar or device needed. Asserts every top-level `require()`
local binding name is globally unique across your compiled output. This
specific gotcha is _not_ reproducible via `tools/rhino_check.py`/a bare
Rhino shell — see `examples/broken/01-redeclaration/README.md` for the
investigation into why (several plausible configurations mimicking AutoJs6's
Kotlin-side `RequireBuilder`/`ScriptRuntime` wiring didn't reproduce it
standalone, even once the root cause above was identified — some detail of
the real on-device wiring still isn't replicated by a bare CLI harness).

## 2. The entry script can't carry tsc's CommonJS `exports` stamp

**Symptom:**

```
ReferenceError: "exports" is not defined.
```

**Mechanism:** any `.ts` file containing `import`/`export` syntax
(including TypeScript's own `import x = require(...)`) makes tsc emit
`Object.defineProperty(exports, "__esModule", { value: true })` as the
file's first compiled statement, unconditionally, regardless of whether the
file has real exports. That's correct for `lib/*.ts` files — they're only
ever loaded _via_ `require()`, which gives them a real `module.exports`
object from their caller's module wrapper. Your entry script (`main.js`) is
different: AutoJs6 executes it directly
(`script.exec(context, scriptable, scriptable)`), never via `require()`, so
it has no `exports` object in scope at all.

**Fix:** use plain `const x: typeof import("./lib/foo.js") = require("./lib/foo.js")`
calls in your entry script instead of `import x = require(...)`. A file
with zero `import`/`export` syntax anywhere in it is compiled by tsc as a
plain script, not a module, and never gets the stamp. See
`examples/clean/main.ts`.

**Caught by:** nothing automated — if you reintroduce real `import`/`export`
syntax into your entry script later, you will bring this back. Review entry
script diffs by hand for that pattern.

## 3. `for...of` is a runtime syntax error, not a compile error

**Symptom:**

```
js: "lib/foo.js", line N: syntax error
js:   for (const x of xs) {
js: ............^
InternalError: Compilation produced N syntax errors.
```

**Mechanism:** this Rhino build's interpreted mode doesn't implement the
`for...of` iterator protocol, despite the engine otherwise being configured
for ES6 (`languageVersion = Context.VERSION_ES6`). This is specifically a
`"use strict"` interaction — the same loop with no surrounding
`"use strict"` parses fine on the same engine; every tsc-compiled file has
`"use strict"` as its first statement, so this always bites compiled
output. tsc's `ES2015` target — the floor; recent tsc versions (7+) have
removed the `ES5`/`ES3` targets that used to downlevel `for...of` to a
plain indexed loop automatically — emits `for...of` exactly as written, so
nothing at compile time catches it.

Likely-related-but-unconfirmed: anything else that depends on the iterator
protocol (array/object destructuring from an iterable, spread into an
array, generators, `Map`/`Set` iteration). Treat those as suspect and
verify with `tools/rhino_check.py` before relying on them.

**Fix:** plain indexed loop (`for (let i = 0; i < arr.length; i++)`) or
`Array.prototype.forEach` (an ES5 method — no iterator protocol involved,
confirmed working). See `examples/clean/lib/greeter.ts`.

**Caught by:** `tools/check_require_bindings.py` (`just lint-rhino`) via
regex on compiled output, and `tools/rhino_check.py` (`just find-errors`)
via an actual Rhino parse against a real jar.

## 4. Java/Kotlin objects aren't JS strings, even when typed `string`

**Symptom:**

```
TypeError: Cannot find function indexOf.
```

**Mechanism:** some host APIs return a Java/Kotlin object whose contract is
"call `toString()` to get the string you want" — not a genuine JS string —
even when a `.d.ts` reasonably types the return value `string`. Confirmed
case: AutoJs6's `Engine.getSource()` (used to find/dedupe running engines
by script path) returns AutoJs6's own `ScriptSource`
(`abstract class ScriptSource(...)`, with `val fullPath: String get() =
toString()`), not a raw string. `examples/broken/04-java-string-coercion/`
reproduces the identical mechanism with `java.io.File` (same shape: a real
object with a meaningful `toString()`, not a JS string) so it doesn't need
AutoJs6's own runtime to demonstrate.

**Fix:** wrap with `String(...)` before calling any `String.prototype`
method — `String(engine.getSource() || "")`. Not decorative: `String(...)`
calls the object's `toString()` and gives you a genuine JS string. See
`examples/clean/lib/greeter.ts`'s `normalizeName()`.

**Caught by:** nothing automated — a `.d.ts` typed `string` will always
type-check fine against the real Java-backed value; TypeScript has no way
to know the runtime shape differs from the declared type. If you add a new
host API call whose type is `string` but which you suspect might be
Java-backed, verify with `tools/rhino_check.py` or on-device before trusting
`.indexOf()`/`.trim()`/etc. to work on it directly.

## Rhino builds are fork-specific — verify, don't assume

Mainline Rhino (`brew install rhino`, currently 1.9.1) does **not**
reproduce gotcha #3 above — its `for...of` support has since changed. Every
AutoJs6 fork vendors its own (possibly patched, possibly a different
version entirely) Rhino build; assuming "Rhino" behaves one specific way
across forks or versions is exactly the trap this toolkit exists to avoid.
Always run `tools/rhino_check.py` against the **actual jar your target fork
bundles** (`tools/find_rhino_jar.py` locates it), not whatever Rhino
happens to be installed system-wide. `src/runtime-guard.ts` extends this
principle to the running device itself: a fork rebuild can ship a different
engine without changing your dev-time assumptions at all.
