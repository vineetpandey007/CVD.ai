import { Link, useLocation } from 'react-router-dom';

export default function Nav() {
  const location = useLocation();

  const NavLink = ({ to, label }: { to: string, label: string }) => {
    const isActive = location.pathname === to;
    return (
      <Link 
        to={to} 
        className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
          isActive 
            ? 'bg-blue-500/10 text-blue-400' 
            : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <nav className="w-full py-4 px-6 sm:px-8 flex justify-between items-center absolute top-0 z-50 bg-gray-950/50 backdrop-blur-md border-b border-gray-800/50">
      <div className="flex items-center gap-8">
        <Link to="/" className="text-2xl font-bold tracking-tighter text-white transition-colors">
          CVD<span className="text-blue-500">.ai</span>
        </Link>
        
        {/* Expanded Menu Bar */}
        <div className="hidden md:flex items-center gap-2">
          <NavLink to="/" label="Platform" />
          <NavLink to="/analyzer" label="Code Analyzer" />
          <NavLink to="/history" label="Audit History" />
          <NavLink to="/model" label="AI Architecture" />
          <a href="https://github.com/vineetpandey007" target="_blank" rel="noreferrer" className="px-3 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">GitHub Profile</a>
        </div>
      </div>
    </nav>
  );
}