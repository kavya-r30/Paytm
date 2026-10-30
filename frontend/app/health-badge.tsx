'use client';

import { useEffect, useState } from 'react';
import type { components } from '@/lib/contracts/api';

type Health = components['schemas']['Health'];

export function HealthBadge() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
    fetch(`${base}/healthz`)
      .then((r) => r.json() as Promise<Health>)
      .then(setHealth)
      .catch((e: unknown) => setError(String(e)));
  }, []);

  if (error) return <p className="text-red">API unreachable: {error}</p>;
  if (!health) return <p className="text-ink-3">Checking API…</p>;
  return (
    <p className="text-green">
      API {health.status} · mode {health.mode} · sim clock {health.clock} · packs {health.packs.join(', ')}
    </p>
  );
}
