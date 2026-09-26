export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="relative border-t border-white/10 px-6 py-10 text-center">
      <p className="font-mono text-xs text-fog">
        © {year} Sentinel. All rights reserved.
      </p>
      <p className="mt-2 font-mono text-xs text-fog">
        Licensed under the MIT License.
      </p>
      <p className="mt-4 text-sm text-fog/80">
        Made by <span className="text-chalk">Vineet Pandey</span>
      </p>
    </footer>
  );
}