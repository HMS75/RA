"use client";

import { useCallback, useState } from "react";
import { Check, Copy } from "lucide-react";
import { buildMarkdown } from "@/lib/citations";
import type { ResearchResult } from "@/lib/types";
import CitationCheck from "./CitationCheck";
import ComparisonTable from "./ComparisonTable";
import CoverageSummary from "./CoverageSummary";
import ReviewBody from "./ReviewBody";
import SourcesPanel from "./SourcesPanel";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}

/** The finished review: text with clickable citations, comparison table, sources, citation check. */
export default function ReviewView({ result }: { result: ResearchResult }) {
  const [activeSource, setActiveSource] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);

  const onCite = useCallback((n: number) => {
    setActiveSource(n);
    document.getElementById(`source-${n}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, []);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(buildMarkdown(result));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard not available, ignore */
    }
  };

  return (
    <article className="space-y-10">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-zinc-500">Literature review</p>
          <h1 className="text-2xl font-bold">{result.topic}</h1>
          <p className="mt-1 text-sm text-zinc-500">
            {result.sources.length} sources cited · {result.comparison.length} papers compared
          </p>
        </div>
        <button
          onClick={copy}
          className="inline-flex items-center gap-2 rounded-lg border border-zinc-300 px-3 py-2 text-sm hover:border-indigo-500 dark:border-zinc-700"
        >
          {copied ? <Check size={16} className="text-emerald-500" /> : <Copy size={16} />}
          {copied ? "Copied" : "Copy as Markdown"}
        </button>
      </header>

      <Section title="How well the papers covered each question">
        <CoverageSummary items={result.sub_questions} />
      </Section>

      <div className="rounded-xl border border-zinc-200 px-6 py-2 dark:border-zinc-800">
        <ReviewBody review={result.review} sources={result.sources} activeSource={activeSource} onCite={onCite} />
      </div>

      <Section title="Paper comparison">
        <ComparisonTable rows={result.comparison} />
      </Section>

      <Section title="Sources">
        <p className="text-sm text-zinc-500">Click a number in the review to jump to its source here.</p>
        <SourcesPanel sources={result.sources} activeSource={activeSource} />
      </Section>

      <Section title="Citation check">
        <CitationCheck result={result} />
      </Section>
    </article>
  );
}
