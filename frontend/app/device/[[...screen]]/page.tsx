'use client';

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Empty, Loading } from '@/components/shell/device';
import { Button } from '@/components/ui/kit';
import { apiGet } from '@/lib/api/client';
import { useDataMode } from '@/lib/api/hooks';
import { useI18n } from '@/lib/i18n/react';
import { resolveScreen } from '@/screens/device/registry';

/**
 * Detail screens opened without an id (from the rail, a voice "nav", the dev index) open the shop's newest
 * record of that kind (`GET /v1/views/latest/{kind}`); the fixture shop keeps its own ids. A shop with no
 * such record yet gets the designed empty state instead of a "not found" error.
 */
const LATEST: Record<string, { kind: string; path: (id: string) => string }> = {
  pay: { kind: 'bill_open', path: (id) => `bill/${id}/pay` },
  paid: { kind: 'bill_closed', path: (id) => `bill/${id}/paid` },
  return: { kind: 'bill_closed', path: (id) => `return/${id}` },
  verdict: { kind: 'verdict', path: (id) => `verdict/${id}` },
  order: { kind: 'order', path: (id) => `order/${id}` },
  patron: { kind: 'patron', path: (id) => `patron/${id}` },
  item: { kind: 'item', path: (id) => `item/${id}` },
  po: { kind: 'po', path: (id) => `po/${id}` },
  gate: { kind: 'gate', path: (id) => `gate/${id}` },
  grn: { kind: 'po', path: (id) => `grn/${id}` },
  claim: { kind: 'claim', path: (id) => `claim/${id}` },
  plan: { kind: 'plan', path: (id) => `plan/${id}` },
  offer: { kind: 'offer', path: (id) => `offer/${id}` },
  campaign: { kind: 'campaign', path: (id) => `campaign/${id}` },
  run: { kind: 'run', path: (id) => `run/${id}` },
};

function LatestRecord({ screen }: { screen: string }) {
  const router = useRouter();
  const { t } = useI18n();
  const [none, setNone] = useState(false);
  useEffect(() => {
    const target = LATEST[screen]!;
    let live = true;
    void apiGet(`/v1/views/latest/${target.kind}`)
      .then((body) => {
        const id = (body as { id: string | null }).id;
        if (!live) return;
        if (id) router.replace(`/device/${target.path(id)}${window.location.search}`);
        else setNone(true);
      })
      .catch(() => live && setNone(true));
    return () => {
      live = false;
    };
  }, [router, screen]);
  if (!none) return <Loading />;
  return (
    <div className="flex h-full items-center justify-center">
      <Empty
        title={t('state.none_title')}
        body={t('state.none_body')}
        action={
          <Button variant="dark" onClick={() => router.push(`/device/home${window.location.search}`)}>
            {t('nav.home')}
          </Button>
        }
      />
    </div>
  );
}

// One route for every device screen: /device/<screen>/<param?>. Envelope `nav.screen` maps here directly.
export default function DevicePage({ params }: { params: Promise<{ screen?: string[] }> }) {
  const { screen = [] } = use(params);
  const mode = useDataMode();
  const { Component, param } = resolveScreen(screen);
  const name = screen[0] ?? 'home';
  if (mode === 'live' && !param && name in LATEST) return <LatestRecord screen={name} />;
  return <Component param={param} />;
}
