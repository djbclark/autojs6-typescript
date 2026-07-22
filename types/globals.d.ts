// Ambient globals provided by AutoJs6's Rhino runtime, typed narrowly to
// what src/ and examples/ actually call — not a general-purpose AutoJs6 API
// surface. See docs/RHINO_GOTCHAS.md for why this project targets what it
// targets and avoids what it avoids.

declare function toast(message: string): void;
declare function sleep(ms: number): void;

interface Console {
  log(...args: unknown[]): void;
  warn(...args: unknown[]): void;
  error(...args: unknown[]): void;
}
declare const console: Console;

/**
 * Rhino's LiveConnect Java-access roots — present in any Rhino script,
 * regardless of host app. `java` is a shortcut into the `java.*` package
 * tree (e.g. `new java.io.File(...)`); `Packages` is the fully-general root
 * (`Packages.org.mozilla.javascript.Context`, etc.) for anything outside
 * `java.*`. Untyped (`any`-shaped) on purpose — this project only reaches
 * through them for a handful of specific classes, and typing the general
 * Java namespace precisely isn't practical or necessary here.
 */
// biome-ignore lint: intentionally `any`-shaped, see comment above.
declare const java: any;
// biome-ignore lint: intentionally `any`-shaped, see comment above.
declare const Packages: any;
