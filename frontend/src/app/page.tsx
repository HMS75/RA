"use client";

import { BookOpenCheck } from "lucide-react";
import OverviewBadge from "@/components/OverviewBadge";
import ResultPreview from "@/components/ResultPreview";
import StepFeed from "@/components/StepFeed";
import TopicForm from "@/components/TopicForm";
import { useResearch } from "@/hooks/useResearch";

export default function Home() {
  const { status, steps, result, error, start, cancel } = useResearch();
  const running = status === "running";

  return (
    <main className="mx-auto max-w-3xl space-y-8 px-4 py-10">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="flex items-center gap-2 text-2xl font-bold">
            <BookOpenCheck className="text-indigo-500" /> Research Paper Agent
          </h1>
          <OverviewBadge />
        </div>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Give a topic. The agent plans, searches papers, fills gaps from arXiv, compares them, and writes a
          literature review with citations. You can watch every step live.
        </p>
      </header>

      <TopicForm running={running} onSubmit={start} />

      {error && (
        <div className="rounded-lg border border-red-300 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:text-red-300">
          {error}
        </div>
      )}

      {steps.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">Agent activity</h2>
            {running && (
              <button
                onClick={cancel}
                className="text-xs text-zinc-500 underline hover:text-zinc-800 dark:hover:text-zinc-200"
                title="The agent keeps running on the server and the review is still saved"
              >
                Stop watching
              </button>
            )}
          </div>
          <div className="rounded-xl border border-zinc-300 p-4 dark:border-zinc-700">
            <StepFeed steps={steps} running={running} />
          </div>
        </section>
      )}

      {status === "stopped" && (
        <p className="text-sm text-zinc-500">
          Stopped watching. The agent may still be finishing on the server, so wait a bit before starting a new run.
        </p>
      )}

      {result && <ResultPreview result={result} />}
    </main>
  );
}
