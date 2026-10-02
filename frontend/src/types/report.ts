export type Finding = {
  line: number | null;
  severity: "vulnerable" | "clear";
  label: string;
  cwe: string | null;
  confidence: number | null;
  source:
    | "model"
    | "bandit"
    | "semgrep"
    | "ruff"
    | "flawfinder"
    | "cppcheck"
    | "njsscan";
};

export type AnalyzeResponse = {
  vulnerable: boolean;
  overall_confidence: number;
  findings: Finding[];
  scan_id: string;
  analysis_warnings: string[];
};
