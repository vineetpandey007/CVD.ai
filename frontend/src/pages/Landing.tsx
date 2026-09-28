import { FadeIn } from "../components/FadeIn";
import { CodePanel } from "../components/CodePanel";
import { Eyebrow } from "../components/Eyebrow";

const PRODUCT_NAME = "Sentinel";
const EASE = "ease-[cubic-bezier(0.16,1,0.3,1)]";

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
  {
    n: "01",
    title: "Paste or upload",
    body: "Drop in a function, a file, or a diff. Python, JavaScript, Java, and C/C++ today.",
  },
  {
    n: "02",
    title: "Dual-signal scan",
    body: "A fine-tuned CodeBERT checkpoint and Bandit/Semgrep's rule sets run in parallel — same code, two independent readings.",
  },
  {
    n: "03",
    title: "Annotated report",
    body: 'Get a CWE-tagged, line-accurate report. Not just "this file is risky" — which line, and why.',
  },
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
      <section className="mx-auto flex min-h-[92vh] max-w-6xl flex-col justify-center gap-14 px-6 pb-24 pt-32 lg:flex-row lg:items-center lg:gap-10">
        <div className="flex-1">
          <FadeIn>
            <Eyebrow>Static + Neural Analysis</Eyebrow>
          </FadeIn>
          <FadeIn delay={120}>
            <h1 className="mt-4 font-serif text-5xl font-semibold leading-[1.08] tracking-tight sm:text-6xl lg:text-7xl">
              Read the diff
              <br />
              before it reads you.
            </h1>
          </FadeIn>
          <FadeIn delay={240}>
            <p className="mt-6 max-w-md font-sans text-lg leading-relaxed text-fog">
              {PRODUCT_NAME} runs a fine-tuned language model and rule-based
              static analysis against the same code, and shows you exactly
              where — and why — they agree something's wrong.
            </p>
          </FadeIn>
          <FadeIn delay={360}>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <a
                href="/analyzer"
                className={`rounded-full bg-brand px-6 py-3 font-sans text-sm font-semibold tracking-tight text-ink transition ${EASE} hover:bg-brand/90`}
              >
                Scan a snippet →
              </a>
              <a
                href="https://github.com"
                className={`font-sans text-sm text-fog underline decoration-fog/30 underline-offset-4 transition ${EASE} hover:text-chalk`}
              >
                View source
              </a>
            </div>
          </FadeIn>
        </div>
        <FadeIn delay={280} className="flex-1">
          <CodePanel lines={heroLines} />
        </FadeIn>
      </section>

      <section id="about" className="mx-auto max-w-3xl px-6 py-16">
        <FadeIn>
          <div className="glass rounded-2xl px-8 py-10 sm:px-12 sm:py-14">
            <Eyebrow>About</Eyebrow>
            <h2 className="mt-3 font-serif text-3xl font-semibold tracking-tight sm:text-4xl">
              Two ways of reading code, one report.
            </h2>
            <p className="mt-6 font-sans text-lg leading-relaxed text-fog">
              Static analyzers know the rules — they catch the exact
              patterns they were written to catch, and nothing else.
              Language models know the patterns underneath the rules — they
              generalize, but can't point at a line number and tell you
              why. {PRODUCT_NAME} runs both: a CodeBERT checkpoint
              fine-tuned on real-world vulnerable code, cross-checked
              against Bandit and Semgrep, merged into a single
              line-accurate finding.
            </p>
          </div>
        </FadeIn>
      </section>

      <section id="how-it-works" className="mx-auto max-w-5xl px-6 py-16">
        <FadeIn className="flex justify-center">
          <Eyebrow align="center">How it works</Eyebrow>
        </FadeIn>
        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {steps.map((step, i) => (
            <FadeIn key={step.n} delay={i * 120}>
              <div
                className={`glass h-full rounded-2xl px-6 py-8 transition ${EASE} hover:bg-white/[0.06]`}
              >
                <p className="font-mono text-sm text-fog/60">{step.n}</p>
                <h3 className="mt-2 font-serif text-xl font-semibold">
                  {step.title}
                </h3>
                <p className="mt-3 font-sans text-sm leading-relaxed text-fog">
                  {step.body}
                </p>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      <section id="coverage" className="mx-auto max-w-5xl px-6 py-16">
        <FadeIn>
          <div className="glass rounded-2xl px-8 py-10 sm:px-12">
            <Eyebrow>Coverage</Eyebrow>
            <h2 className="mt-3 font-serif text-2xl font-semibold tracking-tight">
              What it's currently checking for
            </h2>
            <div className="mt-8 flex flex-wrap gap-3">
              {coverage.map((item) => (
                <span
                  key={item.cwe}
                  className="glass-strong flex items-center gap-2 rounded-full px-4 py-2 font-mono text-xs"
                >
                  <span className="text-fog">{item.cwe}</span>
                  <span className="text-chalk/90">{item.name}</span>
                </span>
              ))}
            </div>
          </div>
        </FadeIn>
      </section>

      <section className="px-6 py-24 text-center">
        <FadeIn>
          <div className="glass-strong mx-auto max-w-2xl rounded-3xl px-8 py-16">
            <h2 className="font-serif text-4xl font-semibold tracking-tight">
              Paste your first snippet.
            </h2>
            <p className="mt-4 font-sans text-fog">
              Free and open source. No signup.
            </p>
            <a
              href="/analyzer"
              className={`mt-8 inline-block rounded-full bg-brand px-7 py-3 font-sans text-sm font-semibold tracking-tight text-ink transition ${EASE} hover:bg-brand/90`}
            >
              Open the analyzer →
            </a>
          </div>
        </FadeIn>
      </section>
    </main>
  );
}
