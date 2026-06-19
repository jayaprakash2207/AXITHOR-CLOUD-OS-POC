'use client';

interface StorageAccount {
  id: string;
  user_id: string;
  provider: string;
  quota: string | null;
  created_at: string;
}

interface DriveStatusCardProps {
  account: StorageAccount | null;
  loading: boolean;
  onRefresh: () => void;
}

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export function DriveStatusCard({ account, loading, onRefresh }: DriveStatusCardProps) {
  async function disconnect() {
    const response = await fetch(`${apiBaseUrl}/storage/disconnect`, {
      method: 'POST',
      credentials: 'include',
    });
    if (response.ok) {
      onRefresh();
    }
  }

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-brand-200">Google Drive</p>
          <h2 className="mt-2 text-xl font-semibold">Drive Status</h2>
        </div>
        {account ? (
          <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
            Connected
          </span>
        ) : (
          <span className="rounded-full bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-200">
            Not connected
          </span>
        )}
      </div>

      <div className="mt-6 space-y-3 text-sm text-white/70">
        <p>Provider: {account?.provider ?? 'google_drive'}</p>
        <p>Quota snapshot: {account?.quota ? 'Stored' : 'Unavailable'}</p>
        <p>Connected at: {account?.created_at ? new Date(account.created_at).toLocaleString() : 'Not yet connected'}</p>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <a
          href={`${apiBaseUrl}/storage/google/login`}
          className="inline-flex items-center justify-center rounded-full bg-brand-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-brand-300"
        >
          {account ? 'Reconnect Drive' : 'Connect Drive'}
        </a>
        {account ? (
          <button
            type="button"
            onClick={() => void disconnect()}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10 disabled:opacity-50"
          >
            Disconnect
          </button>
        ) : null}
      </div>
    </section>
  );
}