import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeCode } from '../api/client';
import Nav from '../components/Nav';

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
      // Navigate to the results page and pass the AI payload
      navigate('/results', { state: { result } });
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
      <Nav />
      <main className="max-w-4xl mx-auto px-6 py-12 pt-24">
        <h1 className="text-4xl font-bold mb-2 tracking-tight">Code Analyzer</h1>
        <p className="text-gray-400 mb-8">Paste your C or C++ code below to scan for vulnerabilities using CodeBERT.</p>

        <div className="mb-6 flex items-center gap-4">
          <label className="text-sm font-medium text-gray-300 uppercase tracking-wide">Language:</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-gray-900 border border-gray-800 text-gray-200 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
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
            className="w-full h-96 bg-gray-900 border border-gray-800 text-gray-200 p-6 font-mono text-sm rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-y"
          />
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
            {error}
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-500/20"
        >
          {loading ? 'Analyzing Code...' : 'Analyze Code'}
        </button>
      </main>
    </div>
  );
}