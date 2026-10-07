import { useLocation, Link, Navigate } from 'react-router-dom';
import type { AnalyzeResponse } from '../types/report';
import Nav from '../components/Nav';

export default function Results() {
  const location = useLocation();
  const result = location.state?.result as AnalyzeResponse;

  if (!result) {
    return <Navigate to="/analyze" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
      <Nav />
      <main className="max-w-5xl mx-auto px-6 py-12 pt-24">
        
        {/* Header Section */}
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold mb-4 tracking-tight">Analysis Complete</h1>
          {result.vulnerable ? (
            <div className="inline-block px-6 py-3 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-lg font-medium shadow-[0_0_30px_rgba(239,68,68,0.15)]">
              ⚠️ Vulnerabilities Detected (Max Confidence: {(result.overall_confidence * 100).toFixed(1)}%)
            </div>
          ) : (
            <div className="inline-block px-6 py-3 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-lg font-medium shadow-[0_0_30px_rgba(16,185,129,0.15)]">
              ✅ No Vulnerabilities Detected (Max Confidence: {(result.overall_confidence * 100).toFixed(1)}%)
            </div>
          )}
        </div>

        {/* Function Slices */}
        <div className="space-y-6 mb-12">
          <h2 className="text-2xl font-semibold mb-4 border-b border-gray-800 pb-2">Function-Level Breakdown</h2>
          {result.functions.map((fn, idx) => {
            const isVuln = fn.probability >= result.model_info.threshold;
            return (
              <div key={idx} className={`p-6 rounded-xl border ${isVuln ? 'border-red-500/30 bg-red-500/5' : 'border-gray-800 bg-gray-900'} relative overflow-hidden`}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-mono font-semibold text-gray-200">{fn.name}()</h3>
                    <p className="text-sm text-gray-500 mt-1">Lines: {fn.start_line} - {fn.end_line}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-2xl font-bold ${isVuln ? 'text-red-400' : 'text-emerald-400'}`}>
                      {(fn.probability * 100).toFixed(1)}%
                    </span>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Vuln Probability</p>
                  </div>
                </div>

                {/* Probability Bar */}
                <div className="w-full h-2 bg-gray-800 rounded-full mt-4">
                  <div 
                    className={`h-full rounded-full ${isVuln ? 'bg-red-500' : 'bg-emerald-500'}`} 
                    style={{ width: `${fn.probability * 100}%` }}
                  />
                </div>

                {/* Truncation Warning */}
                {fn.truncated && (
                  <div className="mt-4 text-xs text-amber-400 bg-amber-400/10 p-2 rounded inline-block">
                    ⚠️ Function exceeds 512 tokens. Model applied head+tail truncation.
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Model Metadata Footer */}
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800 flex flex-col sm:flex-row justify-between items-center text-sm text-gray-400">
          <div>
            <span className="font-semibold text-gray-300">AI Engine:</span> {result.model_info.checkpoint}
          </div>
          <div>
            <span className="font-semibold text-gray-300">Decision Threshold:</span> {result.model_info.threshold}
          </div>
          <div>
            <span className="font-semibold text-gray-300">Test F1:</span> {(result.model_info.test_f1 * 100).toFixed(1)}%
          </div>
          <Link to="/model" className="text-blue-400 hover:text-blue-300 transition-colors">
            View Model Card &rarr;
          </Link>
        </div>

      </main>
    </div>
  );
}