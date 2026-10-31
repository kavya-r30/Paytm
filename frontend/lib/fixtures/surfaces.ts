// Fixture data for the non-device surfaces (phones, console, stage), in the shapes the simulator serves.
import type { Thread } from '../api/sim';
import { NOW, fid, minutesAgo } from './ids';
import { PATRONS, SUPPLIERS } from './gupta';

function msg(
  n: number,
  direction: 'in' | 'out',
  text: string,
  ago: number,
  kind = 'text',
  extra: Record<string, unknown> = {},
) {
  return {
    id: fid('msg', n),
    direction,
    category: direction === 'out' ? 'service' : 'inbound',
    kind,
    created_at: minutesAgo(ago),
    body: { text, ...extra },
  };
}

export const THREADS: Thread[] = [
  {
    id: fid('thread', 21),
    persona_id: 'owner',
    name: 'Ramesh Gupta',
    role: 'owner',
    lang: 'hi-Latn',
    messages: [
      msg(1, 'in', 'Aaj kitna aaya?', 30),
      msg(2, 'out', 'Dopahar tak ₹4,180 · aam guruvaar se 13% aage. Chart neeche hai.', 29, 'image', {
        url: '/chart-preview',
      }),
      msg(3, 'out', 'Diwali stock: Balaji ₹18,400 (₹850 sasta). Haan bolein?', 12, 'buttons', {
        buttons: ['Haan', 'Baad mein'],
      }),
    ],
  },
  {
    id: fid('thread', 22),
    persona_id: 'priya',
    name: PATRONS.priya.name,
    role: 'customer',
    lang: 'hi',
    patron_id: PATRONS.priya.id,
    messages: [
      msg(4, 'out', 'नमस्ते प्रिया जी, आपका बिल ₹90 · गुप्ता जनरल स्टोर। धन्यवाद!', 3, 'template'),
      msg(5, 'out', 'अगली बार ₹500+ पर ₹25 कैशबैक, 12 नवंबर तक।', 3, 'template'),
    ],
  },
  {
    id: fid('thread', 23),
    persona_id: 'mehta',
    name: PATRONS.mehta.name,
    role: 'customer',
    lang: 'hi-Latn',
    patron_id: PATRONS.mehta.id,
    messages: [
      msg(6, 'in', 'Bhaiya 1 kilo kaju, 2 kilo cheeni, besan ek packet, 5 parle bhej do', 8),
      msg(7, 'out', 'Mehta ji, ₹1,240 ka order mila. Shaam 6 baje tak pahunch jayega.', 6, 'template'),
      msg(8, 'out', 'Pay link: ₹1,240', 6, 'pay_link', { url: '/pay/demo-token', amount_paise: 124000 }),
    ],
  },
  {
    id: fid('thread', 24),
    persona_id: 'balaji',
    name: SUPPLIERS.balaji.name,
    role: 'supplier',
    lang: 'hi',
    supplier_id: SUPPLIERS.balaji.id,
    messages: [
      msg(
        9,
        'out',
        'Namaste, Gupta General Store se. Kaju 5 kg, ghee 12 L, besan 20 kg ka rate bhejiye.',
        90,
        'template',
      ),
      msg(10, 'in', 'Kaju 920, ghee 610, besan 102. Kal subah delivery.', 70),
      msg(11, 'in', 'Voice note (0:12)', 68, 'voice_note'),
    ],
  },
  {
    id: fid('thread', 25),
    persona_id: 'chotu',
    name: 'Chotu',
    role: 'helper',
    lang: 'hi-Latn',
    messages: [
      msg(12, 'out', 'Pick list · Mehta ji: kaju 1 kg, cheeni 2 kg, besan 1, Parle-G 5', 5, 'template'),
    ],
  },
];

export const STAGE_EVENTS = [
  {
    type: 'bill.paid',
    at: minutesAgo(1),
    data: { bill_id: fid('bill', 41), total_paise: 9000, mode: 'upi' },
  },
  { type: 'payment.received', at: minutesAgo(1), data: { amount_paise: 9000, utr: '629104882713' } },
  { type: 'offer.issued', at: minutesAgo(1), data: { kind: 'next_txn_cashback', amount_paise: 2500 } },
  { type: 'approval.requested', at: minutesAgo(12), data: { type: 'supply.place_po', tier: 'R3' } },
  { type: 'command.executed', at: minutesAgo(29), data: { type: 'ledger.send_statement', tier: 'R1' } },
];

export const STAGE_SPANS = [
  { name: 'normalise', ms: 18, cost: 0, mode: 'live' },
  { name: 'route', ms: 140, cost: 6, mode: 'live' },
  { name: 'tool:sales_today', ms: 32, cost: 0, mode: 'live' },
  { name: 'tool:compare_weekday', ms: 41, cost: 0, mode: 'live' },
  { name: 'gate', ms: 4, cost: 0, mode: 'live' },
  { name: 'compose', ms: 610, cost: 22, mode: 'replay' },
  { name: 'guard', ms: 95, cost: 3, mode: 'live' },
];

export const FIXTURE_CLOCK = NOW;
