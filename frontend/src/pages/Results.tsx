import { useLocation, useNavigate } from 'react-router-dom';
import { useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';
import ThreatReport from '../components/ThreatReport';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const reportRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  const result = location.state?.result;
  const rawSourceCode = location.state?.sourceCode || '';

  if (!result) {
    return (
      <main className="max-w-4xl w-full mx-auto px-6 py-32 flex-grow text-center z-10 relative">
        <h2 className="text-2xl font-bold text-[var(--foreground)] font-mono uppercase tracking-widest mb-6">
          [SYSTEM_FAULT] No Analysis Data Found
        </h2>
        <button 
          onClick={() => navigate('/analyzer')} 
          className="px-6 py-3 bg-transparent border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:border-[var(--accent)] font-bold text-xs uppercase tracking-widest transition-all"
        >
          ← Return to Scanner
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
        backgroundColor: '#0A0A0A',
        pixelRatio: 2, 
      });

      // Standard A4 dimensions in pixels
      const pdfWidth = 794;
      const pdfHeight = 1123;

      const pdf = new jsPDF('portrait', 'px', [pdfWidth, pdfHeight]);

      const img = new Image();
      img.src = dataUrl;
      await new Promise((resolve) => { img.onload = resolve; });

      const imgWidth = pdfWidth;
      const imgHeight = (img.height * pdfWidth) / img.width;
      
      let heightLeft = imgHeight;
      let position = 0;

      // Add first page
      pdf.addImage(dataUrl, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;

      // Automatically add subsequent pages if content exceeds standard page length
      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(dataUrl, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight;
      }

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

  // Collect all flagged tokens across all vulnerable functions for the unified AI report
  const allFlaggedTokens = functions.flatMap((func: any) => {
    if (!func.line_scores) return [];
    return func.line_scores.map((item: any) => {
      if (typeof item === 'object' && item !== null) {
        return item.code ?? item.text ?? item.word ?? '';
      }
      return '';
    }).filter(Boolean);
  });

  return (
    <main className="max-w-5xl w-full mx-auto px-4 sm:px-6 py-12 pt-32 flex-grow z-10 relative">
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <button 
          onClick={() => navigate('/analyzer')} 
          className="text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors text-xs font-mono font-bold uppercase tracking-widest"
        >
          ← Initialize New Scan
        </button>
        <button
          onClick={handleExportPDF}
          disabled={isExporting}
          className="bg-[var(--foreground)] text-[var(--background)] px-6 py-3 text-xs font-bold font-mono uppercase tracking-widest transition-all disabled:opacity-50 hover:bg-[var(--accent)] hover:text-white"
        >
          {isExporting ? 'Generating PDF...' : '↓ Export Security Audit'}
        </button>
      </div>

      <div ref={reportRef} className="bg-[var(--card)] p-4 sm:p-8 border border-[var(--border)] shadow-2xl space-y-12">
        
        {/* Header Block */}
        <div className={`p-6 border ${isHighRisk ? 'bg-[var(--accent)]/10 border-[var(--accent)]' : 'bg-emerald-500/10 border-emerald-500/50'}`}>
          <h1 className="text-3xl font-black text-[var(--foreground)] uppercase tracking-tighter mb-2">
            Security Audit Report
          </h1>
          <p className="text-[var(--muted-foreground)] font-mono text-xs uppercase tracking-widest mb-6">
            Timestamp: {new Date().toLocaleString()}
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <div className={`px-4 py-2 font-bold font-mono text-xs uppercase tracking-widest border ${isHighRisk ? 'bg-[var(--accent)]/20 text-[var(--accent)] border-[var(--accent)]' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500'}`}>
              {isHighRisk ? `[CRITICAL] ${vulnerableCount} Vulnerabilities Detected` : '[SECURE] No Vulnerabilities Found'}
            </div>
            <div className="px-4 py-2 bg-[var(--background)] border border-[var(--border)] text-[var(--muted-foreground)] font-mono text-xs font-bold uppercase tracking-widest">
              Functions Scanned: {functions.length}
            </div>
          </div>
        </div>

        {/* Function Analysis Breakdown */}
        <div>
          <h2 className="text-xl font-bold text-[var(--foreground)] mb-6 border-b border-[var(--border)] pb-4 uppercase tracking-widest">
            Function Analysis Breakdown
          </h2>
          
          <div className="space-y-8">
            {functions.map((func: any, index: number) => {
              const prob = typeof func.probability === 'number' ? func.probability : 0;
              const isVulnerable = prob >= threshold;

              return (
                <div key={index} className={`bg-[var(--background)] border ${isVulnerable ? 'border-[var(--accent)]' : 'border-[var(--border)]'} relative`}>
                  
                  {/* Function Header */}
                  <div className="p-4 bg-[var(--card)] border-b border-[var(--border)] flex flex-wrap justify-between items-center gap-4">
                    <h3 className="font-mono text-[var(--foreground)] font-bold text-lg">{func.name || `Function_${index + 1}`}</h3>
                    <span className={`px-4 py-1 text-xs font-bold uppercase tracking-widest border ${isVulnerable ? 'bg-[var(--accent)] text-[var(--background)] border-[var(--accent)]' : 'bg-emerald-500/10 text-emerald-500 border-emerald-500/50'}`}>
                      {isVulnerable ? 'Vulnerable' : 'Secure'} ({(prob * 100).toFixed(1)}%)
                    </span>
                  </div>
                  
                  {/* LIME Explainability Breakdown */}
                  {isVulnerable && Array.isArray(func.line_scores) && func.line_scores.length > 0 && (
                    <div className="p-6 sm:p-8">
                      <h4 className="text-xs font-bold text-[var(--accent)] uppercase tracking-widest mb-4">
                        LIME Threat Context (Suspicious Syntax)
                      </h4>
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
                            <div key={i} className="flex items-center justify-between bg-[var(--card)] px-4 py-3 border border-[var(--border)] text-xs font-mono">
                              <div className="flex items-center gap-4 overflow-hidden">
                                {line !== undefined && (
                                  <span className="text-[var(--muted-foreground)] font-bold shrink-0">L_{line}:</span>
                                )}
                                {content ? (
                                  <span className="text-[var(--foreground)] font-bold truncate">{content}</span>
                                ) : (
                                  <span className="text-[var(--muted-foreground)] italic">Flagged token</span>
                                )}
                              </div>
                              <span className={`px-2 py-1 text-[10px] font-bold shrink-0 ml-3 uppercase tracking-wider ${score > 0.2 ? 'bg-[var(--accent)] text-[var(--background)]' : 'bg-[var(--border)] text-[var(--muted-foreground)]'}`}>
                                {(score * 100).toFixed(1)}% Weight
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

        {/* Unified Seq2Seq NLG Executive Audit Report */}
        {rawSourceCode && isHighRisk && (
          <div className="pt-6 border-t border-[var(--border)]">
            <ThreatReport 
              sourceCode={rawSourceCode}
              vulnerabilityType={functions.find((f: any) => f.probability >= threshold)?.name ? `Vulnerability in ${functions.find((f: any) => f.probability >= threshold).name}` : "Multi-Function Code Anomaly"}
              flaggedTokens={allFlaggedTokens}
            />
          </div>
        )}

      </div>
    </main>
  );
}