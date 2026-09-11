import { readdirSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { assertTopologyDocument } from "@agent-topology/spec";
import type { TopologyDocument } from "@agent-topology/spec";
import { renderGraph } from "./render.js";
import { theme } from "./theme.js";

/**
 * Renders every conformance fixture and writes a gallery.
 *
 * The fixtures are the shared ground truth every producer is measured against,
 * so they are also the right corpus for a consumer: nothing here is invented,
 * and coverage of the hard cases is inherited rather than guessed at.
 */

const FIXTURES = process.env.FIXTURES ?? "../repo/conformance/fixtures";
const OUT = process.env.OUT ?? "out";

interface Rendered {
  name: string;
  graphId: string;
  svg: string;
  status: string;
  gapCodes: string[];
}

function main(): void {
  mkdirSync(OUT, { recursive: true });
  const names = readdirSync(FIXTURES, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();

  const rendered: Rendered[] = [];

  for (const name of names) {
    const raw = readFileSync(join(FIXTURES, name, "expected.json"), "utf8");
    const parsed: unknown = JSON.parse(raw);

    // Refuse anything the installed contract does not accept, rather than
    // rendering a best guess. Producers refuse untested framework versions
    // before inspecting a graph; a consumer should hold the same line.
    assertTopologyDocument(parsed);
    const doc = parsed as TopologyDocument;

    if (doc.topologyVersion !== "0.1") {
      throw new Error(`${name}: unsupported topologyVersion ${doc.topologyVersion}`);
    }

    for (const graph of doc.graphs) {
      const svg = renderGraph(doc, graph);

      // Determinism is a stated requirement, so it is checked rather than assumed.
      if (renderGraph(doc, graph) !== svg) {
        throw new Error(`${name}: renderer is not deterministic`);
      }

      writeFileSync(join(OUT, `${name}.svg`), `${svg}\n`, "utf8");
      rendered.push({
        name,
        graphId: graph.id,
        svg,
        status: doc.completeness.status,
        gapCodes: doc.completeness.gaps.map((gap) => gap.code),
      });
    }
  }

  writeFileSync(join(OUT, "index.html"), gallery(rendered), "utf8");
  console.log(`rendered ${rendered.length} graphs from ${names.length} fixtures -> ${OUT}/`);
}

function gallery(items: Rendered[]): string {
  const cards = items
    .map((item) => {
      const flag =
        item.status === "complete"
          ? ""
          : `<span class="flag">${item.gapCodes.join(", ")}</span>`;
      return `<figure><figcaption><span class="name">${item.name}</span>${flag}</figcaption>${item.svg}</figure>`;
    })
    .join("\n");

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>agent-topology conformance fixtures</title>
<style>
  :root { color-scheme: light; }
  body {
    margin: 0;
    background: #E2E7EB;
    color: ${theme.ink};
    font-family: ${theme.sans};
    padding: 40px 24px 80px;
  }
  header { max-width: 660px; margin: 0 auto 44px; }
  h1 { font-size: 20px; font-weight: 600; margin: 0 0 10px; letter-spacing: -0.01em; }
  header p { font-size: 13.5px; line-height: 1.65; color: #4A5761; margin: 0 0 10px; }
  .key { display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: 12px; color: #4A5761;
         border-top: 1px solid ${theme.rule}; padding-top: 14px; margin-top: 18px; }
  .key b { font-weight: 600; color: ${theme.ink}; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
          gap: 24px; max-width: 1180px; margin: 0 auto; align-items: start; }
  figure { margin: 0; background: ${theme.paper}; border: 1px solid ${theme.rule}; }
  figcaption { display: flex; justify-content: space-between; align-items: baseline; gap: 12px;
               padding: 11px 14px; border-bottom: 1px solid ${theme.rule}; }
  .name { font-family: ${theme.mono}; font-size: 12px; }
  .flag { font-size: 10.5px; font-family: ${theme.mono}; color: ${theme.redline}; }
  svg { display: block; width: 100%; height: auto; }
  @media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
</style>
</head>
<body>
<header>
  <h1>Conformance fixtures, rendered</h1>
  <p>Every drawing here is derived from <code>expected.json</code> in the agent-topology
  conformance suite. Nothing is hand-placed, and the renderer is a pure function, so
  a fixture change is the only thing that can change a drawing.</p>
  <p>Ink is what the document asserts. Red is what it cannot: each red mark carries a
  numbered note in the block beneath the drawing.</p>
  <div class="key">
    <span><b>Filled pill</b> entry node</span>
    <span><b>Double outline</b> exit node</span>
    <span><b>Solid line</b> direct edge</span>
    <span><b>Dashed line</b> conditional edge</span>
    <span><b>Dotted line</b> derived from joins[]</span>
    <span><b>Bar across edge</b> interrupt</span>
  </div>
</header>
<main class="grid">
${cards}
</main>
</body>
</html>
`;
}

main();
