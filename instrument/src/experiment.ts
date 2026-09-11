import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { assertTopologyDocument, computeStructureHash } from "@agent-topology/spec";
import type { TopologyDocument } from "@agent-topology/spec";
import { BRANCH_EXTENSION_KEY, renderGraph, type BranchExtension } from "./render.js";
import { theme } from "./theme.js";

/**
 * Side-by-side comparison of the same document rendered from core fields only
 * and with the proposed branch extension read.
 *
 * The extension is injected here rather than produced, because the point of the
 * exercise is to see what the field buys a consumer before asking any producer
 * to emit it. The declared mode for each fixture is the one its own name states
 * the graph means.
 */

const FIXTURES = process.env.FIXTURES ?? "../repo/conformance/fixtures";
const OUT = process.env.OUT ?? "out";

const MODES: Record<string, { sourceId: string; mode: BranchExtension["mode"]; why: string }> = {
  "parallel-fanout": {
    sourceId: "fork",
    mode: "concurrent",
    why: "The fixture name states both destinations run.",
  },
  "conditional-routing": {
    sourceId: "router",
    mode: "exclusive",
    why: "The fixture name states the router picks one destination.",
  },
  "multi-source-join": {
    sourceId: "__start__",
    mode: "concurrent",
    why: "Corroborated by joins[]: both destinations converge on 'joined'.",
  },
  loop: {
    sourceId: "retry",
    mode: "unknown",
    why: "A conditional router may return several destinations, so a producer that does not inspect the routing function cannot tell whether 'retry' loops or exits. The honest third value.",
  },
};

interface Pair {
  name: string;
  mode: BranchExtension["mode"];
  why: string;
  baseline: string;
  experimental: string;
  hashUnchanged: boolean;
  stillValid: boolean;
}

function injectBranch(doc: TopologyDocument, sourceId: string, mode: BranchExtension["mode"]): TopologyDocument {
  const copy = JSON.parse(JSON.stringify(doc)) as TopologyDocument;
  const structure = copy.graphs[0].structure;
  const edgeIds = structure.edges
    .filter((edge) => edge.source === sourceId)
    .map((edge) => edge.id)
    .sort();
  const branch: BranchExtension = {
    id: `branch:${sourceId}`,
    sourceId,
    mode,
    edgeIds,
  };
  (structure as unknown as Record<string, unknown>)[BRANCH_EXTENSION_KEY] = [branch];
  return copy;
}

function main(): void {
  mkdirSync(OUT, { recursive: true });
  const pairs: Pair[] = [];

  for (const name of Object.keys(MODES).sort()) {
    const { sourceId, mode, why } = MODES[name];
    const raw: unknown = JSON.parse(readFileSync(join(FIXTURES, name, "expected.json"), "utf8"));
    assertTopologyDocument(raw);
    const doc = raw as TopologyDocument;

    const extended = injectBranch(doc, sourceId, mode);

    // Two claims to check before any of this is worth proposing:
    // the extended document is still a valid 0.1 document, and its structure
    // hash is unchanged, so no published fixture or receipt is invalidated.
    let stillValid = true;
    try {
      assertTopologyDocument(extended);
    } catch {
      stillValid = false;
    }
    const hashUnchanged =
      computeStructureHash(extended).value === computeStructureHash(doc).value &&
      computeStructureHash(doc).value === doc.structureHash.value;

    const baseline = renderGraph(doc, doc.graphs[0]);
    const experimental = renderGraph(extended, extended.graphs[0], { branchExtension: true });
    writeFileSync(join(OUT, `${name}.core.svg`), `${baseline}\n`, "utf8");
    writeFileSync(join(OUT, `${name}.branch.svg`), `${experimental}\n`, "utf8");

    pairs.push({
      name,
      mode,
      why,
      baseline,
      experimental,
      hashUnchanged,
      stillValid,
    });

    console.log(
      `${name.padEnd(20)} mode=${mode.padEnd(11)} valid=${stillValid} hashUnchanged=${hashUnchanged}`,
    );
  }

  writeFileSync(join(OUT, "compare.html"), page(pairs), "utf8");
  console.log(`\nwrote ${OUT}/compare.html`);
}

function page(pairs: Pair[]): string {
  const rows = pairs
    .map(
      (pair) => `<section>
  <h2>${pair.name}<span class="mode">mode: ${pair.mode}</span></h2>
  <p class="why">${pair.why}</p>
  <div class="pair">
    <figure><figcaption>core fields only</figcaption>${pair.baseline}</figure>
    <figure><figcaption>reading <code>${BRANCH_EXTENSION_KEY}</code></figcaption>${pair.experimental}</figure>
  </div>
  <p class="checks">valid 0.1 document: <b>${pair.stillValid ? "yes" : "no"}</b> &#160;&#160;
     structure hash unchanged: <b>${pair.hashUnchanged ? "yes" : "no"}</b></p>
</section>`,
    )
    .join("\n");

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Branch extension: before and after</title>
<style>
  :root { color-scheme: light; }
  body { margin: 0; background: #E2E7EB; color: ${theme.ink};
         font-family: ${theme.sans}; padding: 40px 24px 80px; }
  header, section { max-width: 1000px; margin: 0 auto; }
  header { margin-bottom: 40px; }
  h1 { font-size: 20px; font-weight: 600; margin: 0 0 10px; letter-spacing: -0.01em; }
  header p { font-size: 13.5px; line-height: 1.65; color: #4A5761; margin: 0 0 10px; max-width: 660px; }
  section { margin-bottom: 46px; border-top: 1px solid ${theme.rule}; padding-top: 22px; }
  h2 { font-family: ${theme.mono}; font-size: 14px; font-weight: 500; margin: 0 0 6px;
       display: flex; justify-content: space-between; align-items: baseline; gap: 16px; }
  .mode { font-family: ${theme.sans}; font-size: 11.5px; color: #4A5761; }
  .why { font-size: 12.5px; line-height: 1.6; color: #4A5761; margin: 0 0 18px; max-width: 660px; }
  .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }
  @media (max-width: 760px) { .pair { grid-template-columns: 1fr; } }
  figure { margin: 0; background: ${theme.paper}; border: 1px solid ${theme.rule}; }
  figcaption { padding: 10px 14px; border-bottom: 1px solid ${theme.rule};
               font-size: 11.5px; color: #4A5761; }
  code { font-family: ${theme.mono}; font-size: 11px; }
  svg { display: block; width: 100%; height: auto; }
  .checks { font-size: 11.5px; color: #4A5761; margin: 14px 0 0; }
</style>
</head>
<body>
<header>
  <h1>What a branch field buys a consumer</h1>
  <p>Left: the same renderer reading core fields only. Right: the same renderer
  reading a proposed <code>${BRANCH_EXTENSION_KEY}</code> on <code>structure</code>,
  placed there to mirror <code>joins[]</code>.</p>
  <p>The extension is prototyped rather than produced. Each pair records whether the
  extended document is still a valid 0.1 document and whether its structure hash moved,
  because a field that cannot be trialled without invalidating published receipts is not
  worth trialling.</p>
</header>
${rows}
</body>
</html>
`;
}

main();
