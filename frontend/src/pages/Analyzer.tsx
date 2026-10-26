import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import SemanticSearchModal from '../components/SemanticSearchModal';

const SAMPLE_VULNERABLE_CODE = `#include <stdio.h>
#include <string.h>

void process_data(char *input) {
    char buffer[50];
    // Unsafe copy leading to buffer overflow
    strcpy(buffer, input);
    printf("Data processed: %s\\n", buffer);
}

int main() {
    char large_input[100] = "Buffer overflow test payload exceeding 50 bytes";
    process_data(large_input);
    return 0;
}`;

export default function Analyzer() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [code, setCode] = useState<string>(SAMPLE_VULNERABLE_CODE);
  const [language, setLanguage] = useState<string>('c');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isBulkScanning, setIsBulkScanning] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);

  const handleScan = async () => {
    if (!code.trim()) {
      setErrorMessage('Source code input cannot be empty.');
      return;
    }

    setIsScanning(true);
    setErrorMessage(null);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const result = await response.json();
      navigate('/results', { state: { result, sourceCode: code } });
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to analyze code snippet.');
    } finally {
      setIsScanning(false);
    }
  };

  const handleBulkUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsBulkScanning(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/analyze-bulk', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const result = await response.json();
      navigate('/results', { state: { result, sourceCode: `// Bulk Scan: ${file.name}` } });
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to process bulk repository archive.');
    } finally {
      setIsBulkScanning(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <main className="max-w-6xl w-full mx-auto px-4 sm:px-6 py-12 pt-32 flex-grow z-10 relative">
      {/* Semantic Search Modal */}
      <SemanticSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
      />

      {/* Top Header Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4 border-b border-[var(--border)] pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black uppercase tracking-tight text-[var(--foreground)]">
            Neural Vulnerability Scanner
          </h1>
          <p className="text-xs font-mono text-[var(--muted-foreground)] uppercase tracking-widest mt-1">
            CodeBERT AST Slicer & Explainable AI Engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSearchOpen(true)}
            className="border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-xs font-mono font-bold uppercase tracking-widest text-[var(--foreground)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-all shadow-sm"
          >
            [⌕ Semantic Vector Search]
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            onChange={handleBulkUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isBulkScanning || isScanning}
            className="border border-[var(--border)] bg-[var(--card)] px-4 py-2.5 text-xs font-mono font-bold uppercase tracking-widest text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:border-[var(--accent)] disabled:opacity-50 transition-all shadow-sm"
          >
            {isBulkScanning ? 'Processing ZIP...' : '↑ Bulk Repository (.zip)'}
          </button>
        </div>
      </div>

      {/* Code Editor Container */}
      <div className="bg-[var(--card)] border border-[var(--border)] p-6 shadow-2xl space-y-6">
        <div className="flex flex-wrap justify-between items-center gap-4 border-b border-[var(--border)] pb-4">
          <div className="flex items-center gap-3">
            <label className="text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)]">
              Target Syntax:
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] px-3 py-1 font-mono text-xs uppercase outline-none focus:border-[var(--accent)]"
            >
              <option value="c">C</option>
              <option value="cpp">C++</option>
            </select>
          </div>

          <button
            onClick={() => setCode(SAMPLE_VULNERABLE_CODE)}
            className="text-[10px] font-mono uppercase tracking-widest text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors underline"
          >
            Reset to Sample Payload
          </button>
        </div>

        {/* Error Notification */}
        {errorMessage && (
          <div className="p-4 bg-red-500/10 border border-red-500 text-red-400 font-mono text-xs">
            [EXECUTION_FAULT]: {errorMessage}
          </div>
        )}

        {/* Text Area */}
        <div className="relative">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={18}
            spellCheck={false}
            placeholder="// Paste C/C++ source code routines here for AST slicing..."
            className="w-full bg-[var(--background)] border border-[var(--border)] p-4 font-mono text-xs sm:text-sm text-[var(--foreground)] focus:border-[var(--accent)] outline-none resize-y leading-relaxed"
          />
        </div>

        {/* Submit Action */}
        <div className="flex justify-end">
          <button
            onClick={handleScan}
            disabled={isScanning || isBulkScanning}
            className="w-full sm:w-auto bg-[var(--foreground)] text-[var(--background)] px-8 py-3.5 text-xs font-bold font-mono uppercase tracking-widest transition-all disabled:opacity-50 hover:bg-[var(--accent)] hover:text-white"
          >
            {isScanning ? 'Executing CodeBERT AST Inference...' : 'Initialize Neural Scan →'}
          </button>
        </div>
      </div>
    </main>
  );
}