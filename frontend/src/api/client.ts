import type { AnalyzeResponse, ModelCardData } from '../types/report';

const API_BASE = 'http://127.0.0.1:8000/api';

export async function analyzeCode(code: string, language: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language })
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Analysis failed. Make sure the backend is running.');
  }
  
  return res.json();
}

export async function fetchModelCard(): Promise<ModelCardData> {
  const res = await fetch(`${API_BASE}/model-card`);
  if (!res.ok) throw new Error('Failed to fetch model card data');
  return res.json();
}