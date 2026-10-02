import { useLocation, Link } from "react-router-dom";

import { CodePanel } from "../components/CodePanel";
import type { AnalyzeResponse, Finding } from "../types/report";

type ResultsLocationState = {
  result?: unknown;
  code?: unknown;
  language?: unknown;
} | null;

type StaticSource = Exclude<Finding["source"], "model">;

const STATIC_SOURCES: StaticSource[] = [
  "bandit",
  "semgrep",
  "ruff",
  "flawfinder",
  "cppcheck",
  "njsscan",
];

const SOURCE_NAMES: Record<StaticSource, string> = {
  bandit: "Bandit",
  semgrep: "Semgrep",
  ruff: "Ruff",
  flawfinder: "Flawfinder",
  cppcheck: "Cppcheck",
  njsscan: "njsscan",
};

const CWE_NAMES: Record<string, string> = {
  "CWE-79": "Cross-site scripting (XSS)",
  "CWE-89": "SQL injection",
  "CWE-120": "Classic buffer overflow",
};

const LANGUAGE_EXTENSIONS: Record<string, string> = {
  python: "py",
  javascript: "js",
  java: "java",
  c: "c",
  cpp: "cpp",
};

function isFinding(value: unknown): value is Finding {
  if (typeof value !== "object" || value === null) return false;
  const finding = value as Record<string, unknown>;
  return (
    (finding.line === null || typeof finding.line === "number") &&
    (finding.severity === "vulnerable" || finding.severity === "clear") &&
    typeof finding.label === "string" &&
    (finding.cwe === null || typeof finding.cwe === "string") &&
    (finding.confidence === null || typeof finding.confidence === "number") &&
    (finding.source === "model" ||
      STATIC_SOURCES.some((source) => source === finding.source))
  );
}

function isAnalyzeResponse(value: unknown): value is AnalyzeResponse {
  if (typeof value !== "object" || value === null) return false;
  const result = value as Record<string, unknown>;
  return (
    typeof result.vulnerable === "boolean" &&
    typeof result.overall_confidence === "number" &&
    Array.isArray(result.findings) &&
    result.findings.every(isFinding) &&
    typeof result.scan_id === "string" &&
    Array.isArray(result.analysis_warnings) &&
    result.analysis_warnings.every((warning) => typeof warning === "string")
  );
}

function formatCwe(cwe: string): string {
  const name = CWE_NAMES[cwe.toUpperCase()];
  return name ? `${cwe} · ${name}` : cwe;
}

function FindingCard({
  finding,
  informational = false,
}: {
  finding: Finding;
  informational?: boolean;
}) {
  return (
    <li
      className={`rounded-xl border border-white/10 px-5 py-4 ${
        informational
          ? "bg-white/[0.03]"
          : finding.severity === "vulnerable"
            ? "bg-signal-red/[0.04]"
            : "bg-signal-green/[0.04]"
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`rounded-full px-3 py-1 font-sans text-xs font-medium uppercase tracking-wider ${
            informational
              ? "bg-white/[0.07] text-fog"
              : finding.severity === "vulnerable"
                ? "bg-signal-red/15 text-signal-red"
                : "bg-signal-green/15 text-signal-green"
          }`}
        >
          {informational
            ? "Informational"
            : finding.severity === "vulnerable"
              ? "Vulnerable"
              : "Clear"}
        </span>
        {(!informational || finding.line != null) && (
          <span className="font-mono text-sm text-fog">
            {finding.line == null ? "Line unavailable" : `Line ${finding.line}`}
          </span>
        )}
        {finding.cwe && (
          <span className="font-mono text-sm text-fog">{formatCwe(finding.cwe)}</span>
        )}
        {informational && finding.confidence != null && (
          <span className="font-mono text-sm text-fog">
            Model score: {(finding.confidence * 100).toFixed(1)}%
          </span>
        )}
      </div>
      <p className="mt-3 font-sans text-base leading-relaxed text-chalk">
        {finding.label}
      </p>
    </li>
  );
}

export default function Results() {
  const location = useLocation();
  const state = location.state as ResultsLocationState;
  const result = isAnalyzeResponse(state?.result) ? state.result : null;

  if (!result) {
    return (
      <main className="relative flex min-h-[92vh] items-center justify-center px-6 pb-24 pt-32 text-chalk">
        <section className="glass w-full max-w-3xl rounded-2xl px-8 py-10 sm:px-12">
          <h1 className="font-serif text-3xl font-semibold tracking-tight sm:text-4xl">
            This scan is no longer available. Run a new analysis.
          </h1>
          <Link
            to="/analyzer"
            className="mt-6 inline-flex rounded-full bg-brand px-6 py-3 font-sans text-sm font-semibold text-ink transition hover:bg-brand/90"
          >
            Run a new analysis
          </Link>
        </section>
      </main>
    );
  }

  const staticFindings = result.findings.filter(
    (finding) => finding.source !== "model",
  );
  const modelFindings = result.findings.filter(
    (finding) => finding.source === "model",
  );
  const groupedFindings = STATIC_SOURCES.map((source) => ({
    source,
    findings: staticFindings.filter((finding) => finding.source === source),
  }));
  const warnings = result.analysis_warnings;
  const confidence = Math.round(result.overall_confidence * 100);
  const code = typeof state?.code === "string" ? state.code : null;
  const language =
    typeof state?.language === "string" ? state.language : "source";
  const codeLines = code?.split("\n").map((line, index) => {
    const finding = staticFindings.find((item) => item.line === index + 1);
    return {
      code: line,
      ...(finding
        ? {
            finding: {
              severity: finding.severity,
              label: finding.label,
              ...(finding.cwe ? { cwe: finding.cwe } : {}),
            },
          }
        : {}),
    };
  });

  return (
    <main className="relative min-h-[92vh] px-6 pb-24 pt-32 text-chalk">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        {warnings.length > 0 && (
          <section
            role="alert"
            className="glass rounded-2xl border border-brand/40 bg-brand/[0.08] p-6 sm:p-8"
          >
            <h2 className="font-sans text-sm font-semibold uppercase tracking-wider text-brand">
              Some analysis tools did not finish
            </h2>
            <ul className="mt-3 space-y-1 font-sans text-base leading-relaxed text-chalk/90">
              {warnings.map((warning, index) => (
                <li key={`${warning}-${index}`}>{warning}</li>
              ))}
            </ul>
          </section>
        )}

        <section
          className={`glass rounded-2xl border p-6 sm:p-8 ${
            result.vulnerable
              ? "border-signal-red/40 bg-signal-red/[0.06]"
              : warnings.length > 0
                ? "border-brand/30"
                : "border-signal-green/30 bg-signal-green/[0.04]"
          }`}
        >
          <p className="font-sans text-xs font-medium uppercase tracking-[0.18em] text-fog">
            Analysis verdict
          </p>
          <h1
            className={`mt-2 font-serif text-5xl font-semibold tracking-tight sm:text-6xl ${
              result.vulnerable
                ? "text-signal-red"
                : warnings.length > 0
                  ? "text-chalk"
                  : "text-signal-green"
            }`}
          >
            {result.vulnerable
              ? "Vulnerable"
              : warnings.length > 0
                ? "No issues found by the tools that completed"
                : "No issues found"}
          </h1>
          <p className="mt-3 font-sans text-lg text-chalk/80">
            Overall confidence:{" "}
            <span className="font-medium text-chalk">{confidence}%</span>
          </p>
        </section>

        {staticFindings.length === 0 && (
          <section className="glass rounded-2xl p-6 sm:p-8">
            <h2 className="font-serif text-2xl font-semibold sm:text-3xl">
              No static-analysis findings
            </h2>
            <p className="mt-2 font-sans text-base leading-relaxed text-fog">
              No static-analysis findings were returned. Coverage is limited:
              testing found patterns missed by the available free rules.
            </p>
          </section>
        )}

        {staticFindings.length > 0 && (
          <section className="glass rounded-2xl p-6 sm:p-8">
            <div>
              <h2 className="font-serif text-2xl font-semibold sm:text-3xl">
                Static-analysis findings
              </h2>
              <p className="mt-2 font-sans text-base leading-relaxed text-fog">
                These findings count toward the verdict.
              </p>
            </div>
            <div className="mt-6 space-y-6">
              {groupedFindings.map(
                ({ source, findings }) =>
                  findings.length > 0 && (
                    <section key={source}>
                      <h3 className="mb-3 font-sans text-xs font-medium uppercase tracking-[0.18em] text-fog">
                        {SOURCE_NAMES[source]}
                      </h3>
                      <ul className="flex flex-col gap-3">
                        {findings.map((finding, index) => (
                          <FindingCard
                            key={`${source}-${finding.line}-${index}`}
                            finding={finding}
                          />
                        ))}
                      </ul>
                    </section>
                  ),
              )}
            </div>
          </section>
        )}

        {modelFindings.length > 0 && (
          <section className="glass rounded-2xl border border-white/10 p-6 sm:p-8">
            <h2 className="font-serif text-2xl font-semibold sm:text-3xl text-chalk">
              Model signal (informational)
            </h2>
            <p className="mt-2 font-sans text-base leading-relaxed text-fog">
              The model’s score is not used for the verdict and only reflects
              roughly the first 512 tokens of the input.
            </p>
            <ul className="mt-5 flex flex-col gap-3">
              {modelFindings.map((finding, index) => (
                <FindingCard
                  key={`model-${finding.line}-${index}`}
                  finding={finding}
                  informational
                />
              ))}
            </ul>
          </section>
        )}

        {codeLines && (
          <section>
            <h2 className="mb-3 font-serif text-2xl font-semibold tracking-tight">
              Scanned code
            </h2>
            <CodePanel
              lines={codeLines}
              filename={`input.${LANGUAGE_EXTENSIONS[language] ?? language}`}
            />
          </section>
        )}

        <div className="flex flex-wrap items-center justify-between gap-4 border-t border-white/10 pt-6">
          <p className="font-mono text-sm text-fog">
            Scan ID: <span className="break-all">{result.scan_id}</span>
          </p>
          <Link
            to="/analyzer"
            className="rounded-full bg-brand px-7 py-3 font-sans text-base font-medium text-ink transition hover:bg-brand/90"
          >
            Scan another
          </Link>
        </div>
      </div>
    </main>
  );
}
