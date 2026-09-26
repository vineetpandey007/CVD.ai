export function AmbientBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 overflow-hidden bg-ink"
    >
      <div className="absolute -left-1/4 top-0 h-[60vh] w-[60vh] animate-drift-slow rounded-full bg-olive/20 blur-3xl" />
      <div className="absolute -right-1/4 bottom-0 h-[70vh] w-[70vh] animate-drift-slow-reverse rounded-full bg-olive/15 blur-3xl" />
    </div>
  );
}