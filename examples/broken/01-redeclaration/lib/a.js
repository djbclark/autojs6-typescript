"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tag = void 0;
// The bug: this file's own `log` binding is fine in isolation — it only
// collides once main.ts also require()s lib/b.ts, which independently
// declares its own top-level `log` for the same log.js dependency.
const log = require("./log.js");
exports.tag = "a:" + typeof log.append;
