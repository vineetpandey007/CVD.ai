import { Link } from "react-router-dom";

const PRODUCT_NAME = "Sentinel";
const EASE = "ease-[cubic-bezier(0.16,1,0.3,1)]";

export function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 px-6 pt-4">
      <div className="glass mx-auto flex max-w-6xl items-center justify-between rounded-full px-5 py-3">
        <Link
          to="/"
          className="font-serif text-lg font-semibold tracking-tight text-chalk"
        >
          {PRODUCT_NAME}
        </Link>
        <nav className="hidden items-center gap-8 font-sans text-xs font-medium uppercase tracking-[0.15em] text-fog sm:flex">
          <Link to="/#about" className={`transition ${EASE} hover:text-chalk`}>
            About
          </Link>
          <Link
            to="/#how-it-works"
            className={`transition ${EASE} hover:text-chalk`}
          >
            How it works
          </Link>
          <Link
            to="/#coverage"
            className={`transition ${EASE} hover:text-chalk`}
          >
            Coverage
          </Link>
        </nav>
        <Link
          to="/analyzer"
          className={`glass-strong rounded-full px-4 py-1.5 font-sans text-xs font-semibold tracking-tight text-chalk transition ${EASE} hover:bg-white/10`}
        >
          Try it →
        </Link>
      </div>
    </header>
  );
}
