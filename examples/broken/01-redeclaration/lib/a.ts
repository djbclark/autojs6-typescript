// The bug: this file's own `log` binding is fine in isolation — it only
// collides once main.ts also require()s lib/b.ts, which independently
// declares its own top-level `log` for the same log.js dependency.
import log = require("./log.js");

export const tag = "a:" + typeof log.append;
