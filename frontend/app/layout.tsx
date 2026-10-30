import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import './globals.css';

export const metadata: Metadata = { title: 'Arth', description: 'AI business partner for Paytm merchants' };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="hi">
      <body>{children}</body>
    </html>
  );
}
