"use strict";
const greeter = require("./lib/greeter.js");
const runtimeGuard = require("../../src/runtime-guard.js");
// Get this once via tools/print_rhino_version.py against your fork's jar
// (tools/find_rhino_jar.py locates it from a source checkout).
const EXPECTED_RHINO_VERSION = "Rhino 2.0.0-SNAPSHOT";
runtimeGuard.verifyRhinoRuntime(EXPECTED_RHINO_VERSION);
const lines = greeter.greetAll([{ name: greeter.normalizeName(" Ada ") }, { name: "Grace" }]);
lines.forEach((line) => toast(line));
