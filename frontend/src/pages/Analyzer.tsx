import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { analyzeCode, type Language } from "../api/client";

const SQL_INJECTION_EXAMPLE = `def get_user(connection, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return connection.execute(query).fetchall()`;

const LANGUAGES: Language[] = ["python", "javascript", "java", "c", "cpp"];

function getErrorMessage(error: unknown): string {
  if (error instanceof TypeError) {
    return "Could not connect to the backend. Make sure the backend server is running, then try again.";
  }

  const message = error instanceof Error ? error.message : "";
  const status = message.match(/\bAPI request failed:\s*(\d{3})/i)?.[1];
  if (status === "429") {
    return "Rate limit reached. You can run up to 10 scans per minute; please wait before trying again.";
  }
  if (status) {
    return `The scan request failed (HTTP ${status}). Please try again.`;
  }
  return "The scan could not be completed. Please try again.";
}

export default function Analyzer() {
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState<Language>("python");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!code.trim() || loading) return;

    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCode(code, language);
      navigate(`/results/${encodeURIComponent(result.scan_id)}`, {
        state: { result },
      });
    } catch (scanError) {
      setError(getErrorMessage(scanError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-[92vh] items-center justify-center px-6 pb-24 pt-32 text-chalk">
      <section className="glass w-full max-w-4xl rounded-2xl px-6 py-8 sm:px-10 sm:py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.15em] text-fog">
              Static + neural analysis
            </p>
            <h1 className="mt-2 font-serif text-3xl font-semibold tracking-tight sm:text-4xl">
              Scan your code
            </h1>
          </div>
          <button
            type="button"
            onClick={() => {
              setCode(SQL_INJECTION_EXAMPLE);
              setLanguage("python");
              setError(null);
            }}
            className="font-sans text-sm text-brand underline decoration-brand/40 underline-offset-4 transition hover:text-chalk"
          >
            Load example
          </button>
        </div>

        <form className="mt-8" onSubmit={handleSubmit}>
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <label
              htmlFor="code"
              className="font-mono text-xs uppercase tracking-wider text-fog"
            >
              Source code
            </label>
            <label className="flex items-center gap-3 font-mono text-xs text-fog">
              Language
              <select
                value={language}
                onChange={(event) => setLanguage(event.target.value as Language)}
                className="glass-strong rounded-lg px-3 py-2 font-mono text-xs text-chalk outline-none focus:border-brand"
              >
                {LANGUAGES.map((item) => (
                  <option key={item} value={item} className="bg-paper text-chalk">
                    {item}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <textarea
            id="code"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="Paste code here, or load the SQL injection example…"
            spellCheck={false}
            aria-describedby="scan-status"
            className="glass-strong min-h-72 w-full resize-y rounded-xl p-4 font-mono text-sm leading-6 text-chalk placeholder:text-fog/60 outline-none transition focus:border-brand"
          />

          {error && (
            <p role="alert" className="mt-4 font-sans text-sm text-signal-red">
              {error}
            </p>
          )}

          {loading && (
            <p
              id="scan-status"
              role="status"
              className="mt-4 rounded-xl border border-brand/20 bg-brand/5 px-4 py-3 font-sans text-sm leading-relaxed text-fog"
            >
              Scan in progress. Analysis typically takes 30–40 seconds because
              static-analysis tools inspect your code. You can leave this page
               open while it runs.
            </p>
          )}

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
            <p className="font-sans text-xs text-fog">
              Up to 500 lines · Your code is not included in scan history
            </p>
            <button
              type="submit"
              disabled={loading || !code.trim()}
              className="rounded-full bg-brand px-7 py-3 font-sans text-sm font-semibold tracking-tight text-ink transition hover:bg-brand/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Scanning…" : "Scan code →"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}
