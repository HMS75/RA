import type { ResearchResult } from "./types";

/**
 * The review text contains citations like [1], [2][5] or [1, 3].
 * This turns each number into a markdown link "[1](#cite-1)" so we can render it as a clickable chip.
 */
export function linkCitations(markdown: string): string {
  return markdown.replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (_match, group: string) =>
    group
      .split(",")
      .map((n) => n.trim())
      .map((n) => `[${n}](#cite-${n})`)
      .join(""),
  );
}

/** Plain-markdown version of a review (used by the "Copy as Markdown" button). */
export function buildMarkdown(result: ResearchResult): string {
  const lines = [`# Literature review: ${result.topic}`, "", result.review, "", "## Sources", ""];
  for (const s of result.sources) {
    lines.push(`[${s.number}] ${s.title} (${s.year}), section: ${s.section} - ${s.url}`);
  }
  return lines.join("\n");
}
