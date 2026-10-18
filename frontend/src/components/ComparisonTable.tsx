import type { ComparisonRow } from "@/lib/types";

const COLUMNS: { key: keyof ComparisonRow; label: string }[] = [
  { key: "method", label: "Method" },
  { key: "data_or_benchmarks", label: "Data / benchmarks" },
  { key: "key_results", label: "Key results" },
  { key: "limitations", label: "Limitations" },
];

function Cell({ value }: { value?: string | number }) {
  const text = value === undefined ? "" : String(value);
  if (!text || text.toLowerCase().startsWith("not stated")) {
    return <span className="text-zinc-400 italic">not stated</span>;
  }
  return <>{text}</>;
}

/** Side-by-side comparison of the papers the agent looked at. Scrolls sideways on small screens. */
export default function ComparisonTable({ rows }: { rows: ComparisonRow[] }) {
  if (rows.length === 0) {
    return <p className="text-sm text-zinc-500">No papers were compared in this run.</p>;
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
      <table className="w-full min-w-[860px] border-collapse text-left text-sm">
        <thead className="bg-zinc-100 text-xs uppercase tracking-wide text-zinc-500 dark:bg-zinc-900">
          <tr>
            <th className="px-3 py-2 font-medium">Paper</th>
            {COLUMNS.map((c) => (
              <th key={c.key} className="px-3 py-2 font-medium">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.arxiv_id} className="border-t border-zinc-200 align-top dark:border-zinc-800">
              <td className="w-56 px-3 py-3">
                <a
                  href={`https://arxiv.org/abs/${row.arxiv_id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                >
                  {row.title ?? row.arxiv_id}
                </a>
                {row.year && <div className="text-xs text-zinc-500">{row.year}</div>}
              </td>
              {row.error ? (
                <td colSpan={COLUMNS.length} className="px-3 py-3 text-red-600 dark:text-red-400">
                  Could not summarise this paper: {row.error}
                </td>
              ) : (
                COLUMNS.map((c) => (
                  <td key={c.key} className="px-3 py-3 text-zinc-700 dark:text-zinc-300">
                    <Cell value={row[c.key] as string | undefined} />
                  </td>
                ))
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
