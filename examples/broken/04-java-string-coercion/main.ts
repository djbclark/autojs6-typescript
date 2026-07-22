// BROKEN ON PURPOSE — see README.md in this directory.
//
// AutoJs6's Engine.getSource() (used e.g. to find/dedupe running engines by
// script path) is typed `string | null` in most community .d.ts files and
// even reads that way from the Kotlin source's intent — but the actual
// runtime value is an AutoJs6-internal ScriptSource object, not a JS
// string. Its contract is "call toString() to get the path" (see
// ScriptSource.fullPath in AutoJs6's own source: `get() = toString()`).
// Calling a String.prototype method directly on it throws immediately:
//   TypeError: Cannot find function indexOf.
//
// This example reproduces the exact same shape with java.io.File instead of
// AutoJs6's own ScriptSource — same mechanism (a Java/Kotlin object whose
// toString() gives you the string you want, but which isn't itself a JS
// string), no AutoJs6 runtime required to demonstrate it.
declare function require(id: string): any;

function getPathLikeObject(): string {
  // A java.io.File — same runtime shape as AutoJs6's ScriptSource returned
  // by Engine.getSource(): a real object with a meaningful toString(), not
  // a JS string. TypeScript still thinks this is `string`.
  return new java.io.File("/sdcard/stayturgid/autojs6/main.js") as unknown as string;
}

const source = getPathLikeObject();
toast("path contains 'main': " + (source.indexOf("main") >= 0));
