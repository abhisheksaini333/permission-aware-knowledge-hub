import test from 'node:test';import assert from 'node:assert/strict';import {apiRequest,messageFor} from '../src/http.mjs';
test('tokens cannot be sent to arbitrary destinations',async()=>{await assert.rejects(apiRequest('https://evil/api','token'),/Invalid/);await assert.rejects(apiRequest('//evil/api','token'),/Invalid/)});
test('validation responses become plain readable text',()=>{assert.equal(messageFor({detail:[{msg:'Required'},{msg:'Too long'}]}),'Required; Too long');assert.equal(messageFor({detail:'Sign in'}),'Sign in')});
