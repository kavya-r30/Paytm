'use client';

// MemoryCard (I4, MEM-1): a learned fact with its evidence and "Sahi hai / Galat / Bhool jao".
import { Brain } from 'lucide-react';
import { useState } from 'react';
import { useCommand } from '@/lib/api/commands';
import { useI18n } from '@/lib/i18n/react';
import { Button, Card, Pill } from '../ui/kit';

export function MemoryCard({
  fact,
  evidence,
  factId,
}: {
  fact: string;
  evidence: string[];
  factId?: string;
}) {
  const { t } = useI18n();
  const run = useCommand();
  const [state, setState] = useState<'open' | 'confirmed' | 'retracted' | 'forgotten'>('open');
  const act = (verb: 'confirm' | 'retract' | 'forget', next: typeof state) => {
    setState(next);
    if (factId) void run(`memory.${verb}`, { fact_id: factId });
  };
  return (
    <Card className="flex flex-col gap-3 p-5">
      <div className="flex items-start gap-3">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-ground bg-sky text-midnight">
          <Brain size={18} />
        </span>
        <p className="text-body font-semibold leading-snug">{fact}</p>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {evidence.map((e) => (
          <Pill key={e}>{e}</Pill>
        ))}
      </div>
      {state === 'open' ? (
        <div className="flex gap-2">
          <Button variant="tint" size="sm" onClick={() => act('confirm', 'confirmed')}>
            {t('memory.right')}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => act('retract', 'retracted')}>
            {t('memory.wrong')}
          </Button>
          <Button variant="text" onClick={() => act('forget', 'forgotten')}>
            {t('memory.forget')}
          </Button>
        </div>
      ) : (
        <Pill tone={state === 'confirmed' ? 'green' : 'grey'}>{t(`memory.state_${state}`)}</Pill>
      )}
    </Card>
  );
}
