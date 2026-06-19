'use client';

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

import { apiFetch } from '@/lib/api';

interface SiteFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

function toSlug(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 63);
}

export function SiteForm({ open, onClose, onSuccess }: SiteFormProps) {
  const [name, setName] = useState('');
  const [subdomain, setSubdomain] = useState('');
  const [subdomainTouched, setSubdomainTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!subdomainTouched) {
      setSubdomain(toSlug(name));
    }
  }, [name, subdomainTouched]);

  useEffect(() => {
    if (open) {
      setName('');
      setSubdomain('');
      setSubdomainTouched(false);
      setError(null);
    }
  }, [open]);

  if (!open) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await apiFetch('/sites', {
        method: 'POST',
        body: JSON.stringify({ name, subdomain }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Failed to create site' }));
        const detail = err.detail;
        const message = typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((e: { msg: string }) => e.msg).join(', ')
            : 'Failed to create site';
        throw new Error(message);
      }

      onSuccess();
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create site');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-md rounded-[2rem] border border-white/10 bg-[#0d1f1a] p-8 shadow-2xl">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Create New Site</h2>
            <p className="mt-1 text-sm text-white/50">
              Give it a name — you can upload files after.
            </p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 rounded-xl p-1.5 text-white/40 hover:bg-white/10 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </p>
          )}

          <div>
            <label className="mb-1.5 block text-sm font-medium text-white/70">
              Site Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={2}
              maxLength={255}
              placeholder="My Portfolio"
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-white placeholder-white/30 focus:border-brand-400 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-white/70">
              Subdomain
            </label>
            <div className="flex items-stretch">
              <input
                type="text"
                value={subdomain}
                onChange={(e) => {
                  setSubdomainTouched(true);
                  setSubdomain(toSlug(e.target.value));
                }}
                required
                minLength={3}
                maxLength={63}
                placeholder="my-portfolio"
                className="w-full rounded-l-xl border border-white/10 bg-white/5 px-4 py-2.5 text-white placeholder-white/30 focus:border-brand-400 focus:outline-none"
              />
              <span className="flex items-center rounded-r-xl border border-l-0 border-white/10 bg-white/10 px-4 text-sm text-white/50 whitespace-nowrap">
                .axithor.tech
              </span>
            </div>
            {subdomain && subdomain.length >= 3 && (
              <p className="mt-1.5 text-xs text-white/40">
                Your site will be at{' '}
                <span className="text-brand-300">{subdomain}.axithor.tech</span>
              </p>
            )}
            {subdomain && subdomain.length < 3 && (
              <p className="mt-1.5 text-xs text-red-400">
                Subdomain must be at least 3 characters
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || !name || !subdomain}
            className="w-full rounded-xl bg-brand-400 py-3 font-semibold text-slate-950 transition hover:bg-brand-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Creating…' : 'Create Site'}
          </button>
        </form>
      </div>
    </div>
  );
}
