"use client";

import { useMemo } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { linkCitations } from "@/lib/citations";
import type { Source } from "@/lib/types";
import CitationChip from "./CitationChip";

type Props = {
  review: string;
  sources: Source[];
  activeSource: number | null;
  onCite: (n: number) => void;
};

/** Renders the review markdown, with every [n] turned into a clickable citation chip. */
export default function ReviewBody({ review, sources, activeSource, onCite }: Props) {
  const components = useMemo<Components>(
    () => ({
      h1: ({ children }) => <h1 className="mt-8 mb-3 text-xl font-bold">{children}</h1>,
      h2: ({ children }) => (
        <h2 className="mt-8 mb-2 border-b border-zinc-200 pb-1 text-lg font-semibold dark:border-zinc-800">
          {children}
        </h2>
      ),
      h3: ({ children }) => <h3 className="mt-5 mb-1 font-semibold">{children}</h3>,
      p: ({ children }) => <p className="my-3 leading-relaxed">{children}</p>,
      ul: ({ children }) => <ul className="my-3 list-disc space-y-1.5 pl-6">{children}</ul>,
      ol: ({ children }) => <ol className="my-3 list-decimal space-y-1.5 pl-6">{children}</ol>,
      li: ({ children }) => <li className="leading-relaxed">{children}</li>,
      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
      a: ({ href, children }) => {
        if (href?.startsWith("#cite-")) {
          const n = Number(href.replace("#cite-", ""));
          const source = sources.find((s) => s.number === n);
          return <CitationChip n={n} source={source} active={activeSource === n} onClick={onCite} />;
        }
        return (
          <a href={href} target="_blank" rel="noreferrer" className="text-indigo-600 underline dark:text-indigo-400">
            {children}
          </a>
        );
      },
    }),
    [sources, activeSource, onCite],
  );

  return (
    <div className="text-[15px]">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {linkCitations(review)}
      </ReactMarkdown>
    </div>
  );
}
