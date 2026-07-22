// Gotcha #1: alias unique to this file, not the generic `log`.
import greeterLog = require("./log.js");

export interface Person {
  name: string;
}

export function greetAll(people: Person[]): string[] {
  const out: string[] = [];
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
export function normalizeName(rawName: unknown): string {
  return String(rawName).trim();
}
