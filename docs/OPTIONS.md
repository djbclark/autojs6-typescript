# OPTIONS — open work

> **For agents:** When the operator asks for **options** or **next steps** in
> this project, read this file, present the open items with descriptions and
> risk, do any requested work, then **replace** this list (drop completed
> items; keep IDs stable). Commit and push in the same turn.

**Risk scale:** **Low** = reversible / read-mostly · **Medium** = touches
published fork behavior or requires real device/emulator verification ·
**High** = affects correctness of the toolkit's own checks.

---

## 1 — Local (non-device) repro for gotcha #1 · Risk: **Low**

Root cause confirmed (AutoJs6's `jvm-npm.js` dropped upstream's Function-wrapper
module isolation — see `docs/RHINO_GOTCHAS.md` #1), but the actual crash still
doesn't reproduce via a bare Rhino CLI shell using the same jar. Tracking
issue: [#1](https://github.com/djbclark/autojs6-typescript/issues/1).

Not blocking — `tools/check_require_bindings.py` already catches this gotcha
class statically, and the real fix is tracked upstream at
[SuperMonster003/AutoJs6#564](https://github.com/SuperMonster003/AutoJs6/issues/564).
This item is purely about closing the toolkit's own local-verification gap.
