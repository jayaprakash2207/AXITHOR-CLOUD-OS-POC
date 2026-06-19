'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ExternalLink, Globe, Layout, Plus } from 'lucide-react';

import { SiteForm } from '@/components/SiteForm';
import { apiFetch } from '@/lib/api';
import { DriveStatusCard } from '@/components/storage/drive-status-card';
import { StorageUsageWidget } from '@/components/storage/storage-usage-widget';
import { Upload } from 'lucide-react';

interface Site {
  id: string;
  name: string;
  subdomain: string;
  status: string;
  created_at: string;
}

interface StorageAccount {
  id: string;
  user_id: string;
  provider: string;
  quota: string | null;
  created_at: string;
}

interface StorageUsage {
  storage_quota: Record<string, number | string | null>;
  drive_metadata: Record<string, string | number | null>;
}

export default function DashboardPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [storageAccount, setStorageAccount] = useState<StorageAccount | null>(null);
  const [storageUsage, setStorageUsage] = useState<StorageUsage | null>(null);
  const [storageLoading, setStorageLoading] = useState(true);

  async function fetchSites() {
    setError(null);
    try {
      const res = await apiFetch('/sites');
      if (!res.ok) {
        throw new Error('Unable to load sites');
      }
      const data = (await res.json()) as Site[];
      setSites(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load sites');
    } finally {
      setLoading(false);
    }
  }

  async function fetchStorage() {
    setStorageLoading(true);
    try {
      const accountResponse = await apiFetch('/storage/me');
      if (accountResponse.ok) {
        setStorageAccount((await accountResponse.json()) as StorageAccount);
        const usageResponse = await apiFetch('/storage/usage');
        if (usageResponse.ok) {
          setStorageUsage((await usageResponse.json()) as StorageUsage);
        } else {
          setStorageUsage(null);
        }
      } else if (accountResponse.status === 404) {
        setStorageAccount(null);
        setStorageUsage(null);
      }
    } finally {
      setStorageLoading(false);
    }
  }

  useEffect(() => {
    fetchSites();
    void fetchStorage();
  }, []);

  return (
    <main className="relative min-h-screen overflow-hidden px-6 py-8 text-white sm:px-10 lg:px-16">
      <div className="pointer-events-none absolute left-[-5rem] top-[-4rem] h-56 w-56 rounded-full bg-brand-300/15 blur-3xl animate-float-slow" />
      <div className="pointer-events-none absolute bottom-10 right-6 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl animate-pulse-soft" />

      <div className="mx-auto max-w-6xl">
        <header className="mb-10 flex items-center justify-between animate-fade-up">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-brand-200">Axithor Cloud OS</p>
            <h1 className="mt-2 text-3xl font-semibold">Dashboard</h1>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="hover-lift inline-flex items-center gap-2 rounded-full bg-brand-400 px-5 py-2.5 text-sm font-semibold text-slate-950"
          >
            <Plus className="h-4 w-4" />
            New Site
          </button>
        </header>

        <div className="grid gap-10 lg:grid-cols-[1fr_350px]">
          <div className="space-y-6">
            {error ? (
              <div className="rounded-[2rem] border border-red-500/30 bg-red-500/10 p-6 text-sm text-red-200">
                {error}
              </div>
            ) : null}

            {loading ? (
              <div className="glass-panel flex h-64 items-center justify-center rounded-[2rem]">
                <span className="text-white/40">Loading sites...</span>
              </div>
            ) : sites.length === 0 ? (
              <div className="glass-panel flex h-64 flex-col items-center justify-center rounded-[2rem] text-center animate-fade-up">
                <Globe className="h-10 w-10 text-white/20" />
                <p className="mt-4 text-white/60">No sites deployed yet.</p>
                <button
                  onClick={() => setShowForm(true)}
                  className="mt-6 text-sm font-medium text-brand-300 hover:underline"
                >
                  Create your first site
                </button>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {sites.map((site) => (
                  <div
                    key={site.id}
                    className="group glass-panel hover-lift rounded-[2rem] p-6 hover:border-brand-400/50 hover:bg-white/10"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-400/10 text-brand-400">
                        <Layout className="h-5 w-5" />
                      </div>
                      <span className="rounded-full bg-white/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white/60">
                        {site.status}
                      </span>
                    </div>
                    <h3 className="mt-4 text-xl font-semibold">{site.name}</h3>
                    <p className="mt-1 text-sm text-white/50">{site.subdomain}.axithor.com</p>
                    <div className="mt-6 flex items-center gap-3">
                      <a
                        href={`${process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') ?? 'http://localhost:8000'}/serve/${site.subdomain}/`}
                        target="_blank"
                        rel="noreferrer"
                        className="hover-lift inline-flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2 text-xs font-semibold hover:bg-white/15"
                      >
                        Visit
                        <ExternalLink className="h-3 w-3" />
                      </a>
                      <Link
                        href={`/dashboard/deploy?site=${site.id}`}
                        className="hover-lift inline-flex items-center gap-2 rounded-xl bg-brand-400/20 px-4 py-2 text-xs font-semibold text-brand-300 hover:bg-brand-400/30"
                      >
                        <Upload className="h-3 w-3" />
                        Deploy
                      </Link>
                      <Link
                        href={`/dashboard/sites/${site.id}`}
                        className="ml-auto text-xs text-white/40 hover:text-white"
                      >
                        Details →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <aside className="space-y-6">
            <DriveStatusCard
              account={storageAccount}
              loading={storageLoading}
              onRefresh={() => {
                void fetchStorage();
              }}
            />

            <StorageUsageWidget usage={storageUsage} loading={storageLoading} />

            <div className="glass-panel rounded-[2rem] p-8">
              <h2 className="font-semibold">Quick Start</h2>
              <ul className="mt-4 space-y-4 text-sm text-white/60">
                <li className="flex gap-3">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />
                  Click <span className="text-white/80">+ New Site</span> to create a site.
                </li>
                <li className="flex gap-3">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />
                  Then click <span className="text-white/80">Deploy</span> on the site card to upload a ZIP.
                </li>
                <li className="flex gap-3">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />
                  Sites are served at <span className="text-brand-300">subdomain.axithor.tech</span>.
                </li>
              </ul>
            </div>
          </aside>
        </div>
      </div>

      <SiteForm
        open={showForm}
        onClose={() => setShowForm(false)}
        onSuccess={() => {
          void fetchSites();
        }}
      />
    </main>
  );
}
