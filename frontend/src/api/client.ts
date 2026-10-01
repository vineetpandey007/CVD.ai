import type { AnalyzeResponse } from "../types/report";

export type Language = "python" | "javascript" | "java" | "c" | "cpp";

export type CweBreakdownItem = {
  cwe: string | null;
  source: string;
  count: number;
};

export type TimelineItem = {
  scan_id: string;
  language: Language;
  vulnerable: boolean;
  overall_confidence: number;
  created_at: string;
};

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export function analyzeCode(
  code: string,
  language: Language,
): Promise<AnalyzeResponse> {
  return fetchJson<AnalyzeResponse>("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language }),
  });
}

export function getCweBreakdown(): Promise<CweBreakdownItem[]> {
  return fetchJson<CweBreakdownItem[]>("/api/history/cwe-breakdown");
}

export function getTimeline(): Promise<TimelineItem[]> {
  return fetchJson<TimelineItem[]>("/api/history/timeline");
}
