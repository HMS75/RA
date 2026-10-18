import { AlertTriangle, ShieldCheck } from "lucide-react";
import type { ResearchResult } from "@/lib/types";

/** Shows the result of the automatic citation check the backend runs on every review. */
export default function CitationCheck({ result }: { result: ResearchResult }) {
  const uncited = result.uncited_sentences;
  const invalid = result.invalid_citations;

  if (uncited.length === 0 && invalid.length === 0) {
    return (
      <p className="inline-flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-400">
        <ShieldCheck size={16} /> Every statement in this review points to a source.
      </p>
    );
  }
  return (
    <div className="space-y-2 text-sm">
      <p className="inline-flex items-center gap-2 text-amber-700 dark:text-amber-400">
        <AlertTriangle size={16} />
        Automatic check found {uncited.length + invalid.length} possible problem(s). Treat these statements with care.
      </p>
      {invalid.length > 0 && (
        <p className="text-zinc-600 dark:text-zinc-400">
          Source numbers that don&apos;t exist: {invalid.join(", ")}
        </p>
      )}
      {uncited.length > 0 && (
        <details>
          <summary className="cursor-pointer text-zinc-600 dark:text-zinc-400">
            {uncited.length} statement(s) with no citation
          </summary>
          <ul className="mt-2 list-disc space-y-1 pl-6 text-zinc-600 dark:text-zinc-400">
            {uncited.map((u) => (
              <li key={u}>{u}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
