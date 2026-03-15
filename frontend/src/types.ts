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

export interface QueryRequest {
  question: string;
}

export interface SourceReference {
  document_id: string;
  document_title: string;
  chunk_text: string;
  relevance_score: number;
}

export interface Finding {
  id: string;
  project_id: string;
  type: "risk" | "gap" | "conflict" | "insight";
  content: string;
  severity: "high" | "medium" | "low" | null;
  source_docs: string;
  status: "open" | "acknowledged" | "resolved";
  annotation: string | null;
  created_at: string;
  updated_at: string;
}

export interface Entity {
  id: string;
  project_id: string;
  name: string;
  type: string;
  description: string;
  first_seen: string;
  last_updated: string;
}

export interface Relation {
  id: string;
  project_id: string;
  from_entity: string;
  to_entity: string;
  relation: string;
  source_doc: string;
  confidence: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceReference[];
  findings: Finding[];
  entities: Entity[];
  relations: Relation[];
}

export interface QueryHistoryEntry {
  id: string;
  question: string;
  answer: string;
  sources: SourceReference[];
  findings: Finding[];
  entities: Entity[];
  relations: Relation[];
  timestamp: string;
}
