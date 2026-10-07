import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <main className="flex-grow flex flex-col items-center justify-start px-4 sm:px-6 pt-32 pb-20 text-center transition-colors duration-300 overflow-x-hidden">
      
      {/* Hero Section */}
      <div className="max-w-5xl mx-auto z-10 w-full mb-32 mt-12">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-6 leading-tight">
          Detect Code Vulnerabilities <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500 dark:from-blue-400 dark:to-cyan-300">
            Before They Deploy.
          </span>
        </h1>
        <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
          CVD.ai leverages a custom-trained CodeBERT transformer model to intelligently identify Buffer Overflows, Memory Leaks, and Logic Flaws in raw C/C++ syntax with state-of-the-art token-level explainability.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link to="/analyzer" className="w-full sm:w-auto px-8 py-4 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-semibold text-lg transition-all shadow-[0_0_40px_-10px_rgba(37,99,235,0.6)] hover:shadow-[0_0_60px_-10px_rgba(37,99,235,0.8)]">
            Run Neural Scan →
          </Link>
          <Link to="/model" className="w-full sm:w-auto px-8 py-4 rounded-full bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white hover:bg-white dark:hover:bg-gray-800 font-semibold text-lg transition-all shadow-sm">
            Read AI Model Card
          </Link>
        </div>
      </div>

      {/* Deep Dive Architecture Section */}
      <div className="max-w-7xl mx-auto z-10 w-full mb-32">
        <div className="text-center mb-16">
          <h2 className="text-sm font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase mb-3">System Architecture</h2>
          <h3 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">How the AI Engine Works</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          {/* Step 1 */}
          <div className="p-8 rounded-3xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200 dark:border-gray-800 hover:-translate-y-1 transition-transform duration-300 shadow-xl shadow-gray-200/50 dark:shadow-none relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 text-8xl font-black text-gray-100 dark:text-gray-800/30 -z-10 -mt-8 -mr-8">1</div>
            <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 rounded-xl flex items-center justify-center text-xl mb-6">⚙️</div>
            <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3 tracking-tight">AST Parsing & Chunking</h4>
            <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">The FastAPI backend uses <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-gray-800 dark:text-gray-300 border border-gray-200 dark:border-gray-700">tree-sitter</code> to dissect raw C/C++ files into an Abstract Syntax Tree, intelligently isolating individual functions for precise contextual analysis.</p>
          </div>
          
          {/* Step 2 */}
          <div className="p-8 rounded-3xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200 dark:border-gray-800 hover:-translate-y-1 transition-transform duration-300 shadow-xl shadow-gray-200/50 dark:shadow-none relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 text-8xl font-black text-gray-100 dark:text-gray-800/30 -z-10 -mt-8 -mr-8">2</div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-xl flex items-center justify-center text-xl mb-6">🧠</div>
            <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3 tracking-tight">CodeBERT Inference</h4>
            <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">Each function is tokenized and fed into a PyTorch model running Microsoft's CodeBERT architecture, fine-tuned specifically on the Devign dataset to classify memory corruption vulnerabilities.</p>
          </div>

          {/* Step 3 */}
          <div className="p-8 rounded-3xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200 dark:border-gray-800 hover:-translate-y-1 transition-transform duration-300 shadow-xl shadow-gray-200/50 dark:shadow-none relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 text-8xl font-black text-gray-100 dark:text-gray-800/30 -z-10 -mt-8 -mr-8">3</div>
            <div className="w-12 h-12 bg-cyan-100 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 rounded-xl flex items-center justify-center text-xl mb-6">🔍</div>
            <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3 tracking-tight">LIME Explainability</h4>
            <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">The AI's black-box decision is demystified using Local Interpretable Model-agnostic Explanations, highlighting exactly which suspicious variable names or buffer sizes triggered the alert.</p>
          </div>
        </div>
      </div>

    </main>
  );
}