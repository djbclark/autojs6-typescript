declare function require(id: string): any;

const util: typeof import("./lib/util.js") = require("./lib/util.js");

util.ensureDirs(["state", "logs", "run", "tmp"]);
