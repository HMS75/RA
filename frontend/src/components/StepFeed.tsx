"use client";

import { useEffect, useRef } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import type { TimedStep } from "@/lib/types";

// Friendly label + colour for each kind of step the agent can report
const PHASES: Record<string, { label: string; color: string }> = {
  plan: { label: "Plan", color: "bg-violet-500/15 text-violet-600 dark:text-violet-300" },
  plan_done: { label: "Plan", color: "bg-violet-500/15 text-violet-600 dark:text-violet-300" },
  check: { label: "Check", color: "bg-sky-500/15 text-sky-600 dark:text-sky-300" },
  coverage: { label: "Coverage", color: "bg-sky-500/15 text-sky-600 dark:text-sky-300" },
  search: { label: "Search", color: "bg-amber-500/15 text-amber-600 dark:text-amber-300" },
  search_done: { label: "Search", color: "bg-amber-500/15 text-amber-600 dark:text-amber-300" },
  rewrite: { label: "Retry", color: "bg-amber-500/15 text-amber-600 dark:text-amber-300" },
  filter: { label: "Filter", color: "bg-orange-500/15 text-orange-600 dark:text-orange-300" },
  ingest: { label: "Add papers", color: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-300" },
  ingest_done: { label: "Add papers", color: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-300" },
  compare: { label: "Compare", color: "bg-pink-500/15 text-pink-600 dark:text-pink-300" },
  write: { label: "Write", color: "bg-indigo-500/15 text-indigo-600 dark:text-indigo-300" },
  repair: { label: "Fix citations", color: "bg-indigo-500/15 text-indigo-600 dark:text-indigo-300" },
  done: { label: "Done", color: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-300" },
};

function scoreColor(score: number) {
  if (score >= 7) return "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300";
  if (score >= 4) return "bg-amber-500/15 text-amber-700 dark:text-amber-300";
  return "bg-red-500/15 text-red-700 dark:text-red-300";
}

type Props = { steps: TimedStep[]; running: boolean };

export default function StepFeed({ steps, running }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // keep the newest step in view
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [steps.length]);

  return (
    <ol className="space-y-3">
      {steps.map((s, i) => {
        const isLast = i === steps.length - 1;
        const spinning = running && isLast && s.step !== "done";
        const phase = PHASES[s.step] ?? { label: s.step, color: "bg-zinc-500/15 text-zinc-600" };

        return (
          <li key={i} className="flex gap-3">
            <div className="mt-0.5">
              {spinning ? (
                <Loader2 size={18} className="animate-spin text-indigo-500" />
              ) : (
                <CheckCircle2 size={18} className="text-emerald-500" />
              )}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded px-2 py-0.5 text-xs font-medium ${phase.color}`}>{phase.label}</span>
                <span className="text-sm">{s.message}</span>
                {typeof s.score === "number" && (
                  <span className={`rounded px-2 py-0.5 text-xs font-semibold ${scoreColor(s.score)}`}>
                    {s.score}/10
                  </span>
                )}
                <span className="ml-auto text-xs text-zinc-400">+{s.t}s</span>
              </div>

              {s.step === "plan_done" && s.sub_questions && (
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-600 dark:text-zinc-400">
                  {s.sub_questions.map((q) => (
                    <li key={q.question}>{q.question}</li>
                  ))}
                </ul>
              )}

              {s.step === "coverage" && s.missing && s.score !== undefined && s.score < 7 && (
                <p className="mt-1 text-xs text-zinc-500">Missing: {s.missing}</p>
              )}

              {(s.step === "filter" || s.step === "compare") && s.papers && s.papers.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {s.papers.map((p) => (
                    <span
                      key={p}
                      className="max-w-full truncate rounded border border-zinc-300 px-2 py-0.5 text-xs text-zinc-600 dark:border-zinc-700 dark:text-zinc-400"
                      title={p}
                    >
                      {p}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </li>
        );
      })}
      <div ref={bottomRef} />
    </ol>
  );
}
