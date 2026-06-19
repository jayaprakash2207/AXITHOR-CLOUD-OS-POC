'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, CheckCircle, ExternalLink, Loader2, RefreshCw, XCircle } from 'lucide-react';

import { apiFetch } from '@/lib/api';

interface DeployedFile {
  id: string;
  path: string;
  mime_type: string | null;
  file_size: number | null;
}

interface Site {
  id: string;
  name: string;
  subdomain: string;
  status: string;
}

type AssetStatus = 'pending' | 'ok' | 'error';

interface AssetResult {
  path: string;
  mime_type: string | null;
  file_size: number | null;
  status: AssetStatus;
  http_status?: number;
  latency_ms?: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') ?? 'http://localhost:8000';

function formatBytes(bytes: number | null): string {
  if (bytes == null) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function MimeChip({ mime }: { mime: string | null }) {
  const label = mime?.split(';')[0] ?? 'unknown';
  const color = label.startsWith('text/html') ? 'bg-blue-500/20 text-blue-300'
    : label.startsWith('text/css') ? 'bg-purple-500/20 text-purple-300'
    : label.startsWith('application/javascript') ? 'bg-yellow-500/20 text-yellow-300'
    : label.startsWith('image/') ? 'bg-green-500/20 text-green-300'
    : label.startsWith('font/') ? 'bg-pink-500/20 text-pink-300'
    : 'bg-white/10 text-white/50';
  return (
    <span className={`rounded-full px-2 py-0.5 text-[10px] font-mono font-semibold ${color}`}>
      {label}
    </span>
  );
}

export default function VerifyPage() {
  const { id } = useParams<{ id: string }>();

  const [site, setSite] = useState<Site | null>(null);
  const [results, setResults] = useState<AssetResult[]>([]);
  const [verifying, setVerifying] = useState(false);
  const [verified, setVerified] = useState(false);

  useEffect(() => {
    Promise.all([
      apiFetch(`/sites/${id}`).then(r => r.ok ? r.json() : null),
      apiFetch(`/sites/${id}/files`).then(r => r.ok ? r.json() : []),
    ]).then(([siteData, files]: [Site | null, DeployedFile[]]) => {
      if (siteData) setSite(siteData);
      setResults((files as DeployedFile[]).map(f => ({
        path: f.path,
        mime_type: f.mime_type,
        file_size: f.file_size,
        status: 'pending',
      })));
    });
  }, [id]);

  async function verifyAll() {
    if (!site) return;
    setVerifying(true);
    setVerified(false);

    const updated: AssetResult[] = await Promise.all(
      results.map(async (asset) => {
        const url = `${API_BASE}/serve/${site.subdomain}/${asset.path}`;
        const t0 = performance.now();
        try {
          const resp = await fetch(url, { method: 'HEAD', cache: 'no-store' });
          return {
            ...asset,
            status: resp.ok ? ('ok' as AssetStatus) : ('error' as AssetStatus),
            http_status: resp.status,
            latency_ms: Math.round(performance.now() - t0),
          };
        } catch {
          return { ...asset, status: 'error' as AssetStatus, latency_ms: Math.round(performance.now() - t0) };
        }
      }),
    );

    setResults(updated);
    setVerifying(false);
    setVerified(true);
  }

  const ok = results.filter(r => r.status === 'ok').length;
  const errors = results.filter(r => r.status === 'error').length;
  const pending = results.filter(r => r.status === 'pending').length;

  return (
    <main className="min-h-screen px-6 py-8 text-white sm:px-10 lg:px-16">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <Link href={`/dashboard/sites/${id}`} className="text-white/40 hover:text-white">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="flex-1">
            <p className="text-xs uppercase tracking-widest text-brand-200">Asset Verification</p>
            <h1 className="mt-1 text-2xl font-semibold">{site?.name ?? '…'}</h1>
          </div>
          <button
            onClick={verifyAll}
            disabled={verifying || results.length === 0}
            className="inline-flex items-center gap-2 rounded-xl bg-brand-400 px-5 py-2.5 text-sm font-semibold text-slate-950 hover:bg-brand-300 disabled:opacity-50"
          >
            {verifying ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Verifying…</>
            ) : (
              <><RefreshCw className="h-4 w-4" /> Verify All Assets</>
            )}
          </button>
        </div>

        {/* Site URL */}
        {site && (
          <div className="mb-6 flex items-center gap-4 rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm">
            <span className="text-white/50">Site URL</span>
            <a
              href={`${API_BASE}/serve/${site.subdomain}/`}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 font-mono text-brand-300 hover:underline"
            >
              {API_BASE}/serve/{site.subdomain}/
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        )}

        {/* Summary bar */}
        {verified && (
          <div className="mb-6 grid grid-cols-3 gap-4">
            <div className="rounded-2xl border border-green-500/20 bg-green-500/10 p-4 text-center">
              <p className="text-2xl font-bold text-green-400">{ok}</p>
              <p className="mt-1 text-xs text-green-300/70">Assets OK</p>
            </div>
            <div className={`rounded-2xl border p-4 text-center ${errors > 0 ? 'border-red-500/20 bg-red-500/10' : 'border-white/10 bg-white/5'}`}>
              <p className={`text-2xl font-bold ${errors > 0 ? 'text-red-400' : 'text-white/30'}`}>{errors}</p>
              <p className="mt-1 text-xs text-white/50">Errors</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
              <p className="text-2xl font-bold text-white/60">{results.length}</p>
              <p className="mt-1 text-xs text-white/50">Total Assets</p>
            </div>
          </div>
        )}

        {/* Asset table */}
        <div className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden">
          <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-4 border-b border-white/10 px-5 py-3 text-[11px] font-semibold uppercase tracking-wider text-white/40">
            <span>Path</span>
            <span>Type</span>
            <span>Size</span>
            <span>Status</span>
            <span>ms</span>
          </div>

          {results.length === 0 ? (
            <div className="flex h-32 items-center justify-center text-sm text-white/40">
              No assets found. Deploy a ZIP first.
            </div>
          ) : (
            results.map((asset) => (
              <div
                key={asset.path}
                className="grid grid-cols-[1fr_auto_auto_auto_auto] items-center gap-4 border-b border-white/5 px-5 py-3 last:border-0 hover:bg-white/5"
              >
                <a
                  href={`${API_BASE}/serve/${site?.subdomain ?? ''}/${asset.path}`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 font-mono text-sm text-white/80 hover:text-brand-300"
                >
                  {asset.path}
                  <ExternalLink className="h-3 w-3 shrink-0 opacity-0 group-hover:opacity-100" />
                </a>
                <MimeChip mime={asset.mime_type} />
                <span className="text-xs text-white/40">{formatBytes(asset.file_size)}</span>
                <span>
                  {asset.status === 'ok' && <CheckCircle className="h-4 w-4 text-green-400" />}
                  {asset.status === 'error' && <XCircle className="h-4 w-4 text-red-400" />}
                  {asset.status === 'pending' && <span className="h-4 w-4 rounded-full border border-white/20 inline-block" />}
                </span>
                <span className="text-xs text-white/30">
                  {asset.latency_ms != null ? `${asset.latency_ms}ms` : '—'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
