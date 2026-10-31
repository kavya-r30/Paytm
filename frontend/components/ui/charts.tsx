'use client';

// Data components (I4): hand-drawn SVG on token colours, so they work in every surface and in the stage.
import { cx } from './kit';

const C = {
  midnight: 'var(--color-midnight)',
  blue: 'var(--color-paytm-blue)',
  sky: 'var(--color-sky)',
  line: 'var(--color-line)',
  ink3: 'var(--color-ink-3)',
  green: 'var(--color-green-fill)',
  red: 'var(--color-red)',
  amber: 'var(--color-amber)',
};
export const SERIES = [C.blue, C.midnight, C.red, C.amber, C.green, C.ink3];

export function Donut({
  parts,
  size = 76,
  stroke = 12,
}: {
  parts: { value: number; color: string }[];
  size?: number;
  stroke?: number;
}) {
  const total = parts.reduce((s, p) => s + p.value, 0) || 1;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  let offset = 0;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={C.line} strokeWidth={stroke} />
      {parts.map((p, i) => {
        const len = (p.value / total) * circ;
        const el = (
          <circle
            key={i}
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={p.color}
            strokeWidth={stroke}
            strokeDasharray={`${Math.max(len - 2, 0)} ${circ}`}
            strokeDashoffset={-offset}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        );
        offset += len;
        return el;
      })}
    </svg>
  );
}

export function Sparkline({
  values,
  width = 80,
  height = 28,
  color = C.green,
}: {
  values: number[];
  width?: number;
  height?: number;
  color?: string;
}) {
  if (values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const pts = values.map(
    (v, i) => `${(i / (values.length - 1)) * width},${height - 3 - ((v - min) / span) * (height - 6)}`,
  );
  return (
    <svg width={width} height={height} aria-hidden>
      <polyline
        points={pts.join(' ')}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function MiniBars({
  values,
  width = 150,
  height = 56,
}: {
  values: number[];
  width?: number;
  height?: number;
}) {
  const max = Math.max(...values, 1);
  const w = width / values.length;
  return (
    <svg width={width} height={height} aria-hidden>
      {values.map((v, i) => {
        const h = Math.max(4, (v / max) * height);
        return (
          <rect
            key={i}
            x={i * w + 3}
            y={height - h}
            width={w - 6}
            height={h}
            rx={5}
            fill={i === values.length - 1 ? C.blue : C.sky}
          />
        );
      })}
    </svg>
  );
}

/** Progress ring for goals (SCR-GROW). */
export function Ring({
  value,
  size = 120,
  stroke = 12,
  color = C.blue,
}: {
  value: number;
  size?: number;
  stroke?: number;
  color?: string;
}) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const v = Math.max(0, Math.min(1, value));
  return (
    <svg width={size} height={size} aria-hidden>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={C.line} strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${v * circ} ${circ}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
    </svg>
  );
}

/** Cover bar for stock rows: filled share coloured by risk, never colour alone (an icon/text sits beside it). */
export function CoverBar({ value, risk }: { value: number; risk: 'ok' | 'low' | 'out' }) {
  const fill = { ok: 'bg-green-fill', low: 'bg-amber', out: 'bg-red' }[risk];
  return (
    <div className="h-2.5 w-full overflow-hidden rounded-chip bg-line">
      <div
        className={cx('h-full rounded-chip', fill)}
        style={{ width: `${Math.max(4, Math.min(100, value * 100))}%` }}
      />
    </div>
  );
}

/** Forecast range bar: p10–p90 band with the p50 tick (SCR-FORECAST headline). */
export function RangeBar({ low, mid, high, max }: { low: number; mid: number; high: number; max: number }) {
  const pct = (v: number) => `${(v / (max || 1)) * 100}%`;
  return (
    <div className="relative h-3 w-full rounded-chip bg-line">
      <div
        className="absolute h-full rounded-chip bg-paytm-blue/40"
        style={{ left: pct(low), width: `calc(${pct(high)} - ${pct(low)})` }}
      />
      <div className="absolute -top-1 h-5 w-1 rounded-chip bg-midnight" style={{ left: pct(mid) }} />
    </div>
  );
}

type Series = (number | null)[];

/**
 * Line + band chart: actual (solid), typical (dashed grey), forecast band (sky) and an optional pin.
 * Used by SCR-HOME (intraday) and SCR-FORECAST (6 days back, 6 ahead).
 */
export function LineBand({
  labels,
  actual,
  typical,
  low,
  high,
  pinIndex,
  width = 560,
  height = 220,
  yFormat,
}: {
  labels: string[];
  actual: Series;
  typical?: Series;
  low?: Series;
  high?: Series;
  pinIndex?: number;
  width?: number;
  height?: number;
  yFormat: (v: number) => string;
}) {
  const padL = 44;
  const padB = 26;
  const w = width - padL - 8;
  const h = height - padB - 10;
  const all = [...actual, ...(typical ?? []), ...(high ?? [])].filter((v): v is number => v !== null);
  const max = Math.max(...all, 1) * 1.08;
  const x = (i: number) => padL + (i / Math.max(labels.length - 1, 1)) * w;
  const y = (v: number) => 10 + h - (v / max) * h;
  const path = (s: Series) =>
    s
      .map((v, i) => (v === null ? null : `${x(i)},${y(v)}`))
      .filter(Boolean)
      .join(' ');
  const band =
    low && high
      ? [
          ...high.map((v, i) => (v === null ? null : `${x(i)},${y(v)}`)).filter(Boolean),
          ...low
            .map((v, i) => (v === null ? null : `${x(i)},${y(v)}`))
            .filter(Boolean)
            .reverse(),
        ].join(' ')
      : '';
  const ticks = [0, 0.5, 1].map((f) => f * max);
  const last = actual.reduce<number>((acc, v, i) => (v !== null ? i : acc), 0);
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} className="overflow-visible" aria-hidden>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={padL} x2={width - 8} y1={y(t)} y2={y(t)} stroke={C.line} />
          <text x={0} y={y(t) + 4} fontSize={12} fill={C.ink3} className="num">
            {yFormat(t)}
          </text>
        </g>
      ))}
      {labels.map((l, i) =>
        i % Math.ceil(labels.length / 6) === 0 || i === labels.length - 1 ? (
          <text key={i} x={x(i)} y={height - 6} fontSize={12} fill={C.ink3} textAnchor="middle">
            {l}
          </text>
        ) : null,
      )}
      {band && <polygon points={band} fill={C.sky} stroke="none" />}
      {high && (
        <polyline points={path(high)} fill="none" stroke={C.blue} strokeWidth={2} strokeDasharray="6 5" />
      )}
      {typical && (
        <polyline
          points={path(typical)}
          fill="none"
          stroke={C.ink3}
          strokeWidth={2}
          strokeDasharray="4 4"
          opacity={0.6}
        />
      )}
      <polyline
        points={path(actual)}
        fill="none"
        stroke={C.midnight}
        strokeWidth={3.5}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {actual[last] !== null && actual[last] !== undefined && (
        <circle
          cx={x(last)}
          cy={y(actual[last] as number)}
          r={6}
          fill={C.blue}
          stroke="white"
          strokeWidth={2.5}
        />
      )}
      {pinIndex !== undefined && actual[pinIndex] != null && (
        <circle
          cx={x(pinIndex)}
          cy={y(actual[pinIndex] as number)}
          r={6}
          fill="white"
          stroke={C.amber}
          strokeWidth={3}
        />
      )}
    </svg>
  );
}
