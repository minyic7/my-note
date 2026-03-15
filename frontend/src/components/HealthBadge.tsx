import { useEffect, useState } from "react";
import * as api from "../api";
import type { HealthStatus } from "../types";

export default function HealthBadge() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function poll() {
      try {
        const data = await api.getHealth();
        if (mounted) {
          setHealth(data);
          setError(false);
        }
      } catch {
        if (mounted) setError(true);
      }
    }

    void poll();
    const id = setInterval(poll, 30_000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  if (error) {
    return (
      <div className="flex items-center gap-2 text-xs text-red-500">
        <span className="inline-block h-2 w-2 rounded-full bg-red-500" />
        Backend unreachable
      </div>
    );
  }

  if (!health) {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span className="inline-block h-2 w-2 rounded-full bg-gray-300" />
        Checking...
      </div>
    );
  }

  const ok = health.status === "ok";

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2 text-xs font-medium">
        <span
          className={`inline-block h-2 w-2 rounded-full ${ok ? "bg-green-500" : "bg-yellow-500"}`}
        />
        <span className={ok ? "text-green-700" : "text-yellow-700"}>
          {ok ? "All systems ok" : "Degraded"}
        </span>
      </div>
      <div className="space-y-0.5 pl-4 text-xs text-gray-500">
        <div>Qdrant: {health.qdrant ? "up" : "down"}</div>
        <div>SQLite: {health.sqlite ? "up" : "down"}</div>
        <div>Agent: {health.agent_running ? "running" : "stopped"}</div>
      </div>
    </div>
  );
}
