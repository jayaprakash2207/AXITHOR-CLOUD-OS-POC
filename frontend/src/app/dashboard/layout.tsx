import Link from 'next/link';

export default function DashboardLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen text-white">
      <header className="border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-10">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-brand-200">Axithor Cloud OS</p>
            <p className="text-sm text-white/60">Module 1 authentication and user management</p>
          </div>
          <nav className="flex items-center gap-3 text-sm">
            <Link href="/dashboard" className="hover-lift rounded-full border border-white/10 px-4 py-2 text-white/75 hover:bg-white/10">
              Dashboard
            </Link>
            <a
              href={`${process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1'}/auth/logout`}
              className="hover-lift rounded-full bg-white px-4 py-2 font-semibold text-slate-950 hover:bg-brand-100"
            >
              Logout
            </a>
          </nav>
        </div>
      </header>
      {children}
    </div>
  );
}