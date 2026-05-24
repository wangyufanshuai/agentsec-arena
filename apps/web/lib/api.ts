import type { Report, RunBundle, Scenario } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  scenarios: () => request<Scenario[]>("/api/scenarios"),
  runs: () => request<RunBundle[]>("/api/runs"),
  createRun: (scenarioId: string) =>
    request<RunBundle>("/api/runs", {
      method: "POST",
      body: JSON.stringify({ scenario_id: scenarioId, difficulty: "training", enable_logs: true })
    }),
  stopRun: (runId: string) => request<RunBundle>(`/api/runs/${runId}/stop`, { method: "POST" }),
  startAttacker: (runId: string) => request<RunBundle>(`/api/runs/${runId}/start-attacker`, { method: "POST" }),
  startDefender: (runId: string) => request<RunBundle>(`/api/runs/${runId}/start-defender`, { method: "POST" }),
  createReport: (runId: string) => request<Report>(`/api/runs/${runId}/report`, { method: "POST" })
};

