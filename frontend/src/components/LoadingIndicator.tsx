export default function LoadingIndicator() {
  return (
    <div className="mx-auto flex max-w-3xl items-center gap-3 rounded-lg border border-blue-100 bg-blue-50 p-4">
      <svg
        className="h-5 w-5 animate-spin text-blue-500"
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      <div>
        <p className="text-sm font-medium text-blue-700">Analyzing your question...</p>
        <p className="text-xs text-blue-500">
          Searching documents, identifying patterns, and generating insights.
        </p>
      </div>
    </div>
  );
}
