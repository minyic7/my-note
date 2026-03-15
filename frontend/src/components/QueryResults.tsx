import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Entity, Finding, Relation, SourceReference } from "../types";
import FindingsPanel from "./FindingsPanel";
import EntitiesPanel from "./EntitiesPanel";
import SourcesPanel from "./SourcesPanel";

interface Props {
  answer: string;
  sources: SourceReference[];
  findings: Finding[];
  entities: Entity[];
  relations: Relation[];
  streaming?: boolean;
}

export default function QueryResults({
  answer,
  sources,
  findings,
  entities,
  relations,
  streaming,
}: Props) {
  const hasFindings = findings.length > 0;
  const hasEntities = entities.length > 0 || relations.length > 0;
  const hasSources = sources.length > 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Answer */}
      <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-a:text-blue-600 prose-code:rounded prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:text-sm prose-pre:bg-gray-900 prose-pre:text-gray-100">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
        </div>
        {streaming && <StreamingCursor />}
      </section>

      {/* Findings */}
      {hasFindings && <FindingsPanel findings={findings} />}

      {/* Entities & Relations */}
      {hasEntities && <EntitiesPanel entities={entities} relations={relations} />}

      {/* Sources */}
      {hasSources && <SourcesPanel sources={sources} />}
    </div>
  );
}

function StreamingCursor() {
  return (
    <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse rounded-sm bg-blue-500" />
  );
}
