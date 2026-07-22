# autojs6-typescript

TypeScript for [AutoJs6](https://github.com/SuperMonster003/AutoJs6)'s bundled
Rhino JavaScript engine — a clean starter, a catalog of engine-specific
gotchas with runnable broken examples, and a verification toolkit that
targets _whatever fork you point it at_, tracking that fork's actual bundled
Rhino build even if it changes in the future.

## Why this exists

AutoJs6 scripts run on Rhino, not Node/V8/QuickJS. tsc and ordinary
Node-based tests happily accept TypeScript output that Rhino cannot
actually run — the mismatch only surfaces as a runtime crash on a real
device, often long after the code that triggers it was written and
"working" (see [docs/RHINO_GOTCHAS.md](docs/RHINO_GOTCHAS.md) for the full
incident this project grew out of: four separate, previously-undiscovered
Rhino bugs found in one debugging session, after a fix had already deployed
cleanly and passed every test).

This project exists so the next person doesn't have to rediscover all four
the hard way:

- **`examples/clean/`** — a small, working, idiomatic multi-file project
  that avoids every gotcha below.
- **`examples/broken/01..04/`** — one directory per gotcha, each with the
  _exact_ code that triggers it, unfixed, plus a README explaining the
  symptom, the mechanism, and the fix.
- **`tools/`** — locate a fork's actual bundled Rhino jar, run your compiled
  output through it, and check for the two gotchas that are mechanically
  detectable without a jar or device at all.
- **`src/runtime-guard.ts`** — a small helper you include in your own
  project that checks the Rhino build actually running your script on a
  real phone against the one you last verified it against, and complains if
  they differ (a silent app update can ship a rebuilt fork with a different
  engine underneath).

## Quick start

```
just install-deps   # node, python3, java, just — see supported platforms below
just install        # npm install (TypeScript)
just build          # compile src/ + examples/ to .js

just find-rhino-jar ~/src/YourAutoJs6Fork   # locate the fork's bundled Rhino jar
just check-clean <jar>                       # clean example parses fine
just find-errors <jar>                       # broken examples show their errors, unfixed
just lint-rhino                              # static checks, no jar/device needed
just test <jar>                              # everything above, in one command
```

## Using this for your own fork

This toolkit is fork-agnostic by design — it doesn't hardcode which Rhino
build you're targeting.

1. **Locate your fork's Rhino jar.** AutoJs6 forks conventionally vendor a
   source-patched Rhino build under `app/libs/*.jar` in their own source
   tree (this is how the reference fork used to write this toolkit does it,
   and how upstream-style forks generally do it too):

   ```
   just find-rhino-jar ~/src/YourAutoJs6Fork
   ```

   If your fork vendors it somewhere non-conventional, pass the `.jar` path
   directly to any recipe that takes one instead of a checkout directory.

   **Extracting it from an APK instead of a source checkout:** possible but
   not "easy" — Android compiles all Java/Kotlin dependencies (including a
   vendored Rhino jar) into merged `classes*.dex` files, not a
   reconstructable copy of the original jar. The realistic path is:
   `apktool d your.apk` to unpack it, then a DEX→JAR reconstruction tool
   (e.g. [dex2jar](https://github.com/pxb1988/dex2jar) or
   [enjarify](https://github.com/google/enjarify)) to get back a runnable
   jar containing `org/mozilla/javascript/**` alongside every other class in
   the app. This works in principle (Rhino itself is MPL-2.0, meant to be
   used this way) but reconstruction quality varies by tool/APK and isn't
   something this project automates or has verified end-to-end — vastly
   prefer a source checkout when one is available.

2. **Record the version marker** (optional but recommended — feeds
   `runtime-guard.ts`):

   ```
   just rhino-version <jar>
   # -> Rhino 2.0.0-SNAPSHOT
   ```

3. **In your own project**, copy `src/runtime-guard.ts` alongside your other
   `lib/*.ts` files (AutoJs6 needs one project directory with everything
   under it) and call it once at startup:

   ```ts
   import runtimeGuard = require("./lib/runtime-guard.js");
   runtimeGuard.verifyRhinoRuntime("Rhino 2.0.0-SNAPSHOT"); // your fork's version marker
   ```

4. **Run the checks against your own compiled output**, not just this
   toolkit's examples:

   ```
   python3 tools/check_require_bindings.py path/to/your/compiled/output
   python3 tools/rhino_check.py <jar> path/to/your/compiled/output/*.js
   ```

## Supported platforms

macOS, the major Linux distros (Debian/Ubuntu, Fedora, Arch, openSUSE), and
Termux (Android) — `just install-deps` detects which one you're on and
installs node, python3, a JDK, and `just` itself accordingly. See
`tools/install-deps.sh` if you'd rather install manually; it's the one
shell script in this project (OS/package-manager detection is inherently a
shell task — everything else is `just` + Python).

## Project layout

```
src/runtime-guard.ts          the standard helper — include in your own project
types/globals.d.ts            ambient Rhino/AutoJs6 globals used by src/ and examples/
examples/clean/                a working reference project
examples/broken/01-04/         one gotcha each, unfixed, with a README
tools/                        find_rhino_jar, rhino_check, print_rhino_version,
                               check_require_bindings, install-deps.sh
docs/RHINO_GOTCHAS.md         the full writeup
```

## License

MIT — see [LICENSE](LICENSE).
