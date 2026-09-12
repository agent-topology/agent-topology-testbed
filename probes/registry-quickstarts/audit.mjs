import assert from "node:assert/strict";
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve, sep } from "node:path";
import { canonicalStringify, computeStructureHash, validateDocument } from "@agent-topology/spec";

const root = realpathSync("node_modules") + sep;
const imports = {};
const versions = {};
for (const name of ["@agent-topology/spec", "@agent-topology/langgraph", "@langchain/langgraph"]) {
  const path = realpathSync(fileURLToPath(import.meta.resolve(name)));
  assert.ok(path.startsWith(root), "import escaped isolated node_modules");
  imports[name] = path;
  versions[name] = JSON.parse(readFileSync(resolve("node_modules", name, "package.json"))).version;
}
assert.equal(versions["@agent-topology/spec"], "0.1.0-beta.2");
assert.equal(versions["@agent-topology/langgraph"], "0.1.0-beta.2");
assert.equal(versions["@langchain/langgraph"], "1.4.14");
const checks = process.argv.slice(2).map((file) => {
  const raw = readFileSync(file, "utf8");
  const doc = JSON.parse(raw);
  assert.equal(validateDocument(doc).valid, true);
  assert.deepEqual(computeStructureHash(doc), doc.structureHash);
  assert.equal(canonicalStringify(doc) + "\n", raw);
  return {file: file.split("/").at(-1), valid: true, hash: doc.structureHash, canonical: true};
});
console.log(JSON.stringify({runtime: process.version, mode: "ESM audit; examples .mjs and .cjs with dynamic import", imports, versions, checks}, null, 2));
