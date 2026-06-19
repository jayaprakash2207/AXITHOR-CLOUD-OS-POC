import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center px-6 text-white">
      <div className="rounded-[2rem] border border-white/10 bg-white/5 p-10 text-center backdrop-blur-xl">
        <p className="text-sm uppercase tracking-[0.3em] text-brand-200">404</p>
        <h1 className="mt-4 text-3xl font-semibold">Page not found</h1>
        <p className="mt-3 text-white/65">The page you requested does not exist.</p>
        <Link href="/" className="mt-6 inline-flex rounded-full bg-white px-5 py-3 font-semibold text-slate-950">
          Go home
        </Link>
      </div>
    </main>
  );
}
