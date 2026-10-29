import { useEffect, useState } from 'react';
import type { ModelCardData } from '../types/report';
import { fetchModelCard } from '../api/client';
import Nav from '../components/Nav';

export default function ModelCard() {
  const [data, setData] = useState<ModelCardData | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchModelCard()
      .then(setData)
      .catch(err => setError(err.message));
  }, []);

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] font-sans relative z-10 pt-32 pb-24 px-6 sm:px-12">
      <Nav />
      <main className="max-w-5xl mx-auto">
        
        {/* Header Section */}
        <div className="mb-16 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="inline-flex items-center gap-3 rounded-full border border-[var(--border)] bg-[var(--muted)] px-5 py-2 mb-6">
            <span className="h-2 w-2 rounded-full bg-[var(--accent)] animate-pulse shadow-[0_0_8px_var(--accent)]" />
            <span className="font-mono text-xs uppercase tracking-[0.15em] text-[var(--foreground)] font-medium">
              NODE_01 // ARCHITECTURE & EVALUATION
            </span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold tracking-tighter leading-[1.1] text-[var(--foreground)] mb-4">
            AI Model Card: <span className="text-[var(--accent)] font-semibold">CVD CodeBERT</span>
          </h1>
          <p className="max-w-2xl text-lg text-[var(--muted-foreground)] leading-relaxed">
            Performance metrics, benchmark comparisons, and statistical reliability for the fine-tuned transformer engine powering our static analysis pipeline.
          </p>
        </div>

        {error && (
          <div className="border border-red-900 bg-red-950/30 text-red-500 font-mono p-6 mb-8 shadow-xl">
            [SYS_ERROR]: {error}
          </div>
        )}

        {!data && !error ? (
          <div className="flex items-center gap-4 text-[var(--accent)] font-mono animate-pulse border border-[var(--border)] bg-[var(--card)] p-8 shadow-2xl">
            <span className="text-xl">⚙</span> Loading evaluation metrics and checkpoint data...
          </div>
        ) : data ? (
          <div className="space-y-16 animate-in fade-in duration-700 delay-150">
            
            {/* Metrics Table */}
            <section>
              <div className="flex items-center mb-6">
                <span className="text-[var(--accent)] font-mono text-xl mr-3">⌖</span>
                <h2 className="text-2xl font-semibold tracking-tight uppercase">Benchmark Comparison (Test Set)</h2>
              </div>
              
              <div className="bg-[var(--card)] border border-[var(--border)] shadow-2xl overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[var(--muted)] border-b border-[var(--border)] text-[var(--accent)] text-xs font-mono tracking-widest uppercase">
                      <th className="p-5 font-semibold">Model Checkpoint</th>
                      <th className="p-5 font-semibold">F1 Score</th>
                      <th className="p-5 font-semibold">Precision</th>
                      <th className="p-5 font-semibold">Recall</th>
                      <th className="p-5 font-semibold">MCC</th>
                      <th className="p-5 font-semibold">PR-AUC</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {data.metrics.map((row, i) => (
                      <tr 
                        key={i} 
                        className="border-b border-[var(--border)] hover:bg-[var(--muted)] transition-colors group cursor-default"
                      >
                        <td className="p-5 font-medium text-[var(--foreground)] flex items-center">
                          <span className="text-[var(--accent)] text-[10px] font-mono inline-block transition-all duration-300 opacity-0 group-hover:opacity-100 transform translate-x-0 group-hover:translate-x-2 mr-3">
                            ▶
                          </span>
                          {row.model}
                        </td>
                        <td className="p-5 font-mono text-[var(--foreground)]">{(row.f1).toFixed(4)}</td>
                        <td className="p-5 font-mono text-[var(--muted-foreground)] group-hover:text-[var(--foreground)] transition-colors">{(row.precision).toFixed(4)}</td>
                        <td className="p-5 font-mono text-[var(--muted-foreground)] group-hover:text-[var(--foreground)] transition-colors">{(row.recall).toFixed(4)}</td>
                        <td className="p-5 font-mono text-[var(--muted-foreground)] group-hover:text-[var(--foreground)] transition-colors">{(row.mcc).toFixed(4)}</td>
                        <td className="p-5 font-mono text-[var(--muted-foreground)] group-hover:text-[var(--foreground)] transition-colors">{(row.pr_auc).toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Confidence Intervals Grid */}
            <section>
              <div className="flex items-center mb-6">
                <span className="text-[var(--accent)] font-mono text-xl mr-3">◎</span>
                <h2 className="text-2xl font-semibold tracking-tight uppercase">Statistical Reliability</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-[var(--card)] border border-[var(--border)] p-8 transition-all duration-300 hover:border-[var(--accent)] hover:-translate-y-1 group shadow-xl">
                  <div className="text-xs font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-4">
                    [ CodeBERT F1 (95% CI) ]
                  </div>
                  {/* REMOVED font-bold, ADDED tracking-tight for sleek math aesthetics */}
                  <div className="text-3xl font-mono tracking-tight text-[var(--foreground)]">
                    [{data.bootstrap_ci?.codebert_f1_95ci[0].toFixed(4)}, {data.bootstrap_ci?.codebert_f1_95ci[1].toFixed(4)}]
                  </div>
                  <div className="mt-5 h-[2px] w-12 bg-[var(--border)] group-hover:bg-[var(--accent)] group-hover:w-full transition-all duration-500"></div>
                </div>

                <div className="bg-[var(--card)] border border-[var(--border)] p-8 transition-all duration-300 hover:border-[var(--accent)] hover:-translate-y-1 group shadow-xl">
                  <div className="text-xs font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-4">
                    [ CodeBERT MCC (95% CI) ]
                  </div>
                  {/* REMOVED font-bold, ADDED tracking-tight */}
                  <div className="text-3xl font-mono tracking-tight text-[var(--foreground)]">
                    [{data.bootstrap_ci?.codebert_mcc_95ci[0].toFixed(4)}, {data.bootstrap_ci?.codebert_mcc_95ci[1].toFixed(4)}]
                  </div>
                  <div className="mt-5 h-[2px] w-12 bg-[var(--border)] group-hover:bg-[var(--accent)] group-hover:w-full transition-all duration-500"></div>
                </div>
              </div>
            </section>

            {/* System Specs & Hyperparameters */}
            <section className="bg-[var(--card)] border border-[var(--border)] p-8 shadow-xl mt-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-32 bg-[var(--accent)] opacity-[0.02] rounded-full blur-3xl pointer-events-none"></div>
              
              <div className="flex items-center mb-8 border-b border-[var(--border)] pb-4 relative z-10">
                <span className="text-[var(--accent)] font-mono text-xl mr-3">⚙</span>
                <h2 className="text-xl font-semibold tracking-tight uppercase">System Specs & Hyperparameters</h2>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
                {/* Changed values to font-mono and standard weight for a classy readout */}
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Architecture Base</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">RoBERTa (CodeBERT)</div>
                </div>
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Fine-Tune Dataset</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">Draper / Devign</div>
                </div>
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Training Samples</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">~1.27M Functions</div>
                </div>
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Dataset Split</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">80% Train / 20% Eval</div>
                </div>
                
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Learning Rate</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">2e-5 (AdamW)</div>
                </div>
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Batch Size</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">32</div>
                </div>
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Epochs</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">10 (Stop at 7)</div>
                </div>
                <div className="p-5 border border-[var(--border)] bg-[var(--background)]/50 backdrop-blur-sm hover:border-[var(--accent)] transition-colors">
                  <div className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-[0.2em] mb-2">Max Seq Length</div>
                  <div className="text-sm font-mono text-[var(--foreground)]">512 Tokens</div>
                </div>
              </div>
            </section>

            {/* Pipeline Overview */}
            <section>
              <div className="flex items-center mb-6">
                <span className="text-[var(--accent)] font-mono text-xl mr-3">⟨/⟩</span>
                <h2 className="text-2xl font-semibold tracking-tight uppercase">Engine Integration Modules</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[var(--card)] border border-[var(--border)] p-6 shadow-xl group hover:border-[var(--accent)] transition-colors">
                  <div className="text-2xl mb-4 text-[var(--muted-foreground)] group-hover:text-[var(--accent)] transition-colors">◎</div>
                  <h3 className="font-semibold text-[var(--foreground)] mb-2 uppercase text-sm tracking-widest">LIME Explainability</h3>
                  <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">
                    Local Interpretable Model-agnostic Explanations isolate predictive logic, assigning mathematical confidence weights to specific C/C++ syntax tokens.
                  </p>
                </div>
                <div className="bg-[var(--card)] border border-[var(--border)] p-6 shadow-xl group hover:border-[var(--accent)] transition-colors">
                  <div className="text-2xl mb-4 text-[var(--muted-foreground)] group-hover:text-[var(--accent)] transition-colors">⌖</div>
                  <h3 className="font-semibold text-[var(--foreground)] mb-2 uppercase text-sm tracking-widest">ChromaDB Vectors</h3>
                  <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">
                    CodeBERT's [CLS] token outputs are mapped into a 768-dimensional space, enabling sub-millisecond semantic similarity searches for historical vulnerabilities.
                  </p>
                </div>
                <div className="bg-[var(--card)] border border-[var(--border)] p-6 shadow-xl group hover:border-[var(--accent)] transition-colors">
                  <div className="text-2xl mb-4 text-[var(--muted-foreground)] group-hover:text-[var(--accent)] transition-colors">⚙</div>
                  <h3 className="font-semibold text-[var(--foreground)] mb-2 uppercase text-sm tracking-widest">Groq LLM Synthesis</h3>
                  <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">
                    Ultra-low latency open-source LLMs (`gpt-oss-20b`) ingest LIME token arrays to synthesize C/C++ patch recommendations and executive threat summaries.
                  </p>
                </div>
              </div>
            </section>

            {/* Limitations */}
            <section className="bg-[var(--card)] border border-[var(--border)] p-8 shadow-xl">
              <div className="flex items-center mb-6 border-b border-[var(--border)] pb-4">
                <span className="text-red-500 font-mono text-xl mr-3">!</span>
                <h2 className="text-xl font-semibold tracking-tight uppercase">Known Limitations</h2>
              </div>
              <ul className="space-y-4">
                {data.limitations.map((lim, i) => (
                  <li key={i} className="flex items-start text-[var(--muted-foreground)] leading-relaxed text-sm">
                    <span className="text-red-500/80 font-mono mr-4 mt-0.5">[{i + 1}]</span>
                    {lim}
                  </li>
                ))}
              </ul>
            </section>

          </div>
        ) : null}
      </main>
    </div>
  );
}