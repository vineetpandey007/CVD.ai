import { Link, useLocation } from 'react-router-dom';

export default function Nav() {
  const location = useLocation();

  // Helper component for perfectly centered, tab-like links
  const NavLink = ({ to, label }: { to: string, label: string }) => {
    const isActive = location.pathname === to;
    return (
      <Link 
        to={to} 
        className={`relative flex items-center h-full px-5 text-sm font-semibold transition-colors duration-200 ${
          isActive 
            ? 'text-[var(--foreground)]' 
            : 'text-[var(--muted-foreground)] hover:text-[var(--foreground)]'
        }`}
      >
        {label}
        {/* Active state underline - Snaps to the bottom border of the nav */}
        {isActive && (
          <span className="absolute bottom-[-1px] left-0 w-full h-[2px] bg-[var(--accent)] shadow-[0_-2px_10px_var(--accent)]"></span>
        )}
      </Link>
    );
  };

  return (
    <nav className="fixed top-0 left-0 w-full h-16 z-50 bg-[var(--background)]/80 backdrop-blur-xl border-b border-[var(--border)]">
      <div className="w-full h-full px-6 sm:px-12 flex justify-between items-center">
        
        {/* 1. Left: Logo */}
        <div className="flex-shrink-0 flex items-center w-[200px]">
          <Link to="/" className="text-2xl font-black tracking-tighter text-[var(--foreground)]">
            CVD<span className="text-[var(--accent)]">.ai</span>
          </Link>
        </div>
        
        {/* 2. Center: Core Navigation Links */}
        <div className="hidden md:flex h-full items-center justify-center space-x-1">
          <NavLink to="/" label="Platform" />
          <NavLink to="/analyzer" label="Analyzer" />
          <NavLink to="/history" label="History" />
          <NavLink to="/model" label="Architecture" />
        </div>

        {/* 3. Right: External Actions */}
        <div className="flex-shrink-0 flex items-center justify-end w-[200px]">
          <a 
            href="https://github.com/VineetPandey" 
            target="_blank" 
            rel="noreferrer" 
            className="group flex items-center gap-2 px-4 py-2 text-xs font-bold uppercase tracking-widest text-[var(--foreground)] border border-[var(--border)] hover:border-[var(--accent)] transition-all bg-[var(--card)]"
          >
            <span>GitHub</span>
            <span className="group-hover:translate-x-1 transition-transform opacity-50 group-hover:opacity-100 group-hover:text-[var(--accent)]">↗</span>
          </a>
        </div>

      </div>
    </nav>
  );
}