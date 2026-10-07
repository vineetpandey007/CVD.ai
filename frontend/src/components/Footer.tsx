export default function Footer() {
  return (
    <footer className="w-full border-t border-gray-800 bg-gray-950/80 backdrop-blur-md py-6 z-50 relative mt-auto">
      <div className="max-w-5xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-mono text-gray-500">
        <div>
          <span className="text-gray-400">CVD.ai</span> &copy; {new Date().getFullYear()} — Released under the MIT License.
        </div>
        <div className="flex items-center gap-2">
          <span>Engineered by</span>
          <span className="text-gray-300 font-semibold tracking-wide">Vineet Pandey</span>
        </div>
      </div>
    </footer>
  );
}