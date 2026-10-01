import { useParams } from "react-router-dom";

export default function Results() {
  const { scanId } = useParams();

  return (
    <main className="relative flex min-h-[92vh] items-center justify-center px-6 pb-24 pt-32 text-chalk">
      <section className="glass w-full max-w-3xl rounded-2xl px-8 py-10 sm:px-12">
        <h1 className="font-serif text-3xl font-semibold tracking-tight sm:text-4xl">
          Results
        </h1>
        <p className="mt-4 font-mono text-sm text-fog">{scanId}</p>
      </section>
    </main>
  );
}
