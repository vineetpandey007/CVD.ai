import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div className="w-full flex flex-col items-center justify-center pt-32 pb-24 px-6 sm:px-12 relative z-10">
      
      {/* Flowchart Animations (Injected safely) */}
      <style>{`
        @keyframes flow-x {
          0% { transform: translateX(-100%); opacity: 0; }
          20% { opacity: 1; }
          80% { opacity: 1; }
          100% { transform: translateX(300%); opacity: 0; }
        }
        @keyframes flow-y {
          0% { transform: translateY(-100%); opacity: 0; }
          20% { opacity: 1; }
          80% { opacity: 1; }
          100% { transform: translateY(300%); opacity: 0; }
        }
        .animate-flow-x {
          animation: flow-x 2s linear infinite;
        }
        .animate-flow-x-delayed {
          animation: flow-x 2s linear infinite;
          animation-delay: 1s;
        }
        .animate-flow-y {
          animation: flow-y 2s linear infinite;
        }
        .animate-flow-y-delayed {
          animation: flow-y 2s linear infinite;
          animation-delay: 1s;
        }
      `}</style>

      {/* 1. Hero Section */}
      <div className="max-w-5xl w-full text-center space-y-8 mt-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        <div className="inline-flex items-center gap-3 rounded-full border border-[var(--border)] bg-[var(--muted)] px-5 py-2 mb-4">
          <span className="h-2 w-2 rounded-full bg-[var(--accent)] animate-pulse shadow-[0_0_8px_var(--accent)]" />
          <span className="font-mono text-xs uppercase tracking-[0.15em] text-[var(--foreground)] font-bold">
            CVD.ai Core Engine
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
          CVD.ai leverages a custom-trained CodeBERT transformer model to intelligently identify Buffer Overflows, Memory Leaks, and Logic Flaws in raw C/C++ syntax with state-of-the-art token-level explainability.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-8">
          <Link 
            to="/analyzer" 
            className="group relative inline-flex items-center justify-center w-full sm:w-auto px-8 py-4 font-bold text-[var(--background)] bg-[var(--accent)] transition-all hover:-translate-y-1 shadow-md hover:shadow-lg"
          >
            <span className="mr-2">Run Neural Scan</span>
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </Link>
          
          <Link 
            to="/model" 
            className="inline-flex items-center justify-center w-full sm:w-auto px-8 py-4 font-bold text-[var(--foreground)] bg-transparent border-2 border-[var(--border)] hover:border-[var(--accent)] transition-all"
          >
            Read AI Model Card
          </Link>
        </div>
      </div>

      {/* 2. Architecture Animated Flowchart Section */}
      <div className="max-w-7xl w-full mt-40">
        
        <div className="flex flex-col items-center mb-16 text-center">
          <span className="text-[var(--accent)] font-mono text-sm font-bold tracking-[0.2em] uppercase mb-4">Pipeline Architecture</span>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-[var(--foreground)]">Data Processing Flow</h2>
        </div>

        {/* The Flowchart Container */}
        <div className="flex flex-col lg:flex-row items-center lg:items-stretch w-full relative z-10">
          
          {/* Node 1: AST Parsing */}
          <div className="w-full lg:w-[30%] bg-[var(--card)] border border-[var(--border)] p-8 transition-colors duration-300 hover:border-[var(--accent)] relative flex flex-col group shadow-2xl">
            <div className="absolute top-0 right-0 px-3 py-1 bg-[var(--border)] text-xs font-mono font-bold text-[var(--muted-foreground)] group-hover:bg-[var(--accent)] group-hover:text-[var(--background)] transition-colors">
              NODE_01
            </div>
            <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center text-xl mb-6 border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
              ⚙️
            </div>
            <h3 className="text-2xl font-bold mb-4 text-[var(--foreground)] tracking-tight">AST Parsing</h3>
            <p className="text-[var(--muted-foreground)] leading-relaxed text-sm">
              Raw source code is surgically dismantled into a structural syntax tree. By isolating discrete functional logic, the engine establishes a foundation for absolute analytical precision.
            </p>
          </div>

          {/* Connector 1 -> 2 */}
          <div className="flex justify-center items-center h-16 lg:h-auto lg:flex-1 w-full relative">
            {/* Mobile Vertical Flow */}
            <div className="h-full w-[2px] bg-[var(--border)] lg:hidden relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[40%] bg-[var(--accent)] animate-flow-y shadow-[0_0_10px_var(--accent)]"></div>
            </div>
            {/* Desktop Horizontal Flow */}
            <div className="w-full h-[2px] bg-[var(--border)] hidden lg:block relative overflow-hidden">
              <div className="absolute top-0 left-0 h-full w-[40%] bg-[var(--accent)] animate-flow-x shadow-[0_0_10px_var(--accent)]"></div>
            </div>
          </div>

          {/* Node 2: CodeBERT Inference */}
          <div className="w-full lg:w-[30%] bg-[var(--card)] border border-[var(--border)] p-8 transition-colors duration-300 hover:border-[var(--accent)] relative flex flex-col group shadow-2xl">
            <div className="absolute top-0 right-0 px-3 py-1 bg-[var(--border)] text-xs font-mono font-bold text-[var(--muted-foreground)] group-hover:bg-[var(--accent)] group-hover:text-[var(--background)] transition-colors">
              NODE_02
            </div>
            <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center text-xl mb-6 border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
              🧠
            </div>
            <h3 className="text-2xl font-bold mb-4 text-[var(--foreground)] tracking-tight">CodeBERT Inference</h3>
            <p className="text-[var(--muted-foreground)] leading-relaxed text-sm">
              Neural transformers evaluate tokenized streams of logic in real-time. Leveraging deep learning, the architecture natively surfaces latent memory corruption and systemic vulnerabilities.
            </p>
          </div>

          {/* Connector 2 -> 3 */}
          <div className="flex justify-center items-center h-16 lg:h-auto lg:flex-1 w-full relative">
            {/* Mobile Vertical Flow */}
            <div className="h-full w-[2px] bg-[var(--border)] lg:hidden relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[40%] bg-[var(--accent)] animate-flow-y-delayed shadow-[0_0_10px_var(--accent)]"></div>
            </div>
            {/* Desktop Horizontal Flow */}
            <div className="w-full h-[2px] bg-[var(--border)] hidden lg:block relative overflow-hidden">
              <div className="absolute top-0 left-0 h-full w-[40%] bg-[var(--accent)] animate-flow-x-delayed shadow-[0_0_10px_var(--accent)]"></div>
            </div>
          </div>

          {/* Node 3: LIME Explainer */}
          <div className="w-full lg:w-[30%] bg-[var(--card)] border border-[var(--border)] p-8 transition-colors duration-300 hover:border-[var(--accent)] relative flex flex-col group shadow-2xl">
            <div className="absolute top-0 right-0 px-3 py-1 bg-[var(--border)] text-xs font-mono font-bold text-[var(--muted-foreground)] group-hover:bg-[var(--accent)] group-hover:text-[var(--background)] transition-colors">
              NODE_03
            </div>
            <div className="w-12 h-12 bg-[var(--muted)] flex items-center justify-center text-xl mb-6 border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors">
              🔍
            </div>
            <h3 className="text-2xl font-bold mb-4 text-[var(--foreground)] tracking-tight">LIME Explainer</h3>
            <p className="text-[var(--muted-foreground)] leading-relaxed text-sm">
              Opaque neural predictions are mathematically deconstructed. Probabilistic risk is mapped directly back to specific lines of code, transforming AI inference into actionable human insight.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}