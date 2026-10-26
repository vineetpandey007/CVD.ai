import { useState } from 'react';

interface Match {
  id: string;
  code: string;
  metadata: {
    function_name?: string;
    probability?: number;
    is_vulnerable?: boolean;
  };
  distance: number;
}

interface SemanticSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SemanticSearchModal({ isOpen, onClose }: SemanticSearchModalProps) {
  const [queryCode, setQueryCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Match[]>([]);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSearch = async () => {
    if (!queryCode.trim()) return;
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch('http://localhost:8000/api/semantic-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_code: queryCode }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      setResults(data.matches || []);
    } catch (err: any) {
      setError(err.message || 'Failed to execute vector search.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-[var(--card)] border border-[var(--border)] max-w-4xl w-full p-6 shadow-2xl flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex justify-between items-center border-b border-[var(--border)] pb-4 mb-4">
          <div>
            <h3 className="text-lg font-black uppercase tracking-wider text-[var(--foreground)]">
              Semantic Vulnerability Search
            </h3>
            <p className="text-xs font-mono text-[var(--muted-foreground)]">
              Powered by CodeBERT [CLS] 768-D Vector Embeddings & ChromaDB
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[var(--muted-foreground)] hover:text-[var(--foreground)] font-mono text-sm px-2 py-1 border border-[var(--border)]"
          >
            [ESC / CLOSE]
          </button>
        </div>

        {/* Query Input */}
        <div className="space-y-3 mb-4">
          <label className="block text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)]">
            Paste C/C++ Function to Find Structurally Similar Code:
          </label>
          <textarea
            value={queryCode}
            onChange={(e) => setQueryCode(e.target.value)}
            rows={5}
            placeholder="void test_function(char *input) { ... }"
            className="w-full bg-[var(--background)] border border-[var(--border)] p-3 font-mono text-xs text-[var(--foreground)] focus:border-[var(--accent)] outline-none resize-none"
          />
          <button
            onClick={handleSearch}
            disabled={loading || !queryCode.trim()}
            className="w-full py-2 bg-[var(--foreground)] text-[var(--background)] font-mono text-xs font-bold uppercase tracking-widest hover:bg-[var(--accent)] hover:text-white disabled:opacity-50 transition-all"
          >
            {loading ? 'Computing Embedding & Querying Vectors...' : 'Execute Vector Search'}
          </button>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-3 mb-4 bg-red-500/10 border border-red-500 text-red-400 font-mono text-xs">
            [ERROR]: {error}
          </div>
        )}

        {/* Results Area */}
        <div className="overflow-y-auto flex-1 space-y-4 pr-1">
          {results.length === 0 && !loading && !error && (
            <p className="text-center py-8 font-mono text-xs text-[var(--muted-foreground)] uppercase">
              No similarity query executed yet or database empty.
            </p>
          )}

          {results.map((match, idx) => {
            const isVulnerable = match.metadata?.is_vulnerable;
            const prob = match.metadata?.probability;
            return (
              <div
                key={match.id || idx}
                className="bg-[var(--background)] border border-[var(--border)] p-4 space-y-2 text-xs font-mono"
              >
                <div className="flex justify-between items-center border-b border-[var(--border)] pb-2">
                  <span className="font-bold text-[var(--foreground)]">
                    Match #{idx + 1}: {match.metadata?.function_name || match.id}
                  </span>
                  <div className="flex gap-2 items-center">
                    <span className="px-2 py-0.5 border border-[var(--border)] text-[var(--muted-foreground)] text-[10px]">
                      Vector Distance: {match.distance.toFixed(4)}
                    </span>
                    {prob !== undefined && (
                      <span
                        className={`px-2 py-0.5 border text-[10px] uppercase font-bold ${
                          isVulnerable
                            ? 'bg-[var(--accent)]/20 text-[var(--accent)] border-[var(--accent)]'
                            : 'bg-emerald-500/20 text-emerald-400 border-emerald-500'
                        }`}
                      >
                        {isVulnerable ? 'Vulnerable' : 'Clean'} ({(prob * 100).toFixed(1)}%)
                      </span>
                    )}
                  </div>
                </div>
                <pre className="p-2 bg-[var(--card)] border border-[var(--border)] text-[11px] overflow-x-auto text-[var(--foreground)]">
                  <code>{match.code}</code>
                </pre>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}