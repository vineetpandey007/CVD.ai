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
      // FIX 1: Scroll to the top of the page before capturing to prevent clipping bugs
      window.scrollTo(0, 0); 
      
      const element = reportRef.current;
      
      const dataUrl = await toPng(element, {
        backgroundColor: '#030712',
        pixelRatio: 2, // Keep the sharp 2x resolution
      });

      // FIX 2: Use scrollHeight to capture the full length of the content
      const width = element.offsetWidth;
      const height = element.scrollHeight; 

      const pdf = new jsPDF({
        orientation: height > width ? 'portrait' : 'landscape',
        unit: 'px',
        // FIX 3: Keep the PDF format exactly matching the 1x CSS dimensions
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

  const vulnerableCount = result.functions?.filter((f: any) => f.prediction === 'Vulnerable').length || 0;
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

      <div ref={reportRef} className="bg-gray-950 p-2 sm:p-8 rounded-2xl">
        
        <div className={`p-6 rounded-xl border mb-8 ${isHighRisk ? 'bg-red-500/10 border-red-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
          <h1 className="text-2xl font-bold text-white mb-2">Security Audit Report</h1>
          <p className="text-gray-400 text-sm mb-4">Generated on {new Date().toLocaleString()}</p>
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-lg font-bold ${isHighRisk ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {isHighRisk ? `${vulnerableCount} Vulnerabilities Detected` : 'Secure - No Vulnerabilities Found'}
            </div>
            <div className="px-4 py-2 bg-gray-800 rounded-lg text-gray-300 text-sm font-medium">
              Functions Scanned: {result.functions?.length || 0}
            </div>
          </div>
        </div>

        <h2 className="text-xl font-bold text-white mb-6 border-b border-gray-800 pb-2">Function Analysis Breakdown</h2>
        
        <div className="space-y-6">
          {result.functions?.map((func: any, index: number) => (
            <div key={index} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
              <div className="p-4 bg-gray-800/50 border-b border-gray-800 flex justify-between items-center">
                <h3 className="font-mono text-blue-400 font-semibold">{func.function_name || `Function_${index + 1}`}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${func.prediction === 'Vulnerable' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                  {func.prediction} ({(func.confidence * 100).toFixed(1)}%)
                </span>
              </div>
              
              {func.prediction === 'Vulnerable' && func.lime_tokens && (
                <div className="p-6">
                  <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Threat Context (LIME)</h4>
                  <div className="bg-gray-950 p-4 rounded-lg font-mono text-sm leading-relaxed text-gray-300 border border-gray-800">
                    {func.lime_tokens.map((token: any, i: number) => (
                      <span 
                        key={i} 
                        className={token.weight > 0.1 ? 'bg-red-500/30 text-red-200 px-1 rounded' : ''}
                        title={`Weight: ${token.weight.toFixed(3)}`}
                      >
                        {token.word}{' '}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}