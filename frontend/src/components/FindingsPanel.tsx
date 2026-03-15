import { useState } from "react";
import type { Finding } from "../types";

interface Props {
  findings: Finding[];
}

const TYPE_CONFIG = {
  risk: {
    label: "Risk",
    bg: "bg-red-50",
    border: "border-red-200",
    badge: "bg-red-100 text-red-800",
    icon: "!",
  },
  gap: {
    label: "Missing Info",
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    badge: "bg-yellow-100 text-yellow-800",
    icon: "?",
  },
  conflict: {
    label: "Contradiction",
    bg: "bg-orange-50",
    border: "border-orange-200",
    badge: "bg-orange-100 text-orange-800",
    icon: "~",
  },
  insight: {
    label: "Insight",
    bg: "bg-blue-50",
    border: "border-blue-200",
    badge: "bg-blue-100 text-blue-800",
    icon: "i",
  },
} as const;

const SEVERITY_BADGE: Record<string, string> = {
  high: "bg-red-600 text-white",
  medium: "bg-yellow-500 text-white",
  low: "bg-gray-300 text-gray-700",
};

export default function FindingsPanel({ findings }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const grouped = {
    risk: findings.filter((f) => f.type === "risk"),
    conflict: findings.filter((f) => f.type === "conflict"),
    gap: findings.filter((f) => f.type === "gap"),
    insight: findings.filter((f) => f.type === "insight"),
  };

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
        Findings
      </h3>
      <div className="space-y-2">
        {(["risk", "conflict", "gap", "insight"] as const).map((type) =>
          grouped[type].map((finding) => {
            const cfg = TYPE_CONFIG[type];
            const isExpanded = expandedId === finding.id;
            return (
              <button
                key={finding.id}
                onClick={() => setExpandedId(isExpanded ? null : finding.id)}
                className={`w-full rounded-lg border text-left transition ${cfg.border} ${cfg.bg} p-3`}
              >
                <div className="flex items-start gap-2">
                  <span
                    className={`mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold ${cfg.badge}`}
                  >
                    {cfg.icon}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${cfg.badge}`}>
                        {cfg.label}
                      </span>
                      {finding.severity && (
                        <span
                          className={`rounded px-1.5 py-0.5 text-xs font-medium ${SEVERITY_BADGE[finding.severity] ?? ""}`}
                        >
                          {finding.severity}
                        </span>
                      )}
                    </div>
                    <p
                      className={`mt-1 text-sm text-gray-800 ${isExpanded ? "" : "line-clamp-2"}`}
                    >
                      {finding.content}
                    </p>
                  </div>
                  <svg
                    className={`h-4 w-4 shrink-0 text-gray-400 transition ${isExpanded ? "rotate-180" : ""}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>
            );
          }),
        )}
      </div>
    </section>
  );
}
