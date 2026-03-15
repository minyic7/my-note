import { useState } from "react";
import * as api from "../../api";
import type { Document } from "../../types";

interface Props {
  projectId: string;
  onComplete: (doc: Document) => void;
}

export default function RawTextForm({ projectId, onComplete }: Props) {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const doc = await api.ingestText(projectId, {
        title: title.trim() || "Untitled",
        text: text.trim(),
      });
      onComplete(doc);
      setTitle("");
      setText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label
          htmlFor="text-title"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Title (optional)
        </label>
        <input
          id="text-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Meeting notes, idea, etc."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
      <div className="mb-4">
        <label
          htmlFor="text-content"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Content
        </label>
        <textarea
          id="text-content"
          required
          rows={6}
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setError(null);
          }}
          placeholder="Paste or type your text here..."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={!text.trim() || loading}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {loading ? "Ingesting..." : "Ingest Text"}
      </button>
    </form>
  );
}
