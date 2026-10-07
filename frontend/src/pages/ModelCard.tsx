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
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
      <Nav />
      <main className="max-w-5xl mx-auto px-6 py-12 pt-24">
        <h1 className="text-4xl font-bold mb-2">Model Card: CVD CodeBERT</h1>
        <p className="text-gray-400 mb-10">Performance metrics and evaluation details for the underlying AI engine.</p>

        {error && <div className="text-red-400 bg-red-500/10 p-4 rounded-lg mb-6">{error}</div>}

        {!data && !error ? (
          <div className="text-gray-500 animate-pulse">Loading evaluation metrics...</div>
        ) : data ? (
          <div className="space-y-10">
            
            {/* Metrics Table */}
            <section>
              <h2 className="text-2xl font-semibold mb-4 border-b border-gray-800 pb-2">Benchmark Comparison (Test Set)</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-900 border-b border-gray-800 text-gray-400 text-sm tracking-wider uppercase">
                      <th className="p-4 font-medium rounded-tl-lg">Model</th>
                      <th className="p-4 font-medium">F1 Score</th>
                      <th className="p-4 font-medium">Precision</th>
                      <th className="p-4 font-medium">Recall</th>
                      <th className="p-4 font-medium">MCC</th>
                      <th className="p-4 font-medium rounded-tr-lg">PR-AUC</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {data.metrics.map((row, i) => (
                      <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-900/50 transition-colors">
                        <td className="p-4 font-medium text-gray-200">{row.model}</td>
                        <td className="p-4 text-emerald-400 font-mono">{(row.f1).toFixed(4)}</td>
                        <td className="p-4 font-mono">{(row.precision).toFixed(4)}</td>
                        <td className="p-4 font-mono">{(row.recall).toFixed(4)}</td>
                        <td className="p-4 font-mono">{(row.mcc).toFixed(4)}</td>
                        <td className="p-4 font-mono">{(row.pr_auc).toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Confidence Intervals */}
            <section>
              <h2 className="text-2xl font-semibold mb-4 border-b border-gray-800 pb-2">Statistical Reliability</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-900 p-5 rounded-lg border border-gray-800">
                  <div className="text-sm text-gray-500 uppercase tracking-wide mb-1">CodeBERT F1 (95% CI)</div>
                  <div className="text-xl font-mono text-gray-200">
                    [{data.bootstrap_ci?.codebert_f1_95ci[0].toFixed(4)}, {data.bootstrap_ci?.codebert_f1_95ci[1].toFixed(4)}]
                  </div>
                </div>
                <div className="bg-gray-900 p-5 rounded-lg border border-gray-800">
                  <div className="text-sm text-gray-500 uppercase tracking-wide mb-1">CodeBERT MCC (95% CI)</div>
                  <div className="text-xl font-mono text-gray-200">
                    [{data.bootstrap_ci?.codebert_mcc_95ci[0].toFixed(4)}, {data.bootstrap_ci?.codebert_mcc_95ci[1].toFixed(4)}]
                  </div>
                </div>
              </div>
            </section>

            {/* Limitations */}
            <section>
              <h2 className="text-2xl font-semibold mb-4 border-b border-gray-800 pb-2">Known Limitations</h2>
              <ul className="list-disc pl-5 space-y-2 text-gray-400">
                {data.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </section>

          </div>
        ) : null}
      </main>
    </div>
  );
}