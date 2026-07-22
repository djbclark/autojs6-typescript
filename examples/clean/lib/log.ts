// Gotcha #1 (see ../../../docs/RHINO_GOTCHAS.md): every file that requires
// this module must alias it to a name unique across the WHOLE require graph
// reachable from main.ts, not just its own direct importers. This project
// only has one such file (greeter.ts), so `greeterLog` is enough — in a
// larger project, every consumer needs its own unique alias.
export function append(line: string): string {
  const msg = new Date().toISOString() + " " + line;
  console.log(msg);
  return msg;
}
