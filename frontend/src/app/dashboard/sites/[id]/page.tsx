'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle,
  Clock,
  ExternalLink,
  FileText,
  Globe,
  RefreshCw,
  Upload,
  XCircle,
} from 'lucide-react';

import { apiFetch } from '@/lib/api';

interface Site {
  id: string;
  name: string;
  subdomain: string;
  status: string;
  created_at: string;
}

interface DeployedFile {
  id: string;
  path: string;
  provider_file_id: string;
  mime_type: string | null;
  file_size: number | null;
  created_at: string;
}

interface Deployment {
  id: string;
  site_id: string;
  status: string;
  error_message: string | null;
  created_at: string;
  finished_at: string | null;
}

interface FileMetadata {
  id: string;
  path: string;
  provider: string;
  checksum: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

const STATUS_ICON: Record<string, React.ReactNode> = {
  success: <CheckCircle className="h-4 w-4 text-green-400" />,
  deployed: <CheckCircle className="h-4 w-4 text-green-400" />,
  failed: <XCircle className="h-4 w-4 text-red-400" />,
  pending: <Clock className="h-4 w-4 text-yellow-400" />,
  draft: <Clock className="h-4 w-4 text-white/40" />,
};

function formatBytes(bytes: number | null): string {
  if (bytes == null) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function SiteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const siteId = params.id as string;

  const [site, setSite] = useState<Site | null>(null);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [files, setFiles] = useState<DeployedFile[]>([]);
  const [metadata, setMetadata] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'files' | 'deployments' | 'metadata'>('files');

  async function fetchAll() {
    setLoading(true);
    const [siteRes, deploymentsRes, filesRes, metaRes] = await Promise.all([
      apiFetch(`/sites/${siteId}`).catch(() => null),
      apiFetch(`/sites/${siteId}/deployments`).catch(() => null),
      apiFetch(`/sites/${siteId}/files`).catch(() => null),
      apiFetch(`/sites/${siteId}/metadata`).catch(() => null),
    ]);

    if (siteRes?.ok) setSite(await siteRes.json());
    if (deploymentsRes?.ok) setDeployments(await deploymentsRes.json());
    if (filesRes?.ok) setFiles(await filesRes.json());
    if (metaRes?.ok) setMetadata(await metaRes.json());
    setLoading(false);
  }

  useEffect(() => {
    fetchAll();
  }, [siteId]);

  if (loading) {
    return (
      <main className="flex h-screen items-center justify-center">
        <span className="text-white/40">Loading site...</span>
      </main>
    );
  }

  if (!site) {
    return (
      <main className="flex h-screen flex-col items-center justify-center gap-4">
        <p className="text-white/60">Site not found.</p>
        <Link href="/dashboard" className="text-sm text-brand-300 hover:underline">
          Back to Dashboard
        </Link>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-8 text-white sm:px-10 lg:px-16">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <Link href="/dashboard" className="text-white/40 hover:text-white">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="flex-1">
            <p className="text-xs uppercase tracking-widest text-brand-200">Site Detail</p>
            <h1 className="mt-1 text-2xl font-semibold">{site.name}</h1>
          </div>
          <div className="flex items-center gap-2">
            {STATUS_ICON[site.status] ?? <Clock className="h-4 w-4 text-white/40" />}
            <span className="rounded-full bg-white/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white/60">
              {site.status}
            </span>
          </div>
        </div>

        {/* Info bar */}
        <div className="mb-8 flex flex-wrap items-center gap-6 rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm">
          <div className="flex items-center gap-2 text-white/60">
            <Globe className="h-4 w-4" />
            <span>{site.subdomain}.axithor.tech</span>
          </div>
          <a
            href={`${process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') ?? 'http://localhost:8000'}/serve/${site.subdomain}/`}
            target="_blank"
            rel="noreferrer"
            className="ml-auto inline-flex items-center gap-1 text-brand-300 hover:underline"
          >
            Visit site <ExternalLink className="h-3 w-3" />
          </a>
          <Link
            href={`/dashboard/deploy?site=${siteId}`}
            className="inline-flex items-center gap-2 rounded-xl bg-brand-400 px-4 py-2 text-xs font-semibold text-slate-950 hover:bg-brand-300"
          >
            <Upload className="h-3 w-3" />
            Deploy ZIP
          </Link>
          <button
            onClick={fetchAll}
            className="inline-flex items-center gap-1 rounded-xl bg-white/10 px-4 py-2 text-xs font-semibold hover:bg-white/15"
          >
            <RefreshCw className="h-3 w-3" />
            Refresh
          </button>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-1 rounded-2xl border border-white/10 bg-white/5 p-1">
          {(['files', 'deployments', 'metadata'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 rounded-xl py-2 text-sm font-medium capitalize transition ${
                activeTab === tab
                  ? 'bg-brand-400 text-slate-950'
                  : 'text-white/50 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === 'files' && (
          <div className="space-y-2">
            {files.length === 0 ? (
              <div className="flex h-48 flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-center">
                <FileText className="h-8 w-8 text-white/20" />
                <p className="mt-3 text-sm text-white/40">No files deployed yet.</p>
              </div>
            ) : (
              files.map((f) => (
                <div
                  key={f.id}
                  className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-5 py-3"
                >
                  <span className="font-mono text-sm text-white/80">{f.path}</span>
                  <div className="flex items-center gap-4 text-xs text-white/40">
                    <span>{f.mime_type ?? '—'}</span>
                    <span>{formatBytes(f.file_size)}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'deployments' && (
          <div className="space-y-3">
            {deployments.length === 0 ? (
              <div className="flex h-48 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                <p className="text-sm text-white/40">No deployments yet.</p>
              </div>
            ) : (
              deployments.map((d) => (
                <div
                  key={d.id}
                  className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 px-5 py-4"
                >
                  <div className="mt-0.5">
                    {STATUS_ICON[d.status] ?? <Clock className="h-4 w-4 text-white/40" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-medium capitalize">{d.status}</span>
                      <span className="text-xs text-white/40">
                        {new Date(d.created_at).toLocaleString()}
                      </span>
                    </div>
                    {d.error_message && (
                      <p className="mt-1 text-xs text-red-400">{d.error_message}</p>
                    )}
                  </div>
                  <span className="font-mono text-[10px] text-white/30">
                    {d.id.slice(0, 8)}
                  </span>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="space-y-2">
            {metadata.length === 0 ? (
              <div className="flex h-48 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                <p className="text-sm text-white/40">No metadata available.</p>
              </div>
            ) : (
              metadata.map((m) => (
                <div
                  key={m.id}
                  className="rounded-xl border border-white/10 bg-white/5 px-5 py-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/80">{m.path}</span>
                    <span className="rounded-full bg-brand-400/20 px-2 py-0.5 text-[10px] font-bold text-brand-300">
                      v{m.version}
                    </span>
                  </div>
                  {m.checksum && (
                    <p className="mt-1 font-mono text-[10px] text-white/30">
                      sha256: {m.checksum.slice(0, 20)}…
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </main>
  );
}
