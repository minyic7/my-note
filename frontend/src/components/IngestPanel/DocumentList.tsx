import type { Document } from "../../types";

interface Props {
  documents: Document[];
}

const statusStyles: Record<Document["status"], string> = {
  pending: "bg-yellow-100 text-yellow-800",
  processing: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

const sourceLabels: Record<Document["source_type"], string> = {
  file: "File",
  url: "URL",
  text: "Text",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function DocumentList({ documents }: Props) {
  if (documents.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
        <p className="text-gray-500">No documents ingested yet.</p>
        <p className="mt-1 text-sm text-gray-400">
          Upload files, paste a URL, or enter text above.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="mb-4 text-lg font-semibold">
        Documents ({documents.length})
      </h2>
      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Name
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Source
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Status
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Chunks
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50">
                <td className="max-w-xs truncate px-4 py-3 text-sm font-medium text-gray-900">
                  {doc.filename}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {sourceLabels[doc.source_type]}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${statusStyles[doc.status]}`}
                  >
                    {doc.status}
                  </span>
                  {doc.error && (
                    <p className="mt-1 text-xs text-red-500" title={doc.error}>
                      {doc.error.length > 60
                        ? `${doc.error.slice(0, 60)}...`
                        : doc.error}
                    </p>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {doc.chunk_count}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {formatDate(doc.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
