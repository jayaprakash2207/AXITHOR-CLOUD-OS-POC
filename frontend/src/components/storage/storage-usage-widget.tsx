'use client';

interface StorageUsageProps {
  usage: {
    storage_quota: Record<string, number | string | null>;
    drive_metadata: Record<string, string | number | null>;
  } | null;
  loading: boolean;
}

function formatBytes(value: number | null | undefined) {
  if (value === null || value === undefined) return 'Unknown';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = value;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

export function StorageUsageWidget({ usage, loading }: StorageUsageProps) {
  const limitValue = Number(usage?.storage_quota.limit ?? 0);
  const usageValue = Number(usage?.storage_quota.usage ?? 0);
  const limit = Number.isFinite(limitValue) ? limitValue : 0;
  const usageBytes = Number.isFinite(usageValue) ? usageValue : 0;
  const percent = limit > 0 ? Math.min((usageBytes / limit) * 100, 100) : 0;

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
      <p className="text-xs uppercase tracking-[0.25em] text-brand-200">Storage usage</p>
      <h2 className="mt-2 text-xl font-semibold">Drive Storage Widget</h2>

      {loading ? (
        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-white/50">Loading usage...</div>
      ) : usage ? (
        <div className="mt-6 space-y-5">
          <div>
            <div className="mb-2 flex items-center justify-between text-sm text-white/65">
              <span>{formatBytes(usageBytes)} used</span>
              <span>{formatBytes(limit)} total</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-gradient-to-r from-brand-300 to-brand-500" style={{ width: `${percent}%` }} />
            </div>
          </div>

          <div className="grid gap-3 text-sm text-white/65">
            <p>Usage percent: {percent.toFixed(1)}%</p>
            <p>Root folder: {String(usage.drive_metadata.rootFolderId ?? 'Unknown')}</p>
            <p>Account name: {String(usage.drive_metadata.displayName ?? 'Unknown')}</p>
            <p>Email: {String(usage.drive_metadata.emailAddress ?? 'Unknown')}</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-white/50">
          Connect Google Drive to retrieve quota and metadata.
        </div>
      )}
    </section>
  );
}