export type Finding = {
  line: number | null;
  severity: "vulnerable" | "clear";
  label: string;
  cwe: string | null;
  confidence: number | null;
  source: "model" | "bandit" | "semgrep";
};

export type AnalyzeResponse = {
  vulnerable: boolean;
  overall_confidence: number;
  findings: Finding[];
  scan_id: string;
};
