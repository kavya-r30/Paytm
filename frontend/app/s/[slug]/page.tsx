'use client';

// Public storefront (I1 /s/:shop, STO-1): mobile-first, no login. GET /v1/public/storefront/{slug}; the Gupta
// fixture stands in when the shop or API is unavailable.
import { useQuery } from '@tanstack/react-query';
import { Clock3, Gift, Minus, Plus, ShoppingBag } from 'lucide-react';
import { use, useMemo, useState } from 'react';
import { Button, Card, Chip, Money, Pill, cx } from '@/components/ui/kit';
import { API_BASE } from '@/lib/api/client';
import type { PublicStorefront } from '@/lib/contracts';
import { publicStorefront } from '@/lib/fixtures/gupta';
import { useI18n } from '@/lib/i18n/react';

async function load(slug: string): Promise<PublicStorefront> {
  const res = await fetch(`${API_BASE}/v1/public/storefront/${encodeURIComponent(slug)}`);
  if (!res.ok) throw new Error(`storefront ${res.status}`);
  return (await res.json()) as PublicStorefront;
}

export default function Storefront({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const { t, money, locale } = useI18n();
  const q = useQuery({ queryKey: ['public/storefront', slug], queryFn: () => load(slug), retry: false });
  const shop = q.data ?? (q.isError ? { ...publicStorefront, slug } : null);
  const [cat, setCat] = useState<string | null>(null);
  const [cart, setCart] = useState<Record<string, number>>({});
  const [placed, setPlaced] = useState(false);
  const [failed, setFailed] = useState(false);

  // STO-2: a public order goes in as a storefront draft (POST /v1/public/storefront/{slug}/orders, no login).
  const placeOrder = async () => {
    const lines = Object.entries(cart)
      .filter(([, n]) => n > 0)
      .map(([item_id, n]) => ({ item_id, qty_milli: n * 1000 }));
    if (!q.data) return setPlaced(true);
    try {
      const res = await fetch(`${API_BASE}/v1/public/storefront/${encodeURIComponent(slug)}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lines }),
      });
      if (!res.ok) throw new Error(String(res.status));
      setPlaced(true);
    } catch {
      setFailed(true);
    }
  };

  const cats = useMemo(() => [...new Set((shop?.items ?? []).map((i) => i.category))], [shop]);
  const items = (shop?.items ?? []).filter((i) => !cat || i.category === cat);
  const total = (shop?.items ?? []).reduce((s, i) => s + (cart[i.item_id] ?? 0) * i.price_paise, 0);
  const count = Object.values(cart).reduce((s, n) => s + n, 0);
  const name = (n: Record<string, string>) => n[locale] ?? n.en ?? Object.values(n)[0] ?? '';
  const add = (id: string, d: number) => setCart((c) => ({ ...c, [id]: Math.max(0, (c[id] ?? 0) + d) }));

  if (!shop) return <main className="p-8 text-center text-body text-ink-3">{t('upi.loading')}</main>;
  return (
    <main className="mx-auto flex min-h-screen max-w-[480px] flex-col bg-ground pb-28">
      <header className="bg-midnight px-5 pb-6 pt-8 text-white">
        <h1 className="text-title">{shop.name}</h1>
        <p className="mt-1 flex items-center gap-1.5 text-meta text-white/70">
          <Clock3 size={14} /> {t('store.hours', { start: shop.hours.start, end: shop.hours.end })}
        </p>
      </header>
      {shop.offers.map((o) => (
        <Card key={o.program_id} className="mx-4 -mt-3 flex items-center gap-3 p-4">
          <Gift className="text-green" />
          <span className="text-body">
            {t('store.offer', { amount: money(o.terms.amount_paise), min: money(o.terms.min_spend_paise) })}
          </span>
        </Card>
      ))}
      <div className="no-scrollbar flex gap-2 overflow-x-auto px-4 py-3">
        <Chip active={!cat} onClick={() => setCat(null)}>
          {t('store.all')}
        </Chip>
        {cats.map((c) => (
          <Chip key={c} active={cat === c} onClick={() => setCat(c)}>
            {t(`bill.cat_${c}`) === `bill.cat_${c}` ? c : t(`bill.cat_${c}`)}
          </Chip>
        ))}
      </div>
      <ul className="flex flex-col gap-2 px-4">
        {items.map((i) => (
          <li
            key={i.item_id}
            className={cx(
              'flex items-center gap-3 rounded-ground bg-white p-3 shadow-1',
              !i.in_stock && 'opacity-50',
            )}
          >
            <span className="flex h-11 w-11 items-center justify-center rounded-ground bg-sky font-extrabold text-midnight">
              {name(i.names).slice(0, 1)}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-body font-bold">{name(i.names)}</span>
              <span className="num text-meta text-ink-3">
                {money(i.price_paise)} / {i.unit}
              </span>
            </span>
            {i.in_stock ? (
              <span className="flex items-center gap-2">
                {(cart[i.item_id] ?? 0) > 0 && (
                  <>
                    <button
                      type="button"
                      aria-label="-"
                      onClick={() => add(i.item_id, -1)}
                      className="rounded-chip bg-ground p-1.5"
                    >
                      <Minus size={16} />
                    </button>
                    <span className="num w-5 text-center font-bold">{cart[i.item_id]}</span>
                  </>
                )}
                <button
                  type="button"
                  aria-label="+"
                  onClick={() => add(i.item_id, 1)}
                  className="rounded-chip bg-paytm-blue p-1.5 text-midnight"
                >
                  <Plus size={16} />
                </button>
              </span>
            ) : (
              <Pill>{t('store.out')}</Pill>
            )}
          </li>
        ))}
      </ul>
      {count > 0 && (
        <div className="fixed bottom-0 left-1/2 w-full max-w-[480px] -translate-x-1/2 p-4">
          {placed ? (
            <Card className="p-4 text-center text-body font-bold text-green">{t('store.placed')}</Card>
          ) : failed ? (
            <Card className="p-4 text-center text-body font-bold text-red">{t('store.failed')}</Card>
          ) : (
            <Button
              size="lg"
              className="w-full"
              icon={<ShoppingBag size={20} />}
              onClick={() => void placeOrder()}
            >
              {t('store.order', { n: count, total: money(total) })}
            </Button>
          )}
        </div>
      )}
      {q.isError && <p className="p-4 text-center text-meta text-ink-3">{t('upi.demo_note')}</p>}
    </main>
  );
}
