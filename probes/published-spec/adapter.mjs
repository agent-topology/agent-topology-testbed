// Copied into each isolated installation so bare imports resolve there.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import * as spec from '@agent-topology/spec';

const raw = readFileSync(0);
const result = {
  identity: {
    version: JSON.parse(readFileSync(new URL('./node_modules/@agent-topology/spec/package.json', import.meta.url))).version,
    runtime: process.version,
    imported_path: import.meta.resolve('@agent-topology/spec'),
    executable: process.execPath,
  },
  input_sha256: createHash('sha256').update(raw).digest('hex'),
};
let stage = 'parse';
try {
  const document = JSON.parse(raw.toString('utf8'));
  stage = 'validation';
  const validation = spec.validateDocument(document);
  result.validation = { accepted: validation.valid, errors: validation.errors };
  if (!validation.valid) result.status = 'rejected';
  else {
    stage = 'canonical';
    result.canonical = spec.canonicalStringify(document);
    stage = 'hash';
    result.structureHash = spec.computeStructureHash(document);
    result.status = 'accepted';
  }
} catch (error) {
  result.status = 'error';
  result.error = { stage, type: error.name, message: error.message };
}
console.log(JSON.stringify(result));
process.exitCode = result.status === 'accepted' ? 0 : result.status === 'rejected' ? 2 : 3;
