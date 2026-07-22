"use strict";
function getPathLikeObject() {
    // A java.io.File — same runtime shape as AutoJs6's ScriptSource returned
    // by Engine.getSource(): a real object with a meaningful toString(), not
    // a JS string. TypeScript still thinks this is `string`.
    return new java.io.File("/sdcard/stayturgid/autojs6/main.js");
}
const source = getPathLikeObject();
toast("path contains 'main': " + (source.indexOf("main") >= 0));
