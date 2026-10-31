'use client';

// Phones (I7 PH): persona threads (owner, customers, suppliers, helper), 390×844, WhatsApp-shaped with neutral
// styling. Every Arth-sent message carries "Sent by Arth" (+ "after {owner} approved" when gated, SRF-5).
import { useQuery } from '@tanstack/react-query';
import { BarChart3, ChevronLeft, CreditCard, Mic, Play, Send } from 'lucide-react';
import Link from 'next/link';
import { use, useState } from 'react';
import { FixedCanvas } from '@/components/shell/frame';
import { Avatar, cx } from '@/components/ui/kit';
import { useDataMode } from '@/lib/api/hooks';
import { inbound, merchantId, threads, type Thread, type ThreadMessage } from '@/lib/api/sim';
import { THREADS } from '@/lib/fixtures/surfaces';
import { useI18n } from '@/lib/i18n/react';
import { useStream } from '@/lib/store/turn';

const ROLE_ORDER = ['owner', 'customer', 'supplier', 'helper'];

function pick(all: Thread[], persona: string): Thread | undefined {
  return all.find((t) => t.persona_id === persona) ?? all.find((t) => t.role === persona) ?? all[0];
}

function Bubble({ m, owner }: { m: ThreadMessage; owner: string }) {
  const { t, time, money } = useI18n();
  const out = m.direction === 'out';
  const text =
    m.body.text ?? (m.body.template_key ? t(String(m.body.template_key), m.body.params as never) : '');
  return (
    <div className={cx('flex', out ? 'justify-end' : 'justify-start')}>
      <div
        className={cx('max-w-[78%] rounded-ground px-3 py-2 shadow-1', out ? 'bg-green-tint' : 'bg-white')}
      >
        {out && <p className="text-meta font-bold text-green">{t('phone.sent_by_arth')}</p>}
        {m.kind === 'image' && (
          <div className="mb-1 flex h-28 items-center justify-center rounded-ground bg-sky text-midnight">
            <BarChart3 size={40} />
          </div>
        )}
        {m.kind === 'voice_note' && (
          <div className="flex items-center gap-2 text-ink-2">
            <Play size={18} />
            <span className="h-1 w-32 rounded-chip bg-ink-3/40" />
            <Mic size={14} />
          </div>
        )}
        {m.kind !== 'voice_note' && (
          <p className="whitespace-pre-line text-body leading-snug text-ink">{text}</p>
        )}
        {m.kind === 'pay_link' && (
          <a
            href={String(m.body.url ?? '#')}
            target="_blank"
            rel="noreferrer"
            className="mt-2 flex items-center gap-2 rounded-ground border border-line bg-white p-2 text-body font-bold text-cyan-text"
          >
            <CreditCard size={18} />
            {t('phone.pay_link', { amount: money(Number(m.body.amount_paise ?? 0)) })}
          </a>
        )}
        {m.kind === 'buttons' && Array.isArray(m.body.buttons) && (
          <div className="mt-2 flex flex-col gap-1">
            {(m.body.buttons as string[]).map((b) => (
              <span
                key={b}
                className="rounded-ground border border-line bg-white py-1.5 text-center text-body font-semibold text-cyan-text"
              >
                {b}
              </span>
            ))}
          </div>
        )}
        <p className="mt-0.5 text-right text-meta text-ink-3">
          {typeof m.body.approved_by === 'string' ? `${t('phone.after_approval', { owner })} · ` : ''}
          {time(m.created_at)}
        </p>
      </div>
    </div>
  );
}

export default function Phone({ params }: { params: Promise<{ persona: string }> }) {
  const { persona } = use(params);
  const { t } = useI18n();
  const mode = useDataMode();
  const merchant = mode === 'live' ? merchantId() : null;
  const tick = useStream((s) => s.items.length);
  const [draft, setDraft] = useState('');
  const [local, setLocal] = useState<ThreadMessage[]>([]);
  const q = useQuery({
    queryKey: ['threads', merchant, tick],
    enabled: !!merchant,
    refetchInterval: 4000,
    queryFn: () => threads(merchant!),
  });
  const all = merchant ? (q.data ?? []) : THREADS;
  const thread = pick(all, persona);
  const owner = all.find((x) => x.role === 'owner')?.name ?? 'owner';
  const messages = [...(thread?.messages ?? []), ...local];

  const send = async () => {
    const text = draft.trim();
    if (!text || !thread) return;
    setDraft('');
    if (merchant) {
      await inbound(merchant, thread.persona_id, text);
      void q.refetch();
    } else {
      setLocal((l) => [
        ...l,
        {
          id: `local-${l.length}`,
          direction: 'in',
          category: 'inbound',
          kind: 'text',
          created_at: new Date().toISOString(),
          body: { text },
        },
      ]);
    }
  };

  return (
    <FixedCanvas width={390} height={844} className="bg-ground" letterbox="bg-ink">
      <div className="flex h-full flex-col">
        <header className="flex items-center gap-3 bg-midnight px-3 pb-3 pt-10 text-white">
          <ChevronLeft size={22} />
          <Avatar name={thread?.name ?? '?'} size={36} tone="sky" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-body font-bold">{thread?.name ?? t('phone.no_thread')}</p>
            <p className="text-meta text-white/70">{t(`phone.role_${thread?.role ?? 'customer'}`)}</p>
          </div>
        </header>
        <nav className="no-scrollbar flex gap-1.5 overflow-x-auto bg-white px-2 py-2">
          {[...all]
            .sort((a, b) => ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role))
            .map((th) => (
              <Link
                key={th.id}
                href={`/phone/${th.persona_id}`}
                className={cx(
                  'shrink-0 rounded-chip px-3 py-1 text-meta font-semibold',
                  th.id === thread?.id ? 'bg-midnight text-white' : 'bg-ground text-ink-2',
                )}
              >
                {th.name.split(' ')[0]}
              </Link>
            ))}
        </nav>
        <div className="no-scrollbar flex flex-1 flex-col gap-2 overflow-y-auto p-3">
          {messages.map((m) => (
            <Bubble key={m.id} m={m} owner={owner} />
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void send();
          }}
          className="flex items-center gap-2 bg-white p-2 pb-6"
        >
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={t('phone.type')}
            className="h-11 flex-1 rounded-chip bg-ground px-4 text-body outline-none"
          />
          <button
            type="submit"
            aria-label={t('phone.send')}
            className="flex h-11 w-11 items-center justify-center rounded-chip bg-green-fill text-white"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </FixedCanvas>
  );
}
