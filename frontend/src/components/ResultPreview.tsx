import { AlertTriangle, FileText } from "lucide-react";
import type { ResearchResult } from "@/lib/types";

/** Simple version for Day 7: shows the raw review text. Day 8 replaces this with the rich view. */
export default function ResultPreview({ result }: { result: ResearchResult }) {
  const warnings = result.uncited_sentences.length + result.invalid_citations.length;
  return (
    <section className="rounded-xl border border-zinc-300 p-5 dark:border-zinc-700">
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <FileText size={18} className="text-indigo-500" />
        <h2 className="font-semibold">Literature review ready</h2>
        <span className="text-xs text-zinc-500">
          {result.sources.length} sources cited · {result.comparison.length} papers compared
        </span>
        {warnings > 0 && (
          <span className="inline-flex items-center gap-1 text-xs text-amber-600">
            <AlertTriangle size={14} /> {warnings} citation warning(s)
          </span>
        )}
      </div>
      <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-relaxed">{result.review}</pre>
    </section>
  );
}
