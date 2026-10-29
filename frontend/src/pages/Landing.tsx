import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div className="w-full flex flex-col items-center justify-center pt-32 pb-24 px-6 sm:px-12 relative z-10">
      
      {/* 1. Hero Section */}
      <div className="max-w-5xl w-full text-center space-y-8 mt-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        <div className="inline-flex items-center gap-3 rounded-full border border-[var(--border)] bg-[var(--muted)] px-5 py-2 mb-4">
          <span className="h-2 w-2 rounded-full bg-[var(--accent)] animate-pulse shadow-[0_0_8px_var(--accent)]" />
          <span className="font-mono text-xs uppercase tracking-[0.15em] text-[var(--foreground)] font-bold">
            CVD.ai Core Engine v2.4 • CodeBERT + Groq LLM + ChromaDB
          </span>
        </div>

        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold tracking-tighter leading-[1.1] text-[var(--foreground)]">
          Enterprise-Grade <br />
          <span className="text-[var(--accent)] relative inline-block mt-2">
            Vulnerability Detection
            <span className="absolute bottom-1 left-0 w-full h-[4px] md:h-[8px] bg-[var(--accent)]/20 rounded-full"></span>
          </span>
        </h1>
        
        <p className="max-w-2xl mx-auto text-lg md:text-xl text-[var(--muted-foreground)] leading-relaxed pt-4">
          CVD.ai unifies fine-tuned CodeBERT transformers, LIME token explainability, ChromaDB semantic vector search, and high-speed Groq LLM threat reporting to secure C/C++ codebases in real-time.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-8">
          <Link 
            to="/analyzer" 
            className="group relative inline-flex items-center justify-center w-full sm:w-auto px-8 py-4 font-bold text-[var(--background)] bg-[var(--accent)] transition-all hover:-translate-y-1 shadow-md hover:shadow-lg cursor-pointer"
          >
            <span className="mr-2">Run Neural Scan</span>
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </Link>
          
          <Link 
            to="/model" 
            className="inline-flex items-center justify-center w-full sm:w-auto px-8 py-4 font-bold text-[var(--foreground)] bg-transparent border-2 border-[var(--border)] hover:border-[var(--accent)] transition-all cursor-pointer"
          >
            Read AI Model Card
          </Link>
        </div>
      </div>

      {/* 2. End-to-End Pipeline Architecture (Classy 2x2 Grid) */}
      <div className="max-w-6xl w-full mt-40">
        
        <div className="flex flex-col items-center mb-16 text-center">
          <span className="text-[var(--accent)] font-mono text-sm font-bold tracking-[0.2em] uppercase mb-4">Neural Architecture</span>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-[var(--foreground)]">End-to-End Processing Flow</h2>
        </div>

        {/* 2x2 Clean Structured Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
          
          {/* Node 1: CodeBERT Classification */}
          <div className="bg-[var(--card)] border border-[var(--border)] p-8 transition-all duration-300 hover:border-[var(--accent)] hover:-translate-y-1 relative flex flex-col group shadow-2xl">
            <div className="flex items-center justify-between mb-6 border-b border-[var(--border)] pb-4">
              <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center font-mono text-lg font-bold text-[var(--accent)] border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
                ⟨/⟩
              </div>
              <span className="px-3 py-1 bg-[var(--muted)] text-xs font-mono font-bold text-[var(--accent)] border border-[var(--border)]">
                STAGE 01 // CODEBERT
              </span>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-[var(--foreground)] tracking-tight">Transformer Inference</h3>
            <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
              Fine-tuned transformer model surgically analyzes raw C/C++ token streams to detect buffer overflows, stack corruption, and logic flaws with high precision.
            </p>
          </div>

          {/* Node 2: LIME Explainability */}
          <div className="bg-[var(--card)] border border-[var(--border)] p-8 transition-all duration-300 hover:border-[var(--accent)] hover:-translate-y-1 relative flex flex-col group shadow-2xl">
            <div className="flex items-center justify-between mb-6 border-b border-[var(--border)] pb-4">
              <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center font-mono text-xl font-bold text-[var(--accent)] border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
                ◎
              </div>
              <span className="px-3 py-1 bg-[var(--muted)] text-xs font-mono font-bold text-[var(--accent)] border border-[var(--border)]">
                STAGE 02 // LIME AI
              </span>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-[var(--foreground)] tracking-tight">Token-Level Explainability</h3>
            <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
              Isolates exact suspicious syntax tokens and variable assignments, mapping probabilistic neural risk back to human-readable source code lines.
            </p>
          </div>

          {/* Node 3: ChromaDB Vector Search */}
          <div className="bg-[var(--card)] border border-[var(--border)] p-8 transition-all duration-300 hover:border-[var(--accent)] hover:-translate-y-1 relative flex flex-col group shadow-2xl">
            <div className="flex items-center justify-between mb-6 border-b border-[var(--border)] pb-4">
              <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center font-mono text-xl font-bold text-[var(--accent)] border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
                ⌖
              </div>
              <span className="px-3 py-1 bg-[var(--muted)] text-xs font-mono font-bold text-[var(--accent)] border border-[var(--border)]">
                STAGE 03 // CHROMADB
              </span>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-[var(--foreground)] tracking-tight">Semantic Vector Search</h3>
            <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
              Generates 768-dimensional mathematical vector embeddings to query persistent historical databases for structurally similar vulnerabilities.
            </p>
          </div>

          {/* Node 4: Groq NLG Reports */}
          <div className="bg-[var(--card)] border border-[var(--border)] p-8 transition-all duration-300 hover:border-[var(--accent)] hover:-translate-y-1 relative flex flex-col group shadow-2xl">
            <div className="flex items-center justify-between mb-6 border-b border-[var(--border)] pb-4">
              <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center font-mono text-xl font-bold text-[var(--accent)] border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
                ⚙
              </div>
              <span className="px-3 py-1 bg-[var(--muted)] text-xs font-mono font-bold text-[var(--accent)] border border-[var(--border)]">
                STAGE 04 // GROQ LLM
              </span>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-[var(--foreground)] tracking-tight">Executive Threat Reports</h3>
            <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
              Synthesizes structured executive threat reports and production-ready C/C++ patched code implementations instantly via ultra-fast Groq inference.
            </p>
          </div>

        </div>
      </div>

      {/* 3. Feature Highlights Section */}
      <div className="max-w-7xl w-full mt-32 grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div className="bg-[var(--card)] border border-[var(--border)] p-8">
          <span className="font-mono text-xs text-[var(--accent)] uppercase tracking-widest block mb-2">[01 SECURITY]</span>
          <h4 className="text-xl font-bold text-[var(--foreground)] mb-3">Buffer Overflow Defense</h4>
          <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
            Instantly flags dangerous functions like `strcpy`, `sprintf`, and unvalidated stack allocations before deployment.
          </p>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] p-8">
          <span className="font-mono text-xs text-[var(--accent)] uppercase tracking-widest block mb-2">[02 EXPORT]</span>
          <h4 className="text-xl font-bold text-[var(--foreground)] mb-3">Executive PDF Reports</h4>
          <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
            Compile complete vulnerability assessments, LIME syntax tokens, and AI patches into downloadable security reports.
          </p>
        </div>

        <div className="bg-[var(--card)] border border-[var(--border)] p-8">
          <span className="font-mono text-xs text-[var(--accent)] uppercase tracking-widest block mb-2">[03 SPEED]</span>
          <h4 className="text-xl font-bold text-[var(--foreground)] mb-3">Sub-Second Groq Inference</h4>
          <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">
            Leverage ultra-fast developer models (`openai/gpt-oss-20b`) with automated fallback handling for zero-latency audits.
          </p>
        </div>

      </div>

    </div>
  );
}