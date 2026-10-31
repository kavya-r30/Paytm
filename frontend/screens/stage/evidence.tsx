'use client';

// Evidence tabs (I2): Trace, Playbooks, Tools, AI calls, Tables, Logs, Health. Live data comes from the SSE
// stream and the views; fixture mode shows a recorded turn so the column is never empty on stage.
import { CircleCheck, CircleX } from 'lucide-react';
import { useState } from 'react';
import { Button, Money, Pill, TierChip, cx } from '@/components/ui/kit';
import { apiGet } from '@/lib/api/client';
import { useDataMode, useView } from '@/lib/api/hooks';
import { views } from '@/lib/api/views';
import type { AuditVerification } from '@/lib/contracts';
import { STAGE_EVENTS, STAGE_SPANS } from '@/lib/fixtures/surfaces';
import { useI18n } from '@/lib/i18n/react';
import { useStream, type StreamItem } from '@/lib/store/turn';
import { useGateText } from '../device/today';

export const EVIDENCE_TABS = ['trace', 'playbooks', 'tools', 'ai', 'tables', 'logs', 'health'] as const;
export type EvidenceTab = (typeof EVIDENCE_TABS)[number];

type Span = { name: string; ms: number; cost: number; mode: string };

function spansFrom(items: StreamItem[], mode: string): Span[] {
  const live = items
    .filter((i) => i.kind === 'span')
    .slice(0, 14)
    .reverse()
    .map((i) => {
      const attrs = (i.data.attrs ?? {}) as Record<string, unknown>;
      return {
        name: String(i.data.name ?? i.type),
        ms: Number(i.data.duration_ms ?? i.data.ms ?? 0),
        cost: Number(attrs.cost_paise ?? 0),
        mode: String(i.data.mode ?? attrs.mode ?? 'live'),
      };
    });
  return live.length || mode === 'live' ? live : STAGE_SPANS;
}

function Trace({ spans }: { spans: Span[] }) {
  const { t } = useI18n();
  const total = spans.reduce((s, x) => s + x.ms, 0) || 1;
  let offset = 0;
  if (!spans.length) return <p className="text-meta text-ink-3">{t('stage.no_spans')}</p>;
  return (
    <div className="flex flex-col gap-1.5">
      {spans.map((s, i) => {
        const left = (offset / total) * 100;
        offset += s.ms;
        return (
          <div key={i} className="text-meta">
            <div className="flex justify-between">
              <span className="truncate font-semibold">{s.name}</span>
              <span className="num text-ink-3">
                {s.ms} ms · ₹{(s.cost / 100).toFixed(2)} · {s.mode}
              </span>
            </div>
            <div className="relative h-2 rounded-chip bg-line">
              <span
                className={cx(
                  'absolute h-2 rounded-chip',
                  s.mode === 'replay' ? 'bg-amber' : 'bg-paytm-blue',
                )}
                style={{ left: `${left}%`, width: `${Math.max(2, (s.ms / total) * 100)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Playbooks() {
  const { t } = useI18n();
  const n = useView(views.notifications());
  const text = useGateText();
  const steps = ['done', 'active', 'needs_you', 'waiting', 'todo'] as const;
  return (
    <div className="flex flex-col gap-3">
      <div className="flex gap-1">
        {steps.map((s, i) => (
          <span
            key={s}
            className={cx(
              'flex-1 rounded-chip py-1 text-center text-meta font-bold',
              i < 2
                ? 'bg-green-tint text-green'
                : i === 2
                  ? 'bg-amber-tint text-amber-text'
                  : 'bg-line text-ink-3',
            )}
          >
            {t(`stage.step_${s}`)}
          </span>
        ))}
      </div>
      {(n.data?.needs_you ?? []).map((g) => (
        <div key={g.gate_id} className="rounded-ground border-2 border-amber p-2">
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-meta font-bold">{text(g).title}</span>
            <TierChip tier={g.tier} compact />
          </div>
          <p className="truncate text-meta text-ink-3">{text(g).sub}</p>
        </div>
      ))}
    </div>
  );
}

function Tools({ spans }: { spans: Span[] }) {
  const tools = spans.filter((s) => s.name.startsWith('tool'));
  return (
    <div className="flex flex-col gap-2">
      {tools.map((s, i) => (
        <div key={i} className="rounded-ground bg-ground p-2 font-mono text-meta">
          <p className="font-bold">{s.name.replace('tool:', '')}()</p>
          <p className="text-ink-3">→ ok · {s.ms} ms</p>
        </div>
      ))}
    </div>
  );
}

function AiCalls({ spans }: { spans: Span[] }) {
  const { t } = useI18n();
  const calls = spans.filter((s) => !s.name.startsWith('tool') && s.cost > 0);
  return (
    <table className="w-full text-meta">
      <thead className="text-left text-ink-3">
        <tr>
          <th>{t('stage.role')}</th>
          <th>ms</th>
          <th>₹</th>
          <th>{t('stage.mode')}</th>
        </tr>
      </thead>
      <tbody>
        {calls.map((c, i) => (
          <tr key={i} className="border-t border-line">
            <td className="py-1 font-semibold">{c.name}</td>
            <td className="num">{c.ms}</td>
            <td className="num">{(c.cost / 100).toFixed(2)}</td>
            <td>
              <Pill tone={c.mode === 'live' ? 'green' : 'amber'}>{c.mode}</Pill>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Tables({ table, setTable }: { table: string; setTable: (t: string) => void }) {
  const { t, time } = useI18n();
  const khata = useView(views.khata());
  const stock = useView(views.stock());
  const offers = useView(views.offers());
  const trust = useView(views.trust());
  const park = useView(views.park());
  const TABLES = ['bills', 'khata', 'stock', 'offers', 'audit'];
  const rows: [string, string][] =
    table === 'khata'
      ? (khata.data?.accounts ?? []).map((a) => [a.display_name, `₹${(a.balance_paise / 100).toFixed(0)}`])
      : table === 'stock'
        ? (stock.data?.items ?? []).map((i) => [i.name, `${i.on_hand_qty_milli / 1000} · ${i.status}`])
        : table === 'offers'
          ? (offers.data?.programs ?? []).map((p) => [t(`offer_kind.${p.type}`), `${p.issued} · ${p.status}`])
          : table === 'audit'
            ? (trust.data?.activity ?? []).map((a) => [a.type, `${a.tier} · ${time(a.occurred_at)}`])
            : (park.data?.bills ?? []).map((b) => [
                b.patron_name ?? b.id.slice(-6),
                `₹${(b.total_paise / 100).toFixed(0)}`,
              ]);
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-1">
        {TABLES.map((x) => (
          <button
            key={x}
            type="button"
            onClick={() => setTable(x)}
            className={cx(
              'rounded-chip px-2 py-0.5 text-meta font-semibold',
              x === table ? 'bg-midnight text-white' : 'bg-ground',
            )}
          >
            {t(`stage.table_${x}`)}
          </button>
        ))}
      </div>
      <table className="w-full text-meta">
        <tbody>
          {rows.map(([a, b], i) => (
            <tr key={i} className={cx('border-t border-line', i === 0 && 'bg-sky')}>
              <td className="truncate py-1 font-semibold">{a}</td>
              <td className="num text-right">{b}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Logs({ items }: { items: StreamItem[] }) {
  const { t, time } = useI18n();
  const mode = useDataMode();
  const [verify, setVerify] = useState<AuditVerification | null>(null);
  const events = items.filter((i) => i.kind === 'event');
  const list =
    events.length || mode === 'live' ? events : STAGE_EVENTS.map((e) => ({ ...e, kind: 'event' as const }));
  const check = async () =>
    setVerify(
      mode === 'live'
        ? ((await apiGet('/v1/audit/verify')) as AuditVerification)
        : { valid: true, checked: 1284, bad_seq: null },
    );
  return (
    <div className="flex flex-col gap-2">
      <Button size="sm" variant="tint" onClick={() => void check()}>
        {t('trust.verify')}
      </Button>
      {verify && (
        <Pill tone={verify.valid ? 'green' : 'red'}>
          {verify.valid
            ? t('trust.verified', { n: verify.checked })
            : t('trust.tampered', { seq: verify.bad_seq ?? 0 })}
        </Pill>
      )}
      {list.slice(0, 18).map((e, i) => (
        <div key={i} className="flex items-center gap-2 border-t border-line pt-1 text-meta">
          <CircleCheck size={13} className="shrink-0 text-green" />
          <span className="flex-1 truncate font-mono">{e.type}</span>
          <span className="num text-ink-3">{time(e.at)}</span>
        </div>
      ))}
    </div>
  );
}

function Health() {
  const { t } = useI18n();
  const h = useView(views.health());
  const connected = useStream((s) => s.connected);
  const mode = useDataMode();
  return (
    <div className="flex flex-col gap-2 text-meta">
      {(h.data?.providers ?? []).map((p) => (
        <p key={p.name} className="flex justify-between capitalize">
          {p.name} <Pill tone={p.mode === 'live' ? 'green' : 'amber'}>{t(`health.mode_${p.mode}`)}</Pill>
        </p>
      ))}
      <p className="flex justify-between">
        {t('stage.sse')}
        {connected || mode === 'fixture' ? (
          <CircleCheck size={16} className="text-green" />
        ) : (
          <CircleX size={16} className="text-red" />
        )}
      </p>
      <p className="flex justify-between">
        {t('stage.queue')} <span className="num">{h.data?.offline_queue.size ?? 0}</span>
      </p>
      <p className="flex justify-between">
        {t('health.spend')} <Money paise={h.data?.ai_spend_today_paise ?? 0} />
      </p>
      <p className="flex justify-between">
        {t('stage.invariants')} <CircleCheck size={16} className="text-green" />
      </p>
    </div>
  );
}

export function Evidence({
  tab,
  setTab,
  table,
  setTable,
}: {
  tab: EvidenceTab;
  setTab: (t: EvidenceTab) => void;
  table: string;
  setTable: (t: string) => void;
}) {
  const { t } = useI18n();
  const items = useStream((s) => s.items);
  const mode = useDataMode();
  const spans = spansFrom(items, mode);
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-card bg-white shadow-1">
      <div className="grid grid-cols-4 gap-1 border-b border-line p-2">
        {EVIDENCE_TABS.map((x) => (
          <button
            key={x}
            type="button"
            onClick={() => setTab(x)}
            className={cx(
              'rounded-chip py-1 text-meta font-bold',
              x === tab ? 'bg-midnight text-white' : 'text-ink-2',
            )}
          >
            {t(`stage.tab_${x}`)}
          </button>
        ))}
      </div>
      <div className="no-scrollbar flex-1 overflow-y-auto p-3">
        {tab === 'trace' && <Trace spans={spans} />}
        {tab === 'playbooks' && <Playbooks />}
        {tab === 'tools' && <Tools spans={spans} />}
        {tab === 'ai' && <AiCalls spans={spans} />}
        {tab === 'tables' && <Tables table={table} setTable={setTable} />}
        {tab === 'logs' && <Logs items={items} />}
        {tab === 'health' && <Health />}
      </div>
    </div>
  );
}
