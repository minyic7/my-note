import { useState } from "react";
import type { SourceReference } from "../types";

interface Props {
  sources: SourceReference[];
}

export default function SourcesPanel({ sources }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
        Sources ({sources.length})
      </h3>
      <div className="space-y-2">
        {sources.map((source, i) => {
          const isExpanded = expanded === i;
          return (
            <button
              key={i}
              onClick={() => setExpanded(isExpanded ? null : i)}
              className="w-full rounded-lg border border-gray-200 bg-white p-3 text-left transition hover:border-gray-300"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <svg
                    className="h-4 w-4 shrink-0 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                    />
                  </svg>
                  <span className="text-sm font-medium text-gray-800">
                    {source.document_title}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded bg-blue-50 px-1.5 py-0.5 text-xs text-blue-600">
                    {Math.round(source.relevance_score * 100)}% match
                  </span>
                  <svg
                    className={`h-4 w-4 text-gray-400 transition ${isExpanded ? "rotate-180" : ""}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              {isExpanded && (
                <div className="mt-2 rounded bg-gray-50 p-2 text-xs leading-relaxed text-gray-600">
                  {source.chunk_text}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </section>
  );
}
