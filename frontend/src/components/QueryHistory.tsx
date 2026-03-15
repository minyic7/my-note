import type { QueryHistoryEntry } from "../types";

interface Props {
  entries: QueryHistoryEntry[];
  selectedId: string | null;
  onSelect: (entry: QueryHistoryEntry) => void;
}

export default function QueryHistory({ entries, selectedId, onSelect }: Props) {
  if (entries.length === 0) {
    return (
      <div className="p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-400">
          Query History
        </h3>
        <p className="mt-3 text-center text-xs text-gray-400">
          No queries yet. Ask a question to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="p-3">
      <h3 className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
        Query History
      </h3>
      <ul className="space-y-1">
        {entries.map((entry) => {
          const isSelected = entry.id === selectedId;
          return (
            <li key={entry.id}>
              <button
                onClick={() => onSelect(entry)}
                className={`w-full rounded-md px-2 py-2 text-left transition ${
                  isSelected
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                <p className="line-clamp-2 text-sm">{entry.question}</p>
                <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
                  <time>{formatTime(entry.timestamp)}</time>
                  {entry.findings.length > 0 && (
                    <span className="rounded bg-gray-100 px-1 py-0.5">
                      {entry.findings.length} finding{entry.findings.length === 1 ? "" : "s"}
                    </span>
                  )}
                </div>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}
