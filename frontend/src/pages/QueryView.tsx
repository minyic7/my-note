import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProject, streamQuery } from "../api";
import type { Project, QueryHistoryEntry, QueryResponse } from "../types";
import QueryInput from "../components/QueryInput";
import QueryResults from "../components/QueryResults";
import QueryHistory from "../components/QueryHistory";
import LoadingIndicator from "../components/LoadingIndicator";

export default function QueryView() {
  const { projectId } = useParams<{ projectId: string }>();

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [currentResult, setCurrentResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistoryEntry[]>([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!projectId) return;
    getProject(projectId)
      .then(setProject)
      .catch(() => setProject(null));
  }, [projectId]);

  const handleSubmit = useCallback(
    (question: string) => {
      if (!projectId) return;

      // Cancel any in-flight request
      abortRef.current?.abort();

      setLoading(true);
      setStreamingText("");
      setCurrentResult(null);
      setError(null);
      setSelectedHistoryId(null);

      let accumulated = "";

      const controller = streamQuery(
        projectId,
        question,
        (chunk) => {
          accumulated += chunk;
          setStreamingText(accumulated);
        },
        (result) => {
          setCurrentResult(result);
          setStreamingText("");
          setLoading(false);

          const entry: QueryHistoryEntry = {
            id: crypto.randomUUID(),
            question,
            answer: result.answer,
            sources: result.sources,
            findings: result.findings,
            entities: result.entities,
            relations: result.relations,
            timestamp: new Date().toISOString(),
          };
          setHistory((prev) => [entry, ...prev]);
          setSelectedHistoryId(entry.id);
        },
        (err) => {
          setError(err.message);
          setLoading(false);
        },
      );

      abortRef.current = controller;
    },
    [projectId],
  );

  const handleSelectHistory = useCallback((entry: QueryHistoryEntry) => {
    setSelectedHistoryId(entry.id);
    setCurrentResult({
      answer: entry.answer,
      sources: entry.sources,
      findings: entry.findings,
      entities: entry.entities,
      relations: entry.relations,
    });
    setStreamingText("");
    setError(null);
  }, []);

  const displayResult = currentResult;

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="flex shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 py-3">
        <div className="flex items-center gap-3">
          <Link
            to={projectId ? `/projects/${projectId}` : "/"}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            title="Back to project"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              {project?.name ?? "Project"}
            </h1>
            {project?.description && (
              <p className="text-xs text-gray-500">{project.description}</p>
            )}
          </div>
        </div>
        <button
          onClick={() => setSidebarOpen((v) => !v)}
          className="rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
        >
          {sidebarOpen ? "Hide" : "Show"} History
        </button>
      </header>

      {/* Main content */}
      <div className="flex min-h-0 flex-1">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-72 shrink-0 overflow-y-auto border-r border-gray-200 bg-white">
            <QueryHistory
              entries={history}
              selectedId={selectedHistoryId}
              onSelect={handleSelectHistory}
            />
          </aside>
        )}

        {/* Query area */}
        <main className="flex min-w-0 flex-1 flex-col">
          <div className="flex-1 overflow-y-auto p-4 md:p-6">
            {error && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                <span className="font-medium">Error:</span> {error}
              </div>
            )}

            {loading && !streamingText && <LoadingIndicator />}

            {streamingText && !currentResult && (
              <QueryResults
                answer={streamingText}
                sources={[]}
                findings={[]}
                entities={[]}
                relations={[]}
                streaming
              />
            )}

            {displayResult && (
              <QueryResults
                answer={displayResult.answer}
                sources={displayResult.sources}
                findings={displayResult.findings}
                entities={displayResult.entities}
                relations={displayResult.relations}
              />
            )}

            {!loading && !displayResult && !streamingText && !error && (
              <div className="flex h-full items-center justify-center">
                <div className="text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-50">
                    <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                    </svg>
                  </div>
                  <h2 className="text-lg font-medium text-gray-700">Ask a question</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    Query your project materials to find insights, risks, and relationships.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Query input at bottom */}
          <div className="shrink-0 border-t border-gray-200 bg-white p-4">
            <QueryInput onSubmit={handleSubmit} disabled={loading} />
          </div>
        </main>
      </div>
    </div>
  );
}
