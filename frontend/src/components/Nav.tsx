import { Link, useLocation } from 'react-router-dom';

export default function Nav() {
  const location = useLocation();
  
  return (
    <nav className="fixed top-0 w-full z-50 bg-gray-950/80 backdrop-blur-md border-b border-gray-800">
      <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-gray-100 tracking-tighter hover:text-white transition-colors">
          CVD<span className="text-blue-500">.ai</span>
        </Link>
        <div className="flex gap-6 text-sm font-medium text-gray-400">
          <Link 
            to="/analyze" 
            className={`hover:text-gray-100 transition-colors ${location.pathname === '/analyze' ? 'text-gray-100' : ''}`}
          >
            Analyzer
          </Link>
          <Link 
            to="/model" 
            className={`hover:text-gray-100 transition-colors ${location.pathname === '/model' ? 'text-gray-100' : ''}`}
          >
            Model Card
          </Link>
        </div>
      </div>
    </nav>
  );
}