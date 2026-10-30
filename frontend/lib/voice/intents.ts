// Voice parity (A11Y-1, T7.17): every device screen and action is reachable by an utterance. Until L4 turns
// exist, the ask dock resolves text against this table locally; with L4 the server's envelope.nav wins.

export type Intent = {
  id: string;
  /** Device screen path ("khata", "bill/new") or null for an in-screen action. */
  screen: string | null;
  /** In-screen action names the screen handles via the `arth:action` window event. */
  action?: string;
  /** Lowercase keywords: a match needs every word of one phrase to occur in the text. */
  phrases: string[];
};

export const INTENTS: Intent[] = [
  { id: 'home', screen: 'home', phrases: ['subah ka haal', 'aaj kaisa', 'aaj ka haal', 'home', 'aaj'] },
  {
    id: 'approve_all',
    screen: null,
    action: 'approve_all',
    phrases: ['teeno haan', 'sab haan', 'saare haan'],
  },
  { id: 'ask', screen: 'ask', phrases: ['aage kyun', 'kyun', 'kitna aaya', 'poochho', 'weekly report'] },
  { id: 'forecast', screen: 'forecast', phrases: ['kal kitni', 'andaaza', 'diwali pe kya', 'forecast'] },
  { id: 'notifications', screen: 'notifications', phrases: ['kya pending', 'pending hai', 'kaam aur undo'] },
  { id: 'undo', screen: null, action: 'undo', phrases: ['wapas lo', 'undo'] },
  { id: 'bill', screen: 'bill/new', phrases: ['naya bill', 'ka bill', 'bill banao', 'bill'] },
  { id: 'qr', screen: null, action: 'show_qr', phrases: ['qr dikhao', 'qr'] },
  { id: 'cash', screen: null, action: 'pay_cash', phrases: ['cash mein lo', 'cash'] },
  { id: 'khata_pay', screen: null, action: 'pay_khata', phrases: ['khate mein daal', 'khate mein'] },
  { id: 'park', screen: 'park', phrases: ['ruke hue', 'bill rok', 'park'] },
  { id: 'return', screen: 'return', phrases: ['wapsi', 'return'] },
  { id: 'verdict', screen: 'verdict', phrases: ['payment check', 'screenshot'] },
  { id: 'learn', screen: 'learn', phrases: ['naya item', 'scan karke'] },
  { id: 'orders', screen: 'orders', phrases: ['orders', 'order dikhao'] },
  { id: 'khata', screen: 'khata', phrases: ['ka hisaab', 'khata', 'udhaar'] },
  { id: 'promises', screen: 'promises', phrases: ['vaade', 'promise'] },
  { id: 'patron', screen: 'patron', phrases: ['grahak ki detail', 'customer detail'] },
  { id: 'stock', screen: 'stock', phrases: ['khatam hone wala', 'stock', 'maal kitna'] },
  { id: 'expiry', screen: 'expiry', phrases: ['expiry', 'kharab hone'] },
  { id: 'suppliers', screen: 'suppliers', phrases: ['supplier', 'distributor'] },
  { id: 'grn', screen: 'grn', phrases: ['maal aaya', 'delivery aayi'] },
  { id: 'claim', screen: 'claim', phrases: ['kam aaya', 'claim', 'rate zyada'] },
  { id: 'po', screen: 'po', phrases: ['purchase order', 'order khud banao'] },
  { id: 'item', screen: 'item', phrases: ['item ki detail', 'daam badlo'] },
  { id: 'gate', screen: 'gate', phrases: ['rates dekho', 'ek faisla', 'quote'] },
  { id: 'grow', screen: 'grow', phrases: ['bikri kaise badh', 'badhao', 'goal'] },
  { id: 'plan', screen: 'plan', phrases: ['arth ka plan', 'growth plan', 'plan chalao'] },
  { id: 'demand', screen: 'demand', phrases: ['kya maang', 'log maang', 'demand'] },
  { id: 'bundle', screen: 'bundle', phrases: ['bundle', 'pre-order', 'preorder'] },
  { id: 'offers', screen: 'offers', phrases: ['offer', 'coupon', 'cashback'] },
  { id: 'campaign', screen: 'campaign', phrases: ['campaign', 'message bheje'] },
  { id: 'ledger', screen: 'ledger', phrases: ['growth ledger', 'kitna fayda', 'impact'] },
  { id: 'storefront', screen: 'storefront', phrases: ['dukaan ka link', 'storefront', 'online dukaan'] },
  { id: 'menu', screen: 'menu', phrases: ['aur kya', 'more', 'menu'] },
  { id: 'team', screen: 'team', phrases: ['raat ko', 'arth ki team', 'kya kya kiya'] },
  { id: 'pause_all', screen: null, action: 'pause_all', phrases: ['sab kaam roko', 'pause all'] },
  { id: 'run', screen: 'run', phrases: ['kaam ki detail', 'run detail'] },
  { id: 'memory', screen: 'memory', phrases: ['kya seekha', 'yaad hai', 'memory'] },
  { id: 'hisaab', screen: 'hisaab', phrases: ['settlement', 'galla', 'cash count', 'hisaab kitaab'] },
  { id: 'reports', screen: 'reports', phrases: ['report', 'gst', 'p&l', 'munafa'] },
  { id: 'feedback', screen: 'feedback', phrases: ['raay', 'rating', 'feedback'] },
  { id: 'language', screen: 'language', phrases: ['bhasha', 'language'] },
  { id: 'staff', screen: 'staff', phrases: ['staff', 'permission'] },
  { id: 'trust', screen: 'trust', phrases: ['bharosa', 'activity log', 'trust'] },
  { id: 'health', screen: 'health', phrases: ['soundbox', 'system', 'battery'] },
  { id: 'capital', screen: 'capital', phrases: ['paise ki zaroorat', 'loan', 'capital'] },
  { id: 'onboarding', screen: 'onboarding', phrases: ['shuruaat', 'setup'] },
  { id: 'pin', screen: 'pin', phrases: ['kaun bill', 'login', 'pin'] },
  { id: 'shift', screen: 'shift', phrases: ['shift'] },
  { id: 'kot', screen: 'kot', phrases: ['kitchen', 'kot'] },
  { id: 'appointments', screen: 'appointments', phrases: ['appointment', 'booking'] },
  { id: 'rx', screen: 'rx', phrases: ['rx', 'refill', 'parchi'] },
];

/** Best intent for an utterance: longest matching phrase wins, so "naya bill" beats "bill". */
export function resolveIntent(text: string): Intent | null {
  const t = text.toLowerCase();
  let best: { intent: Intent; len: number } | null = null;
  for (const intent of INTENTS) {
    for (const phrase of intent.phrases) {
      if (phrase.split(' ').every((w) => t.includes(w)) && (!best || phrase.length > best.len)) {
        best = { intent, len: phrase.length };
      }
    }
  }
  return best?.intent ?? null;
}
