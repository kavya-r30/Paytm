'use client';

// Inputs and surfaces from the Foundations board (I4): buttons, chips, tier chips, toggles, cards, text fit.
import { useLayoutEffect, useRef, useState, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { fitSize, initials } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';

export function cx(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(' ');
}

type Variant = 'primary' | 'dark' | 'amber' | 'ghost' | 'tint' | 'danger' | 'text';
const VARIANT: Record<Variant, string> = {
  primary: 'bg-paytm-blue text-midnight hover:brightness-95',
  dark: 'bg-midnight text-white hover:brightness-110',
  amber: 'bg-amber text-midnight hover:brightness-95',
  ghost: 'bg-white text-ink border-2 border-line hover:border-ink-3',
  tint: 'bg-sky text-midnight hover:brightness-97',
  danger: 'bg-red text-white hover:brightness-110',
  text: 'bg-transparent text-cyan-text hover:underline px-1',
};

/** Buttons never wrap past two lines (I6: the "Mol-bhaav karo" 3-line wrap is a defect). */
export function Button({
  variant = 'primary',
  size = 'md',
  icon,
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
}) {
  const sizes = { sm: 'h-9 px-3 text-meta', md: 'h-12 px-5 text-body', lg: 'h-16 px-6 text-arth' };
  return (
    <button
      type="button"
      className={cx(
        'inline-flex items-center justify-center gap-2 rounded-button font-bold transition disabled:opacity-40',
        VARIANT[variant],
        variant !== 'text' && sizes[size],
        className,
      )}
      {...rest}
    >
      {icon}
      <span className="line-clamp-2 text-center leading-tight">{children}</span>
    </button>
  );
}

export function Chip({
  active,
  tone = 'plain',
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { active?: boolean; tone?: 'plain' | 'amber' | 'red' | 'sky' }) {
  const tones = {
    plain: active ? 'bg-midnight text-white border-midnight' : 'bg-white text-ink border-line',
    amber: 'bg-amber-tint text-amber-text border-amber-tint',
    red: active ? 'bg-red-tint text-red border-red' : 'bg-white text-red border-line',
    sky: active ? 'bg-sky text-midnight border-paytm-blue' : 'bg-white text-midnight border-line',
  };
  return (
    <button
      type="button"
      className={cx(
        'inline-flex h-10 shrink-0 items-center gap-1.5 rounded-chip border-2 px-4 text-body font-semibold whitespace-nowrap',
        tones[tone],
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}

/** Tier chip (I3 rule 4): R0 grey "khud", R1 grey "undo 30s", R2 amber, R3 red, R4 midnight. */
export function TierChip({
  tier,
  className,
  compact,
}: {
  tier: string;
  className?: string;
  compact?: boolean;
}) {
  const { t } = useI18n();
  const tone: Record<string, string> = {
    R0: 'bg-line text-ink-2',
    R1: 'bg-line text-ink-2',
    R2: 'bg-amber-tint text-amber-text',
    R3: 'bg-red-tint text-red',
    R4: 'bg-midnight text-white',
  };
  return (
    <span
      className={cx(
        'inline-flex items-center gap-1 rounded-chip px-2.5 py-0.5 text-meta font-bold whitespace-nowrap',
        tone[tier] ?? tone.R0,
        className,
      )}
    >
      {compact ? tier : `${tier} · ${t(`tier.${tier.toLowerCase()}`)}`}
    </span>
  );
}

export function Pill({
  tone = 'grey',
  children,
}: {
  tone?: 'grey' | 'green' | 'amber' | 'red' | 'sky';
  children: ReactNode;
}) {
  const tones = {
    grey: 'bg-line text-ink-2',
    green: 'bg-green-tint text-green',
    amber: 'bg-amber-tint text-amber-text',
    red: 'bg-red-tint text-red',
    sky: 'bg-sky text-midnight',
  };
  return (
    <span
      className={cx(
        'inline-flex items-center gap-1 rounded-chip px-2.5 py-0.5 text-meta font-bold whitespace-nowrap',
        tones[tone],
      )}
    >
      {children}
    </span>
  );
}

export function Card({
  className,
  children,
  attention,
  onClick,
}: {
  className?: string;
  children: ReactNode;
  attention?: boolean;
  onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={cx(
        'rounded-card bg-white shadow-1',
        attention && 'border-2 border-amber',
        onClick && 'cursor-pointer transition hover:shadow-2',
        className,
      )}
    >
      {children}
    </div>
  );
}

export function Toggle({
  on,
  onChange,
  label,
}: {
  on: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      aria-label={label}
      onClick={() => onChange(!on)}
      className={cx('relative h-7 w-12 shrink-0 rounded-chip transition', on ? 'bg-green-fill' : 'bg-line')}
    >
      <span
        className={cx(
          'absolute top-1 h-5 w-5 rounded-chip bg-white shadow-1 transition-all',
          on ? 'left-6' : 'left-1',
        )}
      />
    </button>
  );
}

export function Avatar({
  name,
  size = 44,
  tone = 'midnight',
}: {
  name: string;
  size?: number;
  tone?: 'midnight' | 'sky';
}) {
  return (
    <span
      style={{ width: size, height: size, fontSize: size * 0.36 }}
      className={cx(
        'inline-flex shrink-0 items-center justify-center rounded-chip font-bold',
        tone === 'midnight' ? 'bg-midnight text-white' : 'bg-sky text-midnight',
      )}
    >
      {initials(name)}
    </span>
  );
}

/** A text slot with a line budget: overflow ends in an ellipsis and the full text is the tooltip (I6). */
export function Fit({
  lines = 1,
  className,
  children,
}: {
  lines?: 1 | 2 | 3;
  className?: string;
  children: string;
}) {
  const clamp = { 1: 'line-clamp-1', 2: 'line-clamp-2', 3: 'line-clamp-3' }[lines];
  return (
    <span title={children} className={cx(clamp, 'break-words', className)}>
      {children}
    </span>
  );
}

/** Headlines and amounts shrink between max and min to fit their box (I6 auto-fit). */
export function AutoFit({
  max,
  min,
  className,
  children,
}: {
  max: number;
  min: number;
  className?: string;
  children: string;
}) {
  const box = useRef<HTMLSpanElement>(null);
  const [size, setSize] = useState(max);
  useLayoutEffect(() => {
    const el = box.current;
    if (!el || !el.parentElement) return;
    el.style.fontSize = `${max}px`;
    setSize(fitSize(el.scrollWidth, el.parentElement.clientWidth, max, min));
  }, [children, max, min]);
  return (
    <span
      ref={box}
      style={{ fontSize: size }}
      title={children}
      className={cx('num block truncate', className)}
    >
      {children}
    </span>
  );
}

export function Money({
  paise,
  compact,
  className,
}: {
  paise: number;
  compact?: boolean;
  className?: string;
}) {
  const { money } = useI18n();
  return <span className={cx('num', className)}>{money(paise, compact)}</span>;
}

export function SectionTitle({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h3 className="text-body font-semibold text-ink-2">{children}</h3>
      {action}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx('pulse rounded-ground bg-line', className)} />;
}

export function Divider() {
  return <div className="h-px w-full bg-line" />;
}
