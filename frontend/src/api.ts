import type {
  Project,
  Document,
  CreateProjectRequest,
  IngestUrlRequest,
  IngestTextRequest,
} from "./types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
      ...(!init?.body || init.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function listProjects(): Promise<Project[]> {
  return request("/projects");
}

export function getProject(id: string): Promise<Project> {
  return request(`/projects/${id}`);
}

export function createProject(body: CreateProjectRequest): Promise<Project> {
  return request("/projects", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function listDocuments(projectId: string): Promise<Document[]> {
  return request(`/projects/${projectId}/documents`);
}

export function ingestFiles(
  projectId: string,
  files: File[],
): Promise<Document[]> {
  const form = new FormData();
  for (const f of files) {
    form.append("files", f);
  }
  return request(`/projects/${projectId}/ingest`, {
    method: "POST",
    body: form,
  });
}

export function ingestUrl(
  projectId: string,
  body: IngestUrlRequest,
): Promise<Document> {
  return request(`/projects/${projectId}/ingest/url`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function ingestText(
  projectId: string,
  body: IngestTextRequest,
): Promise<Document> {
  return request(`/projects/${projectId}/ingest/text`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
