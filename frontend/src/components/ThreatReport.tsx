import { useState } from 'react';

interface ThreatReportProps {
  sourceCode: string;
  vulnerabilityType?: string;
  flaggedTokens?: string[];
}

export default function ThreatReport({
  sourceCode,
  vulnerabilityType = "Potential Memory / Logic Defect",
  flaggedTokens = []
}: ThreatReportProps) {
  const [report, setReport] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    if (!sourceCode.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_code: sourceCode,
          vulnerability_type: vulnerabilityType,
          lime_flagged_tokens: flaggedTokens,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || "Failed to generate report");
      }

      setReport(data.report);
    } catch (err: any) {
      setError(err.message || "Error connecting to NLG engine.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full mt-8 bg-[var(--card)] border border-[var(--border)] p-6 md:p-8 relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[var(--border)] pb-6">
        <div>
          <span className="text-[var(--accent)] font-mono text-xs font-bold tracking-[0.2em] uppercase block mb-1">
            Seq2Seq NLG Pipeline
          </span>
          <h3 className="text-xl font-bold text-[var(--foreground)] tracking-tight uppercase">
            Executive Security Audit Report
          </h3>
        </div>

        <button
          onClick={generateReport}
          disabled={loading || !sourceCode.trim()}
          className="px-6 py-3 bg-[var(--accent)] text-[var(--background)] font-bold text-xs uppercase tracking-widest transition-all hover:opacity-90 disabled:opacity-50 cursor-pointer"
        >
          {loading ? "Synthesizing Audit..." : "Generate AI Audit Report →"}
        </button>
      </div>

      {error && (
        <div className="mt-6 p-4 border border-red-500/50 bg-red-500/10 text-red-400 font-mono text-xs">
          [NLG_ERROR]: {error}
        </div>
      )}

      {report && (
        <div className="mt-6 space-y-4 text-[var(--foreground)] text-sm md:text-base leading-relaxed whitespace-pre-wrap font-sans border-l-2 border-[var(--accent)] pl-6 py-2">
          {report}
        </div>
      )}
    </div>
  );
}