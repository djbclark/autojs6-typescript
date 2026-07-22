# Broken example 4 — Java/Kotlin objects aren't JS strings

## Symptom

```
TypeError: Cannot find function indexOf.
```

## What's actually broken

Some AutoJs6 (and Rhino-hosted app generally) APIs return a Java/Kotlin
object whose contract is "call `toString()` to get the string you want" —
not a genuine JS string. Confirmed case: `Engine.getSource()`, used e.g. to
find/dedupe running engines by script path, returns AutoJs6's own
`ScriptSource` (`abstract class ScriptSource(...)`, with
`val fullPath: String get() = toString()`), not a raw string — even though
community `.d.ts` files (reasonably) type it `string | null`.

This example reproduces the identical mechanism with `java.io.File` instead
(same shape: a real object with a meaningful `toString()`, not a JS string),
so it doesn't need AutoJs6's own runtime to demonstrate:

```ts
const f = new java.io.File("/sdcard/stayturgid/autojs6/main.js");
f.indexOf("main"); // TypeError: Cannot find function indexOf.
```

## The fix

Wrap with `String(...)` before calling any `String.prototype` method:

```ts
String(f).indexOf("main"); // 27
```

`String(...)` calls the object's `toString()` and gives you a genuine JS
string — this is not decorative, it's the actual fix. See
`examples/clean/lib/greeter.ts`'s `normalizeName()` for the same pattern.

No compiler flag or lint rule catches this generically — a `.d.ts` typed
`string` will always type-check fine against the real Java-backed value;
TypeScript has no way to know the runtime shape differs from the declared
type. If you add a new AutoJs6 (or any Rhino-hosted app's) API call whose
type is `string` but which you suspect might be Java-backed, verify with
`tools/rhino_check.py` or on-device before trusting `.indexOf()`/`.trim()`/
etc. to work on it directly.

## Reproducing locally

```
just check-clean <jar>   # passes — the clean example avoids this
just find-errors <jar>   # includes this example's TypeError, unfixed
```
