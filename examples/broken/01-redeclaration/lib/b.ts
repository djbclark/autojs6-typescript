// Identical pattern to lib/a.ts, same local binding name `log` — this is
// the second file to load, so it's the one whose declaration Rhino reports
// as the "redeclaration."
import log = require("./log.js");

export const tag = "b:" + typeof log.append;
