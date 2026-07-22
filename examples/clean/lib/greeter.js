"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.greetAll = greetAll;
exports.normalizeName = normalizeName;
// Gotcha #1: alias unique to this file, not the generic `log`.
const greeterLog = require("./log.js");
function greetAll(people) {
    const out = [];
    // Gotcha #3: plain indexed loop, not `for (const p of people)` — Rhino's
    // interpreted mode throws EvaluatorException on for...of at runtime, not
    // a compile error, so nothing catches this before it reaches a device.
    for (let i = 0; i < people.length; i++) {
        const line = "Hello, " + people[i].name + "!";
        greeterLog.append(line);
        out.push(line);
    }
    return out;
}
// Gotcha #4: values returned by host/Java-interop APIs (Engine.getSource(),
// and many AutoJs6 APIs typed `string` in the .d.ts) can be Java-backed
// strings under the hood — they don't get JS String.prototype methods until
// coerced. String(...) here is not decorative; without it, .trim() would
// throw "TypeError: Cannot find function trim" for a Java-backed input,
// exactly the way it did for engine_guard.ts's Engine.getSource() call.
function normalizeName(rawName) {
    return String(rawName).trim();
}
