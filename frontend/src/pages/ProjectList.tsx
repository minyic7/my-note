import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../api";
import type { Project, CreateProjectRequest } from "../types";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<CreateProjectRequest>({
    name: "",
    description: "",
  });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const project = await api.createProject(form);
      setProjects((prev) => [project, ...prev]);
      setForm({ name: "", description: "" });
      setShowForm(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create project",
      );
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">my-note</h1>
            <p className="mt-1 text-sm text-gray-500">Manage projects, ingest documents, and query your knowledge base</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            {showForm ? "Cancel" : "New Project"}
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {showForm && (
          <form
            onSubmit={handleCreate}
            className="mb-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
          >
            <h2 className="mb-4 text-lg font-semibold">Create Project</h2>
            <div className="mb-4">
              <label
                htmlFor="project-name"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Name
              </label>
              <input
                id="project-name"
                type="text"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="My project"
              />
            </div>
            <div className="mb-4">
              <label
                htmlFor="project-desc"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Description
              </label>
              <textarea
                id="project-desc"
                rows={3}
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="What is this project about?"
              />
            </div>
            <button
              type="submit"
              disabled={creating || !form.name.trim()}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {creating ? "Creating..." : "Create"}
            </button>
          </form>
        )}

        {loading ? (
          <LoadingSkeleton />
        ) : projects.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <p className="text-gray-500">No projects yet.</p>
            <button
              onClick={() => setShowForm(true)}
              className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              Create your first project
            </button>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <div
                key={p.id}
                className="group rounded-lg border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
              >
                <Link to={`/projects/${p.id}`}>
                  <h3 className="font-semibold text-gray-900 group-hover:text-blue-600">{p.name}</h3>
                  {p.description && (
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                      {p.description}
                    </p>
                  )}
                  <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
                    <span>
                      {p.document_count}{" "}
                      {p.document_count === 1 ? "document" : "documents"}
                    </span>
                    <span>Updated {formatDate(p.updated_at)}</span>
                  </div>
                </Link>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <Link
                    to={`/projects/${p.id}/query`}
                    className="text-sm font-medium text-blue-600 hover:text-blue-700"
                  >
                    Query &amp; Analyze
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="animate-pulse rounded-lg border border-gray-200 bg-white p-5">
          <div className="h-4 w-3/4 rounded bg-gray-200" />
          <div className="mt-3 h-3 w-full rounded bg-gray-100" />
          <div className="mt-1 h-3 w-2/3 rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}
