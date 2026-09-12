// Copied into each isolated installation so bare imports resolve there.
// One JSON document + a requested algorithm version in; a direct computeStructureHash
// call out, never passing through validateDocument. Isolates the hash-computation
// boundary (K1 case 7) from structural validation (adapter.mjs instead).
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import * as spec from '@agent-topology/spec';

const algorithmVersion = process.argv[2];
const raw = readFileSync(0);
const result = {
  identity: {
    version: JSON.parse(readFileSync(new URL('./node_modules/@agent-topology/spec/package.json', import.meta.url))).version,
    runtime: process.version,
    imported_path: import.meta.resolve('@agent-topology/spec'),
    executable: process.execPath,
  },
  input_sha256: createHash('sha256').update(raw).digest('hex'),
  requested_algorithm_version: algorithmVersion,
};
try {
  const document = JSON.parse(raw.toString('utf8'));
  result.structureHash = spec.computeStructureHash(document, algorithmVersion);
  result.status = 'computed';
} catch (error) {
  result.status = 'error';
  result.error = { type: error.name, message: error.message };
}
console.log(JSON.stringify(result));
process.exitCode = result.status === 'computed' ? 0 : 3;
