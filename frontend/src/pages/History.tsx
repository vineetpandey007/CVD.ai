import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchScanHistory, fetchScanDetail } from '../api/client';

export default function History() {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchScanHistory()
      .then((data) => {
        // Failsafe: Ensure the API returned an actual array before saving it
        if (Array.isArray(data)) {
          setScans(data);
        } else {
          console.error("Invalid data format received from API:", data);
          setError("Failed to load history: Data is corrupted.");
        }
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleOpenReport = async (id: string) => {
    try {
      const fullReport = await fetchScanDetail(id);
      navigate('/results', { state: { result: fullReport } });
    } catch (err: any) {
      alert(`Could not open report: ${err.message}`);
    }
  };

  return (
    <main className="max-w-5xl w-full mx-auto px-4 sm:px-6 py-12 pt-28 flex-grow">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white">Scan History</h1>
          <p className="text-gray-400 text-sm mt-1">Review past repository and snippet vulnerability audits stored in DuckDB.</p>
        </div>
        <button
          onClick={() => navigate('/analyzer')}
          className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow"
        >
          + New Audit
        </button>
      </div>

      {loading ? (
        <div className="text-gray-400 text-center py-20 font-mono">Loading audit logs from DuckDB...</div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-center">
          {error}
        </div>
      ) : (!Array.isArray(scans) || scans.length === 0) ? (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-12 text-center text-gray-400">
          No audit history found. Run an analysis on the Analyzer tab to populate logs.
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-gray-800/60 text-xs uppercase font-semibold text-gray-400 border-b border-gray-800">
              <tr>
                <th className="px-6 py-4">Target</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Date & Time</th>
                <th className="px-6 py-4 text-center">Vulnerabilities</th>
                <th className="px-6 py-4 text-center">Max Risk</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {scans.map((scan, index) => {
                // Extra failsafe mapping
                const isVuln = (scan.vulnerabilities_found || 0) > 0;
                const riskScore = scan.highest_risk_score || 0;
                
                return (
                  <tr key={scan.id || index} className="hover:bg-gray-800/40 transition">
                    <td className="px-6 py-4 font-mono font-medium text-white">
                      {scan.target_name || "Unknown Target"}
                    </td>
                    <td className="px-6 py-4 capitalize text-gray-400">
                      {scan.scan_type || "N/A"}
                    </td>
                    <td className="px-6 py-4 text-gray-400 text-xs">
                      {scan.created_at || "N/A"}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                        isVuln ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                      }`}>
                        {scan.vulnerabilities_found || 0} / {scan.functions_scanned || 0}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center font-mono text-xs">
                      {(riskScore * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleOpenReport(scan.id)}
                        className="text-blue-400 hover:text-blue-300 text-xs font-semibold underline underline-offset-4"
                      >
                        View Report &rarr;
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}