'use client';

import type { ReactNode } from 'react';
import { DeviceFrame } from '@/components/shell/frame';
import { NavRail, Toasts } from '@/components/shell/device';

export default function DeviceLayout({ children }: { children: ReactNode }) {
  return (
    <DeviceFrame>
      <div className="relative flex h-full w-full">
        <NavRail />
        {children}
        <Toasts />
      </div>
    </DeviceFrame>
  );
}
