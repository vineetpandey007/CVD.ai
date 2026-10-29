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
  const [copied, setCopied] = useState(false);

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

      // Clean any residual markdown characters on the frontend as well
      const cleaned = (data.report || "")
        .replace(/```cpp/gi, "")
        .replace(/```c/gi, "")
        .replace(/```/g, "")
        .replace(/\*\*/g, "")
        .trim();

      setReport(cleaned);
    } catch (err: any) {
      setError(err.message || "Error connecting to NLG engine.");
    } finally {
      setLoading(false);
    }
  };

  // Split report into narrative bullets vs. the C/C++ patched code block
  const parseReportContent = (rawText: string) => {
    const lines = rawText.split('\n');
    const textLines: string[] = [];
    const codeLines: string[] = [];
    let inCodeSection = false;

    for (const line of lines) {
      const trimmed = line.trim();
      // Detect start of C/C++ code block (#include, void/int signature, or comment after 3. THE FIX)
      if (
        !inCodeSection &&
        (trimmed.startsWith('#include') ||
          trimmed.startsWith('//') ||
          /^(void|int|char|size_t|bool|struct|static)\s+\w+\s*\(/.test(trimmed))
      ) {
        inCodeSection = true;
      }

      if (inCodeSection) {
        codeLines.push(line);
      } else {
        textLines.push(line);
      }
    }

    return {
      textLines,
      codeBlock: codeLines.join('\n').trim(),
    };
  };

  const parsed = report ? parseReportContent(report) : null;

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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

        {/* Hidden from PDF exports via data-html2canvas-ignore and print:hidden */}
        <button
          onClick={generateReport}
          disabled={loading || !sourceCode.trim()}
          data-html2canvas-ignore="true"
          className="print:hidden px-6 py-3 bg-[var(--accent)] text-[var(--background)] font-bold text-xs uppercase tracking-widest transition-all hover:opacity-90 disabled:opacity-50 cursor-pointer"
        >
          {loading
            ? "Synthesizing Audit..."
            : report
            ? "Regenerate Audit Report ↻"
            : "Generate AI Audit Report →"}
        </button>
      </div>

      {error && (
        <div className="mt-6 p-4 border border-red-500/50 bg-red-500/10 text-red-400 font-mono text-xs">
          [NLG_ERROR]: {error}
        </div>
      )}

      {parsed && (
        <div className="mt-6 space-y-6">
          {/* Structured Executive Findings */}
          <div className="space-y-3 border-l-2 border-[var(--accent)] pl-6 py-1">
            {parsed.textLines.map((line, idx) => {
              const trimmed = line.trim();
              if (!trimmed) return null;

              const isHeader = /^(1\.|2\.|3\.)\s*(THE ISSUE|THE DANGER|THE FIX)/i.test(trimmed);

              if (isHeader) {
                return (
                  <h4
                    key={idx}
                    className="text-xs font-mono font-bold uppercase tracking-[0.15em] text-[var(--accent)] pt-3 first:pt-0"
                  >
                    {trimmed}
                  </h4>
                );
              }

              return (
                <p
                  key={idx}
                  className="text-[var(--foreground)] text-sm md:text-base leading-relaxed font-sans"
                >
                  {trimmed}
                </p>
              );
            })}
          </div>

          {/* Dedicated Monospace Terminal Box for Patched C/C++ Code */}
          {parsed.codeBlock && (
            <div className="border border-[var(--border)] bg-black/50">
              <div className="flex items-center justify-between px-4 py-2 border-b border-[var(--border)] bg-white/[0.02]">
                <span className="font-mono text-[10px] uppercase tracking-widest text-emerald-400 font-bold">
                  // Recommended Patched Implementation (C/C++)
                </span>
                <button
                  onClick={() => copyCode(parsed.codeBlock)}
                  data-html2canvas-ignore="true"
                  className="print:hidden font-mono text-[10px] uppercase tracking-wider text-[var(--foreground)] opacity-70 hover:opacity-100 cursor-pointer"
                >
                  {copied ? "[Copied]" : "[Copy Patch]"}
                </button>
              </div>
              <pre className="p-4 text-xs md:text-sm font-mono text-emerald-300/90 overflow-x-auto leading-relaxed whitespace-pre-wrap">
                <code>{parsed.codeBlock}</code>
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}