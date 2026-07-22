/**
 * Standard helper: include this alongside your own code in every AutoJs6
 * TypeScript project and call verifyRhinoRuntime() once, early in your entry
 * script (before anything that depends on the gotchas in docs/RHINO_GOTCHAS.md
 * being absent). It compares the Rhino build actually running your script
 * against the one you last verified your code against, and complains loudly
 * if they differ — a silent app update (Obtainium, Play Store, F-Droid) can
 * ship a rebuilt fork with a different Rhino jar underneath, and the gotchas
 * this toolkit works around are Rhino-build-specific: a fork's fix for one
 * bug can reintroduce (or resolve) another between builds.
 *
 * Get `expected` once via tools/print_rhino_version.py against the fork's
 * jar (tools/find_rhino_jar.py locates it from a source checkout), and
 * hardcode the result in your own entry script — see examples/clean/main.ts.
 *
 * Uses Rhino's own Context#getImplementationVersion() via raw Java interop
 * (`Packages.org.mozilla.javascript.Context`), NOT an AutoJs6-specific API —
 * this works in any app that bundles Rhino, not just AutoJs6.
 */

function readRhinoVersion(): string {
  try {
    const RhinoContext = Packages.org.mozilla.javascript.Context;
    const cx = RhinoContext.getCurrentContext() || RhinoContext.enter();
    return String(cx.getImplementationVersion());
  } catch (e) {
    return "unavailable (" + e + ")";
  }
}

export interface RhinoVersionMismatch {
  expected: string;
  actual: string;
}

/**
 * Returns true when the running Rhino build matches `expected`. On a
 * mismatch: calls `onMismatch` if given, otherwise falls back to
 * console.warn + toast (either may be absent depending on host — both calls
 * are individually best-effort).
 */
export function verifyRhinoRuntime(expected: string, onMismatch?: (info: RhinoVersionMismatch) => void): boolean {
  const actual = readRhinoVersion();
  if (actual === expected) return true;

  const info: RhinoVersionMismatch = { expected, actual };
  if (onMismatch) {
    onMismatch(info);
    return false;
  }

  const msg =
    "Rhino runtime mismatch: expected " +
    JSON.stringify(expected) +
    ", got " +
    JSON.stringify(actual) +
    ". This fork's Rhino build has changed since these TypeScript gotchas/" +
    "fixes were last verified — re-run this toolkit's checks against the " +
    "new build before trusting them.";
  try {
    if (typeof console !== "undefined" && console.warn) console.warn(msg);
  } catch {
    /* best effort */
  }
  try {
    if (typeof toast === "function") toast(msg);
  } catch {
    /* best effort */
  }
  return false;
}
