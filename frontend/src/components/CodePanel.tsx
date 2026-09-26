interface Finding {
  severity: "vulnerable" | "clear";
  label: string;
  cwe?: string;
  confidence?: number;
}

interface CodeLine {
  code: string;
  finding?: Finding;
}

interface CodePanelProps {
  lines: CodeLine[];
  filename?: string;
}

/**
 * Renders a small line-numbered code block with inline finding markers.
 * Used on the landing page hero and reusable on the Results page for the
 * real scan output — same visual language both places, deliberately.
 */
export function CodePanel({ lines, filename = "views.py" }: CodePanelProps) {
  const findings = lines.filter((l) => l.finding);

  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-paper shadow-2xl shadow-black/40">
      <div className="flex items-center gap-2 border-b border-white/10 px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-signal-red/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-brand/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-signal-green/70" />
        <span className="ml-2 font-mono text-xs text-fog">{filename}</span>
      </div>

      <div className="px-2 py-3">
        {lines.map((line, i) => (
          <div
            key={i}
            className={`flex items-start gap-3 rounded px-2 py-1 font-mono text-[13px] leading-6 ${
              line.finding?.severity === "vulnerable"
                ? "border-l-2 border-signal-red bg-signal-red/[0.07]"
                : line.finding?.severity === "clear"
                ? "border-l-2 border-signal-green bg-signal-green/[0.06]"
                : "border-l-2 border-transparent"
            }`}
          >
            <span className="w-5 shrink-0 select-none text-right text-fog/50">
              {i + 1}
            </span>
            <span className="whitespace-pre text-chalk/90">{line.code}</span>
          </div>
        ))}
      </div>

      {findings.length > 0 && (
        <div className="space-y-2 border-t border-white/10 bg-black/20 px-4 py-3">
          {findings.map((f, i) => (
            <div
              key={i}
              className="flex flex-wrap items-center gap-2 font-mono text-xs"
            >
              <span
                className={`rounded-full px-2 py-0.5 ${
                  f.severity === "vulnerable"
                    ? "bg-signal-red/15 text-signal-red"
                    : "bg-signal-green/15 text-signal-green"
                }`}
              >
                {f.severity === "vulnerable" ? "flagged" : "clear"}
              </span>
              {f.cwe && <span className="text-fog">{f.cwe}</span>}
              <span className="text-chalk/70">{f.label}</span>
              {f.confidence != null && (
                <span className="text-fog">
                  · model {f.confidence}% confident
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}