import { useState } from "react";
import * as api from "../../api";
import type { Document } from "../../types";

interface Props {
  projectId: string;
  onComplete: (doc: Document) => void;
}

export default function UrlIngestForm({ projectId, onComplete }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    try {
      const doc = await api.ingestUrl(projectId, { url: trimmed });
      onComplete(doc);
      setUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <label
        htmlFor="ingest-url"
        className="mb-1 block text-sm font-medium text-gray-700"
      >
        Webpage URL
      </label>
      <div className="flex gap-2">
        <input
          id="ingest-url"
          type="url"
          required
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            setError(null);
          }}
          placeholder="https://example.com/article"
          className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={!url.trim() || loading}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Ingesting..." : "Ingest"}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </form>
  );
}
