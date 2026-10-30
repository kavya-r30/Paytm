'use client';

// The Orb (I3 rule 7): idle, listening (cyan ring, breathing), thinking (travelling arc), speaking (mouth
// bars), needs_you (amber dashed ring), done (green ring, happy eyes), alert (red). Sizes 16–160.
import type { ReactNode } from 'react';
import type { Presence } from '@/lib/store/turn';
import { useI18n } from '@/lib/i18n/react';
import { cx } from '../ui/kit';

const BODY =
  'radial-gradient(circle at 34% 28%, color-mix(in srgb, white 70%, var(--color-paytm-blue)) 0%, var(--color-paytm-blue) 45%, var(--color-cyan-text) 100%)';

export function Orb({
  state = 'idle',
  size = 50,
  className,
}: {
  state?: Presence;
  size?: number;
  className?: string;
}) {
  const ring: Partial<Record<Presence, string>> = {
    listening: 'outline outline-[3px] outline-offset-4 outline-paytm-blue orb-breathe',
    needs_you: 'outline-dashed outline-[3px] outline-offset-4 outline-amber',
    done: 'outline outline-[3px] outline-offset-4 outline-green-fill',
    alert: 'outline outline-[3px] outline-offset-4 outline-red',
  };
  const eyeH = size * 0.17;
  const eyeW = Math.max(2, size * 0.075);
  const happy = state === 'done';
  return (
    <span
      className={cx(
        'relative inline-flex shrink-0 rounded-chip',
        state === 'idle' && 'orb-float',
        ring[state],
        className,
      )}
      style={{ width: size, height: size, background: BODY, boxShadow: 'var(--shadow-2)' }}
      role="img"
      aria-label={`arth ${state}`}
    >
      {state === 'thinking' && (
        <span
          className="orb-spin absolute -inset-1.5 rounded-chip border-[3px] border-transparent"
          style={{ borderTopColor: 'var(--color-paytm-blue)', borderRightColor: 'var(--color-paytm-blue)' }}
        />
      )}
      <span
        className="absolute inset-0 flex flex-col items-center justify-center"
        style={{ gap: size * 0.07 }}
      >
        <span className="flex" style={{ gap: size * 0.13 }}>
          {[0, 1].map((i) =>
            happy ? (
              <span
                key={i}
                style={{
                  width: eyeH,
                  height: eyeH / 2,
                  borderTopWidth: eyeW,
                  borderRadius: '999px 999px 0 0',
                }}
                className="border-white"
              />
            ) : (
              <span key={i} className="orb-eye rounded-chip bg-white" style={{ width: eyeW, height: eyeH }} />
            ),
          )}
        </span>
        {size >= 36 && (
          <span className="flex items-end" style={{ gap: Math.max(1, size * 0.025), height: size * 0.09 }}>
            {[0.5, 0.8, 1, 0.8, 0.5].map((h, i) => (
              <span
                key={i}
                className={cx('rounded-chip bg-white/90', state === 'speaking' && 'wave-bar')}
                style={{
                  width: Math.max(1, size * 0.025),
                  height: `${state === 'speaking' ? 100 : h * 55}%`,
                  animationDelay: `${i * 0.12}s`,
                }}
              />
            ))}
          </span>
        )}
      </span>
    </span>
  );
}

export function MiniOrb({ state = 'idle' }: { state?: Presence }) {
  return <Orb state={state} size={28} />;
}

/** Arth's words always sit in a sky band with the mini orb (I3 rule 2). */
export function ArthNote({
  children,
  className,
  label = true,
}: {
  children: ReactNode;
  className?: string;
  label?: boolean;
}) {
  const { t } = useI18n();
  return (
    <div className={cx('flex items-start gap-3 rounded-ground bg-sky p-4', className)}>
      <MiniOrb />
      <div className="min-w-0 text-body leading-snug text-ink">
        {label && <span className="font-bold text-midnight">{t('arth.note_label')} </span>}
        {children}
      </div>
    </div>
  );
}

/** "Kahaan se: 214 bills · UPI ledger · 3 cash entries" (I3 rule 6). */
export function ProvenanceChips({ items }: { items: { kind: string; count?: number }[] }) {
  const { t } = useI18n();
  if (!items.length) return null;
  return (
    <div className="flex flex-wrap items-center gap-2 text-meta text-ink-3">
      <span className="font-semibold">{t('arth.provenance')}</span>
      {items.map((p, i) => (
        <span key={i} className="rounded-chip border border-line bg-white px-2.5 py-0.5">
          {p.count !== undefined ? `${p.count} ` : ''}
          {t(`provenance.${p.kind}`)}
        </span>
      ))}
    </div>
  );
}

/** Waveform bars for the live-voice strip and the brief card. */
export function Waveform({
  bars = 18,
  active = true,
  tone = 'light',
}: {
  bars?: number;
  active?: boolean;
  tone?: 'light' | 'dark';
}) {
  return (
    <span className="flex h-8 items-center gap-[3px]" aria-hidden>
      {Array.from({ length: bars }, (_, i) => (
        <span
          key={i}
          className={cx(
            'w-[3px] rounded-chip',
            active && 'wave-bar',
            tone === 'light' ? 'bg-paytm-blue' : 'bg-white/80',
          )}
          style={{ height: `${30 + ((i * 37) % 70)}%`, animationDelay: `${(i % 6) * 0.11}s` }}
        />
      ))}
    </span>
  );
}
