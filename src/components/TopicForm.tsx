"use client";

import { useState } from "react";
import { Search } from "lucide-react";

const EXAMPLES = [
  "methods for reducing LLM hallucination",
  "impact of noisy data on language model performance",
  "limitations of retrieval-augmented generation",
];

type Props = {
  running: boolean;
  onSubmit: (topic: string, expand: boolean) => void;
};

export default function TopicForm({ running, onSubmit }: Props) {
  const [topic, setTopic] = useState("");
  const [expand, setExpand] = useState(true);
  const canSubmit = topic.trim().length >= 3 && !running;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (canSubmit) onSubmit(topic.trim(), expand);
      }}
      className="space-y-3"
    >
      <div className="flex gap-2">
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          maxLength={200}
          placeholder="Enter a research topic..."
          disabled={running}
          className="flex-1 rounded-lg border border-zinc-300 bg-transparent px-4 py-3 outline-none focus:border-indigo-500 disabled:opacity-60 dark:border-zinc-700"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Search size={18} /> Research
        </button>
      </div>

      <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
        <input
          type="checkbox"
          checked={expand}
          disabled={running}
          onChange={(e) => setExpand(e.target.checked)}
          className="h-4 w-4 accent-indigo-600"
        />
        Let the agent search arXiv and add papers when my database has gaps (slower)
      </label>

      <div className="flex flex-wrap gap-2 pt-1">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            disabled={running}
            onClick={() => setTopic(example)}
            className="rounded-full border border-zinc-300 px-3 py-1 text-xs text-zinc-600 transition hover:border-indigo-500 hover:text-indigo-600 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-400"
          >
            {example}
          </button>
        ))}
      </div>
    </form>
  );
}
