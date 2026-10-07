import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeCode } from '../api/client';

export default function Analyzer() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('c');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to analyze.');
      return;
    }
    setLoading(true);
    setError('');
    
    try {
      const result = await analyzeCode(code, language);
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
          Paste your C or C++ code below to scan for vulnerabilities using CodeBERT.
        </p>
      </div>

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

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-100 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-600 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-500/20 text-center"
      >
        {loading ? 'Analyzing Code...' : 'Analyze Code'} 
      </button>
    </main>
  );
}