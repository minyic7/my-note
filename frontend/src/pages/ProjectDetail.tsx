import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import * as api from "../api";
import type { Project, Document } from "../types";
import FileUploadForm from "../components/IngestPanel/FileUploadForm";
import UrlIngestForm from "../components/IngestPanel/UrlIngestForm";
import RawTextForm from "../components/IngestPanel/RawTextForm";
import DocumentList from "../components/IngestPanel/DocumentList";

type IngestTab = "file" | "url" | "text";

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<IngestTab>("file");

  const loadData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [proj, docs] = await Promise.all([
        api.getProject(id),
        api.listDocuments(id),
      ]);
      setProject(proj);
      setDocuments(docs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function handleIngestComplete(docs: Document | Document[]) {
    const newDocs = Array.isArray(docs) ? docs : [docs];
    setDocuments((prev) => [...newDocs, ...prev]);
    if (project) {
      setProject({
        ...project,
        document_count: project.document_count + newDocs.length,
        updated_at: new Date().toISOString(),
      });
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error ?? "Project not found"}
        </div>
        <Link
          to="/"
          className="mt-4 inline-block text-sm text-blue-600 hover:text-blue-700"
        >
          Back to projects
        </Link>
      </div>
    );
  }

  const tabs: { key: IngestTab; label: string }[] = [
    { key: "file", label: "Upload Files" },
    { key: "url", label: "From URL" },
    { key: "text", label: "Raw Text" },
  ];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link
        to="/"
        className="mb-4 inline-block text-sm text-gray-500 hover:text-gray-700"
      >
        &larr; All projects
      </Link>

      <div className="mb-6">
        <h1 className="text-2xl font-bold">{project.name}</h1>
        {project.description && (
          <p className="mt-1 text-gray-500">{project.description}</p>
        )}
        <div className="mt-2 flex items-center gap-4 text-sm text-gray-400">
          <span>
            {project.document_count}{" "}
            {project.document_count === 1 ? "document" : "documents"}
          </span>
          <span>
            Updated{" "}
            {new Date(project.updated_at).toLocaleDateString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
      </div>

      {/* Ingest Panel */}
      <div className="mb-8 rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? "border-b-2 border-blue-600 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        <div className="p-6">
          {activeTab === "file" && (
            <FileUploadForm
              projectId={project.id}
              onComplete={handleIngestComplete}
            />
          )}
          {activeTab === "url" && (
            <UrlIngestForm
              projectId={project.id}
              onComplete={handleIngestComplete}
            />
          )}
          {activeTab === "text" && (
            <RawTextForm
              projectId={project.id}
              onComplete={handleIngestComplete}
            />
          )}
        </div>
      </div>

      {/* Document List */}
      <DocumentList documents={documents} />
    </div>
  );
}
