'use client';

// Fixed-canvas scalers (I1): the device is 960×720 logical (4:3) and the stage 1920×1080, scaled uniformly
// to fit the viewport with letterboxing, never reflowed.
import { useEffect, useRef, useState, type ReactNode } from 'react';
import { cx } from '../ui/kit';

/**
 * The UI shows at 80% of the window on desktop: a top-level fixed canvas fills 80% of its fit; inside the
 * stage's iframes it keeps filling its slot (I2 geometry). Flow-layout surfaces get the same 80% from the
 * `zoom` rule in globals.css.
 */
export const UI_ZOOM = 0.8;

export function useFitScale(width: number, height: number) {
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const zoom = window.self === window.top ? UI_ZOOM : 1;
    const update = () => setScale(zoom * Math.min(el.clientWidth / width, el.clientHeight / height));
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [width, height]);
  return { ref, scale };
}

export function FixedCanvas({
  width,
  height,
  children,
  className,
  letterbox = 'bg-ink',
}: {
  width: number;
  height: number;
  children: ReactNode;
  className?: string;
  letterbox?: string;
}) {
  const { ref, scale } = useFitScale(width, height);
  return (
    <div
      ref={ref}
      className={cx('fixed inset-0 flex items-center justify-center overflow-hidden', letterbox)}
    >
      <div style={{ width: width * scale, height: height * scale }} className="relative shrink-0">
        <div
          style={{ width, height, transform: `scale(${scale})`, transformOrigin: 'top left' }}
          className={cx('absolute left-0 top-0 overflow-hidden', className)}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

export function DeviceFrame({ children }: { children: ReactNode }) {
  return (
    <FixedCanvas width={960} height={720} className="bg-ground" letterbox="bg-midnight">
      {children}
    </FixedCanvas>
  );
}
