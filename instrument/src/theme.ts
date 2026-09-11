/**
 * Design tokens.
 *
 * Concept: an engineering drawing. Everything the document asserts is drawn in
 * ink. Everything the document cannot assert is a redline annotation. Red is
 * used for exactly one meaning — "do not trust this part" — and for nothing else.
 */
export const theme = {
  paper: "#EDF0F3",
  ink: "#172029",
  muted: "#6B7883",
  rule: "#C3CCD4",
  redline: "#C0362C",
  redlineWash: "rgba(192,54,44,0.10)",

  // Identifiers are literal strings lifted from source, so they are set in a
  // monospace face. Prose is not.
  mono: "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace",
  sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
} as const;

export const metrics = {
  nodeHeight: 38,
  nodePadX: 16,
  charWidth: 7.4, // 12.5px monospace advance, measured empirically
  fontSize: 12.5,
  minNodeWidth: 64,
  rankGap: 74,
  siblingGap: 30,
  marginX: 28,
  marginTop: 28,
  marginBottom: 28,
  joinBarHeight: 7,
} as const;
