'use client';

import { use } from 'react';
import { resolveScreen } from '@/screens/device/registry';

// One route for every device screen: /device/<screen>/<param?>. Envelope `nav.screen` maps here directly.
export default function DevicePage({ params }: { params: Promise<{ screen?: string[] }> }) {
  const { screen = [] } = use(params);
  const { Component, param } = resolveScreen(screen);
  return <Component param={param} />;
}
