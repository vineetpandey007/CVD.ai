import { useLocation, useNavigate } from 'react-router-dom';
import { useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const reportRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  const result = location.state?.result;

  if (!result) {
    return (
      <main className="max-w-4xl w-full mx-auto px-6 py-32 flex-grow text-center">
        <h2 className="text-2xl font-bold text-white mb-4">No analysis data found.</h2>
        <button onClick={() => navigate('/analyzer')} className="text-blue-500 hover:text-blue-400">
          &larr; Return to Analyzer
        </button>
      </main>
    );
  }

  const handleExportPDF = async () => {
    if (!reportRef.current) return;
    setIsExporting(true);

    try {
      window.scrollTo(0, 0); 
      
      const element = reportRef.current;
      
      const dataUrl = await toPng(element, {
        backgroundColor: '#030712',
        pixelRatio: 2, 
      });

      const width = element.offsetWidth;
      const height = element.scrollHeight; 

      const pdf = new jsPDF({
        orientation: height > width ? 'portrait' : 'landscape',
        unit: 'px',
        format: [width, height] 
      });

      pdf.addImage(dataUrl, 'PNG', 0, 0, width, height);
      pdf.save(`CVD_Audit_Report_${new Date().getTime()}.pdf`);
    } catch (error) {
      console.error("PDF Export failed:", error);
    } finally {
      setIsExporting(false);
    }
  };

  const threshold = typeof result.model_info?.threshold === 'number' ? result.model_info.threshold : 0.5;
  const functions = Array.isArray(result.functions) ? result.functions : [];
  const vulnerableCount = functions.filter((f: any) => (f.probability ?? 0) >= threshold).length;
  const isHighRisk = vulnerableCount > 0;

  return (
    <main className="max-w-5xl w-full mx-auto px-4 sm:px-6 py-12 pt-28 flex-grow">
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <button onClick={() => navigate('/analyzer')} className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
          &larr; New Scan
        </button>
        <button
          onClick={handleExportPDF}
          disabled={isExporting}
          className="bg-gray-800 hover:bg-gray-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold border border-gray-700 transition-all shadow-sm disabled:opacity-50 flex items-center gap-2"
        >
          {isExporting ? 'Generating PDF...' : '📄 Export Security Audit'}
        </button>
      </div>

      <div ref={reportRef} className="bg-gray-950 p-4 sm:p-8 rounded-2xl border border-gray-900">
        
        <div className={`p-6 rounded-xl border mb-8 ${isHighRisk ? 'bg-red-500/10 border-red-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
          <h1 className="text-2xl font-bold text-white mb-2">Security Audit Report</h1>
          <p className="text-gray-400 text-sm mb-4">Generated on {new Date().toLocaleString()}</p>
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-lg font-bold ${isHighRisk ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {isHighRisk ? `${vulnerableCount} Vulnerabilities Detected` : 'Secure - No Vulnerabilities Found'}
            </div>
            <div className="px-4 py-2 bg-gray-800 rounded-lg text-gray-300 text-sm font-medium">
              Functions Scanned: {functions.length}
            </div>
          </div>
        </div>

        <h2 className="text-xl font-bold text-white mb-6 border-b border-gray-800 pb-2">Function Analysis Breakdown</h2>
        
        <div className="space-y-6">
          {functions.map((func: any, index: number) => {
            const prob = typeof func.probability === 'number' ? func.probability : 0;
            const isVulnerable = prob >= threshold;

            return (
              <div key={index} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
                <div className="p-4 bg-gray-800/50 border-b border-gray-800 flex justify-between items-center">
                  <h3 className="font-mono text-blue-400 font-semibold">{func.name || `Function_${index + 1}`}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${isVulnerable ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {isVulnerable ? 'Vulnerable' : 'Secure'} ({(prob * 100).toFixed(1)}%)
                  </span>
                </div>
                
                {/* Explainability Breakdown */}
                {isVulnerable && Array.isArray(func.line_scores) && func.line_scores.length > 0 && (
                  <div className="p-6">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Threat Context (Suspicious Lines)</h4>
                    <div className="space-y-2">
                      {func.line_scores.map((item: any, i: number) => {
                        let line: any = undefined;
                        let score = 0;
                        let content = '';

                        if (Array.isArray(item)) {
                          line = item[0];
                          score = typeof item[1] === 'number' ? item[1] : 0;
                        } else if (typeof item === 'object' && item !== null) {
                          line = item.line ?? item.line_num ?? item.line_number;
                          score = typeof item.score === 'number' ? item.score : (typeof item.weight === 'number' ? item.weight : 0);
                          content = item.code ?? item.text ?? item.word ?? '';
                        }

                        return (
                          <div key={i} className="flex items-center justify-between bg-gray-950 px-3 py-2 rounded-lg border border-gray-800 text-xs font-mono">
                            <div className="flex items-center gap-2 overflow-hidden">
                              {line !== undefined && (
                                <span className="text-blue-400 font-semibold shrink-0">Line {line}:</span>
                              )}
                              {content ? (
                                <span className="text-gray-300 truncate">{content}</span>
                              ) : (
                                <span className="text-gray-500 italic">Flagged code segment</span>
                              )}
                            </div>
                            <span className={`px-2 py-0.5 rounded text-[11px] font-bold shrink-0 ml-3 ${score > 0.2 ? 'bg-red-500/20 text-red-400' : 'bg-gray-800 text-gray-400'}`}>
                              {(score * 100).toFixed(1)}% Suspicious
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}