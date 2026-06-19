'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle,
  CloudUpload,
  FileArchive,
  Loader2,
  Upload,
  XCircle,
} from 'lucide-react';

import { apiFetch } from '@/lib/api';

interface Site {
  id: string;
  name: string;
  subdomain: string;
  status: string;
}

interface DeploymentResult {
  site_id: string;
  status: string;
  files_deployed: number;
  deployment_id: string;
  created_at: string;
}

type UploadState = 'idle' | 'uploading' | 'success' | 'error';

export default function DeployPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedSiteId = searchParams.get('site');

  const [sites, setSites] = useState<Site[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>(preselectedSiteId ?? '');
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<UploadState>('idle');
  const [result, setResult] = useState<DeploymentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    apiFetch('/sites')
      .then((r) => r.json())
      .then((data: Site[]) => {
        setSites(data);
        if (!selectedSiteId && data.length > 0) setSelectedSiteId(data[0].id);
      })
      .catch(() => {});
  }, []);

  const handleFile = useCallback((f: File) => {
    if (!f.name.endsWith('.zip')) {
      setError('Only .zip files are accepted.');
      return;
    }
    setFile(f);
    setError(null);
    setState('idle');
    setResult(null);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile],
  );

  async function deploy() {
    if (!file || !selectedSiteId) return;
    setState('uploading');
    setError(null);
    setResult(null);

    const form = new FormData();
    form.append('zip_file', file);

    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';
    try {
      const res = await fetch(`${apiBase}/sites/${selectedSiteId}/deploy`, {
        method: 'POST',
        credentials: 'include',
        body: form,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(body.detail ?? 'Deployment failed');
      }

      const data = (await res.json()) as DeploymentResult;
      setResult(data);
      setState('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Deployment failed');
      setState('error');
    }
  }

  const selectedSite = sites.find((s) => s.id === selectedSiteId);

  return (
    <main className="min-h-screen px-6 py-8 text-white sm:px-10 lg:px-16">
      <div className="mx-auto max-w-2xl">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <Link href="/dashboard" className="text-white/40 hover:text-white">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <p className="text-xs uppercase tracking-widest text-brand-200">Deploy</p>
            <h1 className="mt-1 text-2xl font-semibold">Upload ZIP</h1>
          </div>
        </div>

        <div className="space-y-6">
          {/* Site selector */}
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
            <label className="mb-3 block text-sm font-medium text-white/70">Target Site</label>
            {sites.length === 0 ? (
              <p className="text-sm text-white/40">
                No sites found.{' '}
                <Link href="/dashboard" className="text-brand-300 hover:underline">
                  Create one first.
                </Link>
              </p>
            ) : (
              <select
                value={selectedSiteId}
                onChange={(e) => setSelectedSiteId(e.target.value)}
                className="w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2.5 text-sm text-white outline-none focus:border-brand-400"
              >
                {sites.map((s) => (
                  <option key={s.id} value={s.id} className="bg-slate-900">
                    {s.name} ({s.subdomain}.axithor.tech)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Drop zone */}
          <div
            className={`flex cursor-pointer flex-col items-center justify-center rounded-[2rem] border-2 border-dashed p-12 transition ${
              dragOver
                ? 'border-brand-400 bg-brand-400/10'
                : file
                  ? 'border-green-500/50 bg-green-500/5'
                  : 'border-white/20 bg-white/5 hover:border-white/40'
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".zip"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
            {file ? (
              <>
                <FileArchive className="h-12 w-12 text-green-400" />
                <p className="mt-4 font-medium text-white">{file.name}</p>
                <p className="mt-1 text-sm text-white/40">
                  {(file.size / 1024 / 1024).toFixed(2)} MB — click to change
                </p>
              </>
            ) : (
              <>
                <CloudUpload className="h-12 w-12 text-white/30" />
                <p className="mt-4 text-white/60">Drag & drop your ZIP here</p>
                <p className="mt-1 text-sm text-white/40">or click to browse</p>
                <p className="mt-4 text-xs text-white/30">
                  Must contain index.html · Max 100 MB
                </p>
              </>
            )}
          </div>

          {/* Requirements */}
          <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm text-white/50">
            <p className="font-medium text-white/70">ZIP Requirements</p>
            <ul className="mt-2 space-y-1">
              <li>• Must contain an index.html at the root</li>
              <li>• Supported: HTML, CSS, JS, images, fonts, audio, video</li>
              <li>• Maximum size: 100 MB per deploy</li>
            </ul>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-3 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-200">
              <XCircle className="mt-0.5 h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Success */}
          {result && (
            <div className="rounded-2xl border border-green-500/30 bg-green-500/10 px-5 py-4 text-sm text-green-200">
              <div className="flex items-center gap-2 font-semibold">
                <CheckCircle className="h-4 w-4" />
                Deployment successful
              </div>
              <p className="mt-2 text-green-300/70">
                {result.files_deployed} files deployed to{' '}
                <a
                  href={`https://${selectedSite?.subdomain}.axithor.tech`}
                  target="_blank"
                  rel="noreferrer"
                  className="underline"
                >
                  {selectedSite?.subdomain}.axithor.tech
                </a>
              </p>
              <Link
                href={`/dashboard/sites/${result.site_id}`}
                className="mt-3 inline-block text-xs text-green-400 hover:underline"
              >
                View site details →
              </Link>
            </div>
          )}

          {/* Deploy button */}
          <button
            disabled={!file || !selectedSiteId || state === 'uploading'}
            onClick={deploy}
            className="flex w-full items-center justify-center gap-2 rounded-2xl bg-brand-400 py-3 text-sm font-semibold text-slate-950 transition hover:bg-brand-300 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {state === 'uploading' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Deploying…
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Deploy
              </>
            )}
          </button>
        </div>
      </div>
    </main>
  );
}
