"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tag = void 0;
// Identical pattern to lib/a.ts, same local binding name `log` — this is
// the second file to load, so it's the one whose declaration Rhino reports
// as the "redeclaration."
const log = require("./log.js");
exports.tag = "b:" + typeof log.append;
