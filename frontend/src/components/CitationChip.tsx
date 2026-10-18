"use client";

import type { Source } from "@/lib/types";

type Props = {
  n: number;
  source?: Source; // undefined = the LLM cited a number that doesn't exist
  active: boolean;
  onClick: (n: number) => void;
};

/** The small clickable [3] badge inside the review text. */
export default function CitationChip({ n, source, active, onClick }: Props) {
  const base =
    "mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded px-1 align-baseline text-[11px] font-semibold transition";
  if (!source) {
    return (
      <span className={`${base} bg-red-500/15 text-red-600 dark:text-red-300`} title="This source number doesn't exist">
        {n}?
      </span>
    );
  }
  return (
    <button
      type="button"
      onClick={() => onClick(n)}
      title={`${source.title} (${source.year}), ${source.section}`}
      className={`${base} ${
        active
          ? "bg-indigo-600 text-white"
          : "bg-indigo-500/15 text-indigo-700 hover:bg-indigo-500/30 dark:text-indigo-300"
      }`}
    >
      {n}
    </button>
  );
}
