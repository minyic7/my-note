import type { Entity, Relation } from "../types";

interface Props {
  entities: Entity[];
  relations: Relation[];
}

const ENTITY_TYPE_COLORS: Record<string, string> = {
  person: "bg-purple-100 text-purple-800",
  organization: "bg-green-100 text-green-800",
  location: "bg-teal-100 text-teal-800",
  concept: "bg-indigo-100 text-indigo-800",
  technology: "bg-cyan-100 text-cyan-800",
  event: "bg-pink-100 text-pink-800",
};

function typeColor(type: string): string {
  return ENTITY_TYPE_COLORS[type.toLowerCase()] ?? "bg-gray-100 text-gray-700";
}

export default function EntitiesPanel({ entities, relations }: Props) {
  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
        Entities &amp; Relationships
      </h3>

      {/* Entities as cards */}
      {entities.length > 0 && (
        <div className="mb-4 grid gap-2 sm:grid-cols-2">
          {entities.map((entity) => (
            <div
              key={entity.id}
              className="rounded-lg border border-gray-200 bg-white p-3"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{entity.name}</span>
                <span
                  className={`rounded px-1.5 py-0.5 text-xs font-medium ${typeColor(entity.type)}`}
                >
                  {entity.type}
                </span>
              </div>
              {entity.description && (
                <p className="mt-1 text-sm text-gray-600">{entity.description}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Relations as a list */}
      {relations.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white">
          <div className="border-b border-gray-100 px-3 py-2">
            <span className="text-xs font-medium text-gray-500">Relationships</span>
          </div>
          <ul className="divide-y divide-gray-100">
            {relations.map((rel) => (
              <li key={rel.id} className="flex items-center gap-2 px-3 py-2 text-sm">
                <span className="font-medium text-gray-800">{rel.from_entity}</span>
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600">
                  {rel.relation}
                </span>
                <span className="font-medium text-gray-800">{rel.to_entity}</span>
                {rel.confidence < 1 && (
                  <span className="ml-auto text-xs text-gray-400">
                    {Math.round(rel.confidence * 100)}%
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
