import Link from 'next/link';
import { ArrowRight, Cloud, FolderGit2, ShieldCheck } from 'lucide-react';

const features = [
  {
    icon: Cloud,
    title: 'BYOC deployment',
    description: 'Connect Google Drive once and deploy static sites directly from your own storage.',
  },
  {
    icon: FolderGit2,
    title: 'Production workflow',
    description: 'Repository-backed data access, service boundaries, and audit-friendly deploy history.',
  },
  {
    icon: ShieldCheck,
    title: 'Secure by default',
    description: 'Google OAuth, signed sessions, strict typing, and environment-driven configuration.',
  },
];

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden px-6 py-8 text-white sm:px-10 lg:px-16">
      <div className="pointer-events-none absolute left-10 top-16 h-48 w-48 rounded-full bg-brand-300/20 blur-3xl animate-float-slow" />
      <div className="pointer-events-none absolute bottom-12 right-8 h-56 w-56 rounded-full bg-cyan-400/20 blur-3xl animate-pulse-soft" />

      <div className="glass-panel mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col justify-between rounded-[2rem] shadow-2xl shadow-black/30">
        <header className="flex items-center justify-between border-b border-white/10 px-6 py-5 sm:px-10">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-brand-200">Axithor Cloud OS</p>
            <p className="mt-1 text-sm text-white/60">Bring Your Own Cloud hosting for static websites</p>
          </div>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-full bg-brand-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-brand-300"
          >
            Connect Google Drive
            <ArrowRight className="h-4 w-4" />
          </Link>
        </header>

        <section className="grid flex-1 gap-10 px-6 py-12 sm:px-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center lg:px-12">
          <div className="max-w-3xl animate-fade-up" style={{ animationDelay: '80ms' }}>
            <p className="mb-5 inline-flex items-center rounded-full border border-brand-300/25 bg-brand-300/10 px-4 py-2 text-sm text-brand-100 animate-pulse-soft">
              Production-grade BYOC platform architecture
            </p>
            <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl">
              Deploy static websites from Google Drive with a cloud control plane built for startups.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-white/70">
              Axithor Cloud OS pairs a Next.js frontend with a FastAPI backend, PostgreSQL, and Google OAuth to manage secure deployments without mock data or placeholder workflows.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                href="/login"
                className="hover-lift inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 font-semibold text-slate-950"
              >
                Start with Google
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/dashboard"
                className="hover-lift inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-6 py-3 font-semibold text-white"
              >
                Open dashboard
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 -z-10 rounded-[2rem] bg-brand-400/20 blur-3xl" />
            <div className="grid gap-4 rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 shadow-glow animate-fade-up" style={{ animationDelay: '160ms' }}>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 hover-lift">
                <p className="text-sm text-white/55">Connected storage</p>
                <p className="mt-2 text-2xl font-semibold">Google Drive</p>
                <p className="mt-2 text-sm text-white/65">Drive folders become deployable site roots.</p>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                {features.map((feature) => {
                  const Icon = feature.icon;
                  return (
                    <div key={feature.title} className="hover-lift rounded-3xl border border-white/10 bg-white/5 p-4">
                      <Icon className="h-5 w-5 text-brand-300" />
                      <h2 className="mt-4 font-semibold text-white">{feature.title}</h2>
                      <p className="mt-2 text-sm leading-6 text-white/65">{feature.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
