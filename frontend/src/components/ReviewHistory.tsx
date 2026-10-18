"use client";

import { useEffect, useState } from "react";
import { History } from "lucide-react";
import { getReviews } from "@/lib/api";
import type { ReviewSummary } from "@/lib/types";

type Props = { onOpen: (slug: string) => void };

/** Reviews saved from earlier runs. Opening one is instant: no agent run, no LLM calls. */
export default function ReviewHistory({ onOpen }: Props) {
  const [reviews, setReviews] = useState<ReviewSummary[] | null>(null);

  useEffect(() => {
    getReviews().then(setReviews).catch(() => setReviews([]));
  }, []);

  if (!reviews || reviews.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="flex items-center gap-2 font-semibold">
        <History size={18} className="text-indigo-500" /> Past reviews
      </h2>
      <ul className="divide-y divide-zinc-200 rounded-xl border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
        {reviews.map((r) => (
          <li key={r.slug}>
            <button
              onClick={() => onOpen(r.slug)}
              className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm hover:bg-zinc-100 dark:hover:bg-zinc-900"
            >
              <span className="font-medium">{r.topic}</span>
              <span className="shrink-0 text-xs text-zinc-500">
                {r.sources} sources · {new Date(r.created * 1000).toLocaleDateString()}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
