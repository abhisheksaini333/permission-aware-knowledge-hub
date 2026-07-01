import test from "node:test";
import assert from "node:assert/strict";
import {validateCallback} from "../src/auth.mjs";
test("callback requires a finite unexpired bounded state lifetime", () => {
  for(const expires of [undefined, NaN, Infinity, 100, 400101])
    assert.throws(()=>validateCallback({state:"a",expires},{state:"a",code:"b"},100));
  assert.equal(validateCallback({state:"a",expires:1000},{state:"a",code:"b"},100),"b");
});
