import { ExternalLink } from "lucide-react";
import type { Source } from "@/lib/types";

type Props = { sources: Source[]; activeSource: number | null };

/** The list of papers (and the exact text pieces) the review cites. */
export default function SourcesPanel({ sources, activeSource }: Props) {
  if (sources.length === 0) {
    return <p className="text-sm text-zinc-500">The review did not cite any sources.</p>;
  }
  return (
    <ol className="space-y-3">
      {sources.map((s) => (
        <li
          key={s.number}
          id={`source-${s.number}`}
          className={`rounded-lg border p-3 transition ${
            activeSource === s.number
              ? "border-indigo-500 bg-indigo-500/5 ring-2 ring-indigo-500/40"
              : "border-zinc-200 dark:border-zinc-800"
          }`}
        >
          <div className="flex items-start gap-3">
            <span className="mt-0.5 inline-flex h-6 min-w-6 items-center justify-center rounded bg-indigo-500/15 px-1.5 text-xs font-semibold text-indigo-700 dark:text-indigo-300">
              {s.number}
            </span>
            <div className="min-w-0 flex-1">
              <div className="font-medium leading-snug">{s.title}</div>
              <div className="mt-0.5 flex flex-wrap items-center gap-x-3 text-xs text-zinc-500">
                <span>{s.year}</span>
                <span>Section: {s.section}</span>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-indigo-600 hover:underline dark:text-indigo-400"
                >
                  arXiv <ExternalLink size={12} />
                </a>
              </div>
              <details className="mt-2 text-sm">
                <summary className="cursor-pointer text-xs text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200">
                  Show the exact text used
                </summary>
                <p className="mt-2 rounded bg-zinc-100 p-3 leading-relaxed text-zinc-700 dark:bg-zinc-900 dark:text-zinc-300">
                  {s.text}
                </p>
              </details>
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}
