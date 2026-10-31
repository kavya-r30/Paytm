'use client';

// Simulated UPI app page (I1 /pay/:token, T2.2): payee and amount only, nothing personal. Backed by
// GET/POST /sim/pay/{token}; falls back to a demo order when the token is unknown or the API is down.
import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, Clock3, ShieldCheck, XCircle } from 'lucide-react';
import { use, useState } from 'react';
import { Button, Card, Money } from '@/components/ui/kit';
import { payNow, payPage, type PayPage } from '@/lib/api/sim';
import { useI18n } from '@/lib/i18n/react';

const DEMO: PayPage = {
  token: 'demo-token',
  payee_name: 'Gupta General Store',
  payee_vpa: 'guptastore@paytm',
  amount_paise: 124000,
  status: 'waiting',
  expires_at: '2026-10-29T09:40:00Z',
};

export default function PayPageRoute({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const { t } = useI18n();
  const q = useQuery({ queryKey: ['pay', token], queryFn: () => payPage(token), retry: false });
  const page = q.data ?? (q.isError ? { ...DEMO, token } : null);
  const [result, setResult] = useState<'success' | 'pending' | 'failed' | null>(null);
  const [busy, setBusy] = useState(false);

  const pay = async (outcome: 'success' | 'pending' | 'failed') => {
    setBusy(true);
    try {
      if (q.data) await payNow(token, outcome);
      setResult(outcome);
    } catch {
      setResult('failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-[420px] flex-col gap-4 bg-ground p-5">
      <p className="flex items-center gap-2 text-meta text-ink-3">
        <ShieldCheck size={16} /> {t('upi.simulated')}
      </p>
      {!page ? (
        <Card className="p-8 text-center text-body text-ink-3">{t('upi.loading')}</Card>
      ) : (
        <>
          <Card className="flex flex-col items-center gap-2 p-6 text-center">
            <p className="text-body text-ink-3">{t('upi.paying')}</p>
            <p className="text-arth font-bold">{page.payee_name}</p>
            {page.payee_vpa && <p className="text-meta text-ink-3">{page.payee_vpa}</p>}
            <Money paise={page.amount_paise} className="mt-2 text-amount font-extrabold" />
          </Card>
          {result === null ? (
            <div className="flex flex-col gap-2">
              <Button size="lg" disabled={busy} onClick={() => void pay('success')}>
                {t('upi.pay')}
              </Button>
              <Button variant="ghost" disabled={busy} onClick={() => void pay('pending')}>
                {t('upi.sim_pending')}
              </Button>
              <Button variant="ghost" className="text-red" disabled={busy} onClick={() => void pay('failed')}>
                {t('upi.sim_failed')}
              </Button>
            </div>
          ) : (
            <Card className="flex flex-col items-center gap-2 p-6 text-center">
              {result === 'success' && <CheckCircle2 size={56} className="text-green-fill" />}
              {result === 'pending' && <Clock3 size={56} className="text-amber" />}
              {result === 'failed' && <XCircle size={56} className="text-red" />}
              <p className="text-arth font-bold">{t(`upi.result_${result}`)}</p>
            </Card>
          )}
          {q.isError && <p className="text-center text-meta text-ink-3">{t('upi.demo_note')}</p>}
        </>
      )}
    </main>
  );
}
