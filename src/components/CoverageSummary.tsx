import type { ResearchResult } from "@/lib/types";

function badge(score: number) {
  if (score >= 7) return "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300";
  if (score >= 4) return "bg-amber-500/15 text-amber-700 dark:text-amber-300";
  return "bg-red-500/15 text-red-700 dark:text-red-300";
}

/** For each sub-question the agent asked: how well the papers covered it, and how many it added. */
export default function CoverageSummary({ items }: { items: ResearchResult["sub_questions"] }) {
  if (!items || items.length === 0) return null;
  return (
    <ul className="space-y-2">
      {items.map((q) => (
        <li key={q.question} className="flex items-start gap-3 text-sm">
          <span className={`mt-0.5 shrink-0 rounded px-2 py-0.5 text-xs font-semibold ${badge(q.coverage.score)}`}>
            {q.coverage.score}/10
          </span>
          <div>
            <div>{q.question}</div>
            <div className="text-xs text-zinc-500">
              {q.papers_added > 0 ? `Agent added ${q.papers_added} new paper(s). ` : ""}
              {q.coverage.score < 7 && q.coverage.missing ? `Still missing: ${q.coverage.missing}` : ""}
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
