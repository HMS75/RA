"use client";

import { useEffect, useState } from "react";
import { getOverview } from "@/lib/api";
import type { Overview } from "@/lib/types";

/** Small badge in the header: how much the database holds, or "backend offline". */
export default function OverviewBadge() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    getOverview().then(setOverview).catch(() => setOffline(true));
  }, []);

  if (offline) {
    return (
      <span className="inline-flex items-center gap-2 rounded-full border border-red-300 px-3 py-1 text-xs text-red-600 dark:border-red-900 dark:text-red-400">
        <span className="h-2 w-2 rounded-full bg-red-500" /> backend offline
      </span>
    );
  }
  if (!overview) return null;
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-zinc-300 px-3 py-1 text-xs text-zinc-600 dark:border-zinc-700 dark:text-zinc-400">
      <span className="h-2 w-2 rounded-full bg-emerald-500" />
      {overview.papers} papers · {overview.chunks.toLocaleString()} chunks
    </span>
  );
}
