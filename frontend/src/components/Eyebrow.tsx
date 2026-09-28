import type { ReactNode } from "react";

interface EyebrowProps {
  children: ReactNode;
  align?: "left" | "center";
}

/**
 * Small kicker label used above section headings — replaces the earlier
 * "// section" monospace comment style with a quieter, editorial
 * treatment: a thin rule plus tracked uppercase type. Monospace stays
 * reserved for content that's genuinely code/data (the CodePanel, CWE
 * tags, step numerals) — not general UI chrome like this.
 */
export function Eyebrow({ children, align = "left" }: EyebrowProps) {
  return (
    <span
      className={`inline-flex items-center gap-2 font-sans text-[11px] font-medium uppercase tracking-[0.2em] text-fog ${
        align === "center" ? "justify-center" : ""
      }`}
    >
      <span className="h-px w-4 bg-brand/50" />
      {children}
    </span>
  );
}
