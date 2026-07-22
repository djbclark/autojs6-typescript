# Agent notes — autojs6-typescript

Open item status: `docs/OPTIONS.md`
Rhino/AutoJs6 gotcha catalog: `docs/RHINO_GOTCHAS.md`
Project overview + quick start: `README.md`

Before editing anything under `src/`, `examples/`, or `types/`, read
`docs/RHINO_GOTCHAS.md` — every gotcha it documents was found the hard way
(a fix deploying cleanly, passing every test, then crashing on a real
device), and the whole point of this project is to keep that from happening
to someone else.

Run `just build` after any `.ts` change, and `just lint-rhino` before
committing (no jar/device needed). `just test <path-to-rhino.jar>` for the
full suite, including the real-Rhino checks — `just find-rhino-jar` locates
a jar from a fork checkout.
