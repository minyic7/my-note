import type {
  Project,
  Document,
  CreateProjectRequest,
  IngestUrlRequest,
  IngestTextRequest,
  HealthStatus,
  QueryResponse,
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

// Project APIs
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

export function getHealth(): Promise<HealthStatus> {
  return request("/health");
}

// Query APIs
export async function submitQuery(
  projectId: string,
  question: string,
): Promise<QueryResponse> {
  return request<QueryResponse>(`/projects/${projectId}/query`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function streamQuery(
  projectId: string,
  question: string,
  onChunk: (text: string) => void,
  onDone: (full: QueryResponse) => void,
  onError: (err: Error) => void,
): AbortController {
  const controller = new AbortController();

  fetch(`${BASE}/projects/${projectId}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ question }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        throw new Error(`API ${res.status}: ${await res.text().catch(() => res.statusText)}`);
      }

      const contentType = res.headers.get("content-type") ?? "";

      // If server doesn't support streaming, fall back to JSON
      if (!contentType.includes("text/event-stream")) {
        const data = (await res.json()) as QueryResponse;
        onChunk(data.answer);
        onDone(data);
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let fullResponse: QueryResponse | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data) as { chunk?: string; result?: QueryResponse };
              if (parsed.chunk) onChunk(parsed.chunk);
              if (parsed.result) fullResponse = parsed.result;
            } catch {
              // Skip unparseable lines
            }
          }
        }
      }

      if (fullResponse) {
        onDone(fullResponse);
      }
    })
    .catch((err: unknown) => {
      if (err instanceof Error && err.name !== "AbortError") {
        onError(err);
      }
    });

  return controller;
}
