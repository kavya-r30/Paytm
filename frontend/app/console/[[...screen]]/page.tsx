'use client';

import { use } from 'react';
import { ConsoleApp } from '@/screens/console/app';

// The owner's Console (I7 CON): /console/<screen>. R4 actions live only here, behind OTP.
export default function ConsolePage({ params }: { params: Promise<{ screen?: string[] }> }) {
  const { screen = [] } = use(params);
  return <ConsoleApp screen={screen[0] ?? 'home'} param={screen[1]} />;
}
