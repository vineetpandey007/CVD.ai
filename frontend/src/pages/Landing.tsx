import { FadeIn } from "../components/FadeIn";
import { CodePanel } from "../components/CodePanel";

const PRODUCT_NAME = "Sentinel";

const heroLines = [
  { code: "def get_user(request):" },
  { code: "    user_id = request.GET['id']" },
  {
    code: '    query = "SELECT * FROM users WHERE id = " + user_id',
    finding: {
      severity: "vulnerable" as const,
      label: "SQL Injection — unsanitized string concatenation",
      cwe: "CWE-89",
      confidence: 94,
    },
  },
  { code: "    return db.execute(query)" },
];

const steps = [
  { n: "01", title: "Paste or upload", body: "Drop in a function, a file, or a diff. Python, JavaScript, Java, and C/C++ today." },
  { n: "02", title: "Dual-signal scan", body: "A fine-tuned CodeBERT checkpoint and Bandit/Semgrep's rule sets run in parallel — same code, two independent readings." },
  { n: "03", title: "Annotated report", body: 'Get a CWE-tagged, line-accurate report. Not just "this file is risky" — which line, and why.' },
];

const coverage = [
  { cwe: "CWE-89", name: "SQL Injection" },
  { cwe: "CWE-79", name: "Cross-Site Scripting" },
  { cwe: "CWE-78", name: "Command Injection" },
  { cwe: "CWE-22", name: "Path Traversal" },
  { cwe: "CWE-120", name: "Buffer Overflow" },
  { cwe: "CWE-502", name: "Insecure Deserialization" },
];

export default function Landing() {
  return (
      <main className="relative text-chalk">
      <section className="mx-auto flex min-h-[88vh] max-w-6xl flex-col justify-center gap-14 px-6 py-24 lg:flex-row lg:items-center lg:gap-10">
        <div className="flex-1">
          <FadeIn>
            <p className="font-mono text-sm text-brand">// static + neural analysis</p>
          </FadeIn>
          <FadeIn delay={120}>
            <h1 className="mt-4 font-mono text-4xl font-bold leading-[1.1] tracking-tight sm:text-5xl lg:text-6xl">
              Read the diff<br />before it reads you.
            </h1>
          </FadeIn>
          <FadeIn delay={240}>
            <p className="mt-6 max-w-md text-lg leading-relaxed text-fog">
              {PRODUCT_NAME} runs a fine-tuned language model and rule-based
              static analysis against the same code, and shows you exactly
              where — and why — they agree something's wrong.
            </p>
          </FadeIn>
          <FadeIn delay={360}>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <a href="/analyzer" className="rounded-md bg-brand px-5 py-2.5 font-mono text-sm font-medium text-ink transition hover:bg-brand/90">
                Scan a snippet →
              </a>
              <a href="https://github.com" className="font-mono text-sm text-fog underline decoration-fog/30 underline-offset-4 transition hover:text-chalk">
                View source
              </a>
            </div>
          </FadeIn>
        </div>
        <FadeIn delay={280} className="flex-1">
          <CodePanel lines={heroLines} />
        </FadeIn>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-24">
        <FadeIn><p className="font-mono text-sm text-brand">// about</p></FadeIn>
        <FadeIn delay={100}>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            Two ways of reading code, one report.
          </h2>
        </FadeIn>
        <FadeIn delay={200}>
          <p className="mt-6 text-lg leading-relaxed text-fog">
            Static analyzers know the rules — they catch the exact
            patterns they were written to catch, and nothing else. Language
            models know the patterns underneath the rules — they
            generalize, but can't point at a line number and tell you why.{" "}
            {PRODUCT_NAME} runs both: a CodeBERT checkpoint fine-tuned on
            real-world vulnerable code, cross-checked against Bandit and
            Semgrep, merged into a single line-accurate finding. Where one
            misses something subtle, the other usually catches it. It's
            open source, it runs the checkpoint as-is with no training
            step required, and every finding traces back to a specific
            line — not just a risk score for the whole file.
          </p>
        </FadeIn>
      </section>

      <section className="border-t border-white/10 bg-paper/40">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <FadeIn><p className="font-mono text-sm text-brand">// how it works</p></FadeIn>
          <div className="mt-10 grid gap-10 sm:grid-cols-3">
            {steps.map((step, i) => (
              <FadeIn key={step.n} delay={i * 120}>
                <p className="font-mono text-sm text-fog/60">{step.n}</p>
                <h3 className="mt-2 font-mono text-lg font-semibold">{step.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-fog">{step.body}</p>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-24">
        <FadeIn><p className="font-mono text-sm text-brand">// coverage</p></FadeIn>
        <FadeIn delay={100}>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight">What it's currently checking for</h2>
        </FadeIn>
        <FadeIn delay={200}>
          <div className="mt-8 flex flex-wrap gap-3">
            {coverage.map((item) => (
              <span key={item.cwe} className="flex items-center gap-2 rounded-full border border-white/10 bg-paper px-4 py-2 font-mono text-xs">
                <span className="text-fog">{item.cwe}</span>
                <span className="text-chalk/90">{item.name}</span>
              </span>
            ))}
          </div>
        </FadeIn>
      </section>

      <section className="border-t border-white/10 px-6 py-28 text-center">
        <FadeIn>
          <h2 className="font-mono text-3xl font-bold tracking-tight sm:text-4xl">Paste your first snippet.</h2>
        </FadeIn>
        <FadeIn delay={140}>
          <p className="mt-4 text-fog">Free and open source. No signup.</p>
        </FadeIn>
        <FadeIn delay={280}>
          <a href="/analyzer" className="mt-8 inline-block rounded-md bg-brand px-6 py-3 font-mono text-sm font-medium text-ink transition hover:bg-brand/90">
            Open the analyzer →
          </a>
        </FadeIn>
      </section>
    </main>
  );
}
