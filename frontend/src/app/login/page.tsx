import Link from 'next/link';
import { ArrowRight, LogIn, ShieldCheck } from 'lucide-react';

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export default function LoginPage() {
  return (
    <main className="grid min-h-screen place-items-center px-6 py-12 text-white">
      <div className="w-full max-w-md rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center gap-3 text-brand-200">
          <ShieldCheck className="h-5 w-5" />
          <span className="text-xs uppercase tracking-[0.3em]">Authentication</span>
        </div>
        <h1 className="mt-4 text-3xl font-semibold">Sign in to Axithor Cloud OS</h1>
        <p className="mt-3 text-sm leading-6 text-white/65">
          Use Google to create or sign in to your account. The backend verifies the OAuth response and issues access and refresh cookies.
        </p>

        <a
          href={`${apiBaseUrl}/auth/google/login`}
          className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-full bg-brand-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-brand-300"
        >
          <LogIn className="h-4 w-4" />
          Continue with Google
          <ArrowRight className="h-4 w-4" />
        </a>

        <div className="mt-6 flex items-center justify-between text-sm text-white/50">
          <Link href="/" className="hover:text-white/80">
            Back to home
          </Link>
          <Link href="/dashboard" className="hover:text-white/80">
            Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}