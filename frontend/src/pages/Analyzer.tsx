import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeCode, analyzeBulkFiles } from '../api/client';

export default function Analyzer() {
  const [scanMode, setScanMode] = useState<'snippet' | 'bulk'>('snippet');
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('c');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.name.endsWith('.zip')) {
        setError('Please select a valid .zip file.');
        setFile(null);
      } else {
        setError('');
        setFile(selectedFile);
      }
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    
    try {
      let result;
      if (scanMode === 'snippet') {
        if (!code.trim()) throw new Error('Please enter some code to analyze.');
        result = await analyzeCode(code, language);
      } else {
        if (!file) throw new Error('Please upload a .zip repository first.');
        result = await analyzeBulkFiles(file);
      }
      navigate('/results', { state: { result } });
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-4xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12 pt-28 sm:pt-32 flex-grow transition-colors duration-300">
      
      <div className="mb-6 sm:mb-8 bg-white/60 dark:bg-gray-900/60 backdrop-blur-md p-6 sm:p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-lg dark:shadow-none">
        <h1 className="text-3xl sm:text-4xl font-bold mb-2 tracking-tight text-gray-900 dark:text-white">Code Analyzer</h1>
        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
          Scan single files or audit entire repositories for vulnerabilities using CodeBERT.
        </p>
      </div>

      {/* Mode Selection Tabs */}
      <div className="flex space-x-6 mb-6 border-b border-gray-300 dark:border-gray-800">
        <button 
          onClick={() => setScanMode('snippet')}
          className={`pb-3 font-semibold text-sm transition-colors ${scanMode === 'snippet' ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
        >
          Paste Code Snippet
        </button>
        <button 
          onClick={() => setScanMode('bulk')}
          className={`pb-3 font-semibold text-sm transition-colors ${scanMode === 'bulk' ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
        >
          Upload Repository (.zip)
        </button>
      </div>

      {/* Snippet Mode UI */}
      {scanMode === 'snippet' && (
        <div className="animate-in fade-in duration-300">
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
            <label className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Language:</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-800 text-gray-900 dark:text-gray-200 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none transition-colors duration-300 w-full sm:w-auto shadow-sm"
            >
              <option value="c">C</option>
              <option value="cpp">C++</option>
            </select>
          </div>

          <div className="mb-6">
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="void test() {&#10;    char buf[10];&#10;    strcpy(buf, 'overflow');&#10;}"
              className="w-full h-80 sm:h-96 bg-white/80 dark:bg-gray-900/80 backdrop-blur border border-gray-300 dark:border-gray-800 text-gray-800 dark:text-gray-200 p-4 sm:p-6 font-mono text-xs sm:text-sm rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-colors duration-300 resize-y shadow-sm"
            />
          </div>
        </div>
      )}

      {/* Bulk Scan Mode UI */}
      {scanMode === 'bulk' && (
        <div className="animate-in fade-in duration-300 mb-6">
          <div className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${file ? 'border-emerald-500 bg-emerald-500/5' : 'border-gray-300 dark:border-gray-700 hover:border-blue-500 hover:bg-blue-500/5'}`}>
            <input type="file" accept=".zip" onChange={handleFileChange} className="hidden" id="zip-upload" />
            <label htmlFor="zip-upload" className="cursor-pointer flex flex-col items-center justify-center w-full h-full">
              <span className="text-5xl mb-4">{file ? '📦' : '📁'}</span>
              <span className={`font-semibold text-lg ${file ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-700 dark:text-gray-200'}`}>
                {file ? file.name : 'Click to upload a .zip repository'}
              </span>
              {!file && <span className="text-gray-500 dark:text-gray-400 text-sm mt-2">Extracts and scans all .c, .cpp, .h, and .hpp files automatically.</span>}
              {file && <span className="text-emerald-500/80 text-sm mt-2 font-mono">{(file.size / 1024 / 1024).toFixed(2)} MB</span>}
            </label>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-100 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-600 dark:text-red-400 text-sm flex items-center gap-2">
          ⚠️ {error}
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading || (scanMode === 'bulk' && !file)}
        className="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-500/20 text-center flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="animate-spin text-xl">⚙️</span> 
            {scanMode === 'bulk' ? 'Auditing Repository...' : 'Analyzing Code...'}
          </>
        ) : (
          scanMode === 'bulk' ? 'Run Repository Audit' : 'Analyze Code'
        )} 
      </button>
    </main>
  );
}