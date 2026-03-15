export interface Project {
  id: string;
  name: string;
  description: string;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  source_type: "file" | "url" | "text";
  status: "pending" | "processing" | "completed" | "failed";
  error?: string;
  chunk_count: number;
  created_at: string;
}

export interface CreateProjectRequest {
  name: string;
  description: string;
}

export interface IngestUrlRequest {
  url: string;
}

export interface IngestTextRequest {
  text: string;
  title: string;
}

export interface HealthStatus {
  status: string;
  qdrant: boolean;
  sqlite: boolean;
  agent_running: boolean;
}
