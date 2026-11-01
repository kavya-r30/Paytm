// Arth pitch deck (Paytm Hackathon 2026, Merchant Growth AI): structured pptxgenjs deck.
const path = require('path');
const pptxgen = require('pptxgenjs');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const { applyTheme } = require(
  'C:/Users/kavya/.claude/skills/synced/1482bb3c-261b-45e0-940a-01a2d2156049_93e98501-81dc-442a-adf8-565368874a5e/pptx/scripts/apply_theme.js',
);

const OUT = process.argv[2] || path.join(__dirname, 'Arth_Pitch_Deck.pptx');

// Arth design tokens (spec I3): Paytm midnight + Paytm blue, amber for "needs your haan"
const HEX = {
  ink: '0B1B33', white: 'FFFFFF', midnight: '002E6E', ground: 'F5F7FA',
  blue: '00BAF2', amber: 'F5A524', green: '067647', cyan: '0077B6', sky: 'E8F8FE', red: 'D0103F',
};
const THEME = {
  name: 'Arth',
  headFontFace: 'Calibri',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: HEX.ink, lt1: HEX.white, dk2: HEX.midnight, lt2: HEX.ground,
    accent1: HEX.blue, accent2: HEX.amber, accent3: HEX.green, accent4: HEX.cyan,
    accent5: HEX.sky, accent6: HEX.red, hlink: HEX.cyan, folHlink: HEX.midnight,
  },
};

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.title = 'Arth: the AI business partner on every Paytm Soundbox';
pres.author = 'Team Arth';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const ACC = { blue: C.accent1, amber: C.accent2, green: C.accent3, cyan: C.accent4, sky: C.accent5, red: C.accent6 };

// ---- layouts ---------------------------------------------------------------------------------------
pres.defineSlideMaster({
  title: 'Arth Dark Title',
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 2.0, w: 7.2, h: 1.6, fontSize: 66, bold: true, color: C.background1, valign: 'bottom' }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.7, y: 3.7, w: 7.2, h: 1.4, fontSize: 26, color: C.background1, valign: 'top' }, text: '' } },
  ],
});
pres.defineSlideMaster({
  title: 'Arth Content',
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontSize: 32, bold: true, color: C.text2, valign: 'middle' }, text: '' } },
    { text: { text: 'Arth  ·  Paytm Hackathon 2026  ·  Merchant Growth AI', options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent4, isTextBox: true } } },
  ],
  slideNumber: { x: 12.3, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4 },
});
pres.defineSlideMaster({
  title: 'Arth Dark Content',
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontSize: 32, bold: true, color: C.background1, valign: 'middle' }, text: '' } },
  ],
  slideNumber: { x: 12.3, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent1 },
});

// ---- helpers ---------------------------------------------------------------------------------------
async function iconPng(Icon, hex) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Icon, { color: '#' + hex, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}
// the deck's motif: a white icon in a coloured circle
async function badge(slide, Icon, x, y, d, fill, name) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name + ' circle' });
  const pad = d * 0.26;
  slide.addImage({ data: await iconPng(Icon, 'FFFFFF'), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, altText: name, objectName: name + ' icon' });
}
function card(slide, x, y, w, h, fill, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill },
    shadow: { type: 'outer', color: '0B1B33', opacity: 0.12, blur: 6, offset: 2, angle: 90 },
    objectName: name,
  });
}
function text(slide, t, opts) {
  slide.addText(t, { isTextBox: true, margin: 0, valign: 'top', ...opts });
}

(async () => {
  // ---- 1. Title -------------------------------------------------------------------------------------
  pres.addSection({ title: 'Opening' });
  let s = pres.addSlide({ masterName: 'Arth Dark Title', sectionTitle: 'Opening' });
  s.addText('Arth', { placeholder: 'title' });
  s.addText('The AI business partner on every Paytm Soundbox', { placeholder: 'body' });
  text(s, 'Merchant Growth AI  ·  Paytm Hackathon 2026', { x: 0.7, y: 5.3, w: 7, h: 0.4, fontSize: 16, color: ACC.blue });
  await badge(s, fa.FaMicrophone, 9.2, 1.6, 2.6, ACC.blue, 'Voice');
  card(s, 8.3, 4.6, 4.4, 0.7, C.background1, 'Utterance 1');
  text(s, '"Priya ka bill banao, 2 Parle-G aur ek Maggi"', { x: 8.5, y: 4.6, w: 4.1, h: 0.7, fontSize: 15, italic: true, color: C.text2, valign: 'middle' });
  card(s, 8.3, 5.5, 4.4, 0.7, ACC.amber, 'Utterance 2');
  text(s, '"Diwali ke liye kya kar sakte hain?"', { x: 8.5, y: 5.5, w: 4.1, h: 0.7, fontSize: 15, italic: true, color: C.text1, valign: 'middle' });
  s.addNotes('Arth turns the Paytm Soundbox every shop already has into an AI business partner the owner talks to in their own language.');

  // ---- 2. Problem -----------------------------------------------------------------------------------
  pres.addSection({ title: 'Problem and solution' });
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Problem and solution' });
  s.addText('Shops take payments digitally but still run on memory and paper', { placeholder: 'title' });
  const pains = [
    [fa.FaBook, 'Udhaar leaks', 'Khata lives in a notebook; dues are forgotten and never chased politely'],
    [fa.FaBoxOpen, 'Festival stock-outs', 'No forecast, so the best-selling items run out in Diwali week'],
    [fa.FaClock, 'No time for apps', 'Business apps want typing in English; the owner is at the counter all day'],
    [fa.FaUniversity, 'Invisible to lenders', 'Without clean records, a good shop cannot show it deserves a loan'],
  ];
  for (let i = 0; i < pains.length; i++) {
    const x = 0.6 + i * 3.08;
    card(s, x, 1.8, 2.85, 4.3, C.background2, 'Pain ' + (i + 1));
    await badge(s, pains[i][0], x + 0.3, 2.1, 0.9, ACC.red, pains[i][1]);
    text(s, pains[i][1], { x: x + 0.3, y: 3.25, w: 2.3, h: 0.5, fontSize: 20, bold: true, color: C.text2 });
    text(s, pains[i][2], { x: x + 0.3, y: 3.85, w: 2.3, h: 2.0, fontSize: 15, color: C.text1 });
  }
  text(s, 'The payment is digital. The business behind it is not.', { x: 0.6, y: 6.35, w: 12, h: 0.45, fontSize: 18, italic: true, color: ACC.cyan });
  s.addNotes('Paytm already sits at the counter of these shops. The gap is everything that happens around the payment: credit, stock, suppliers and growth.');

  // ---- 3. Solution ----------------------------------------------------------------------------------
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Problem and solution' });
  s.addText('Arth listens, does the work, and asks before it acts', { placeholder: 'title' });
  const says = [
    '"Priya ka bill banao, 2 Parle-G aur ek Maggi… khate mein daal do."',
    '"Diwali ke liye kya kar sakte hain?"',
    '"Meena ko dues ka message bhejo."',
  ];
  for (let i = 0; i < says.length; i++) {
    card(s, 0.6, 1.75 + i * 1.5, 5.6, 1.2, i === 1 ? ACC.sky : C.background2, 'Owner says ' + (i + 1));
    text(s, says[i], { x: 0.9, y: 1.75 + i * 1.5, w: 5.0, h: 1.2, fontSize: 17, italic: true, color: C.text2, valign: 'middle' });
  }
  const pillars = [
    [fa.FaLanguage, ACC.blue, 'Hears and speaks', 'Hindi, Hinglish, English and five more Indian languages, by voice'],
    [fa.FaBolt, ACC.green, 'Does the work', 'Billing, khata, stock, supplier orders, offers, collections, growth plans'],
    [fa.FaUserShield, ACC.amber, 'Asks for your haan', 'Money and customer messages always wait for the owner’s yes'],
  ];
  for (let i = 0; i < pillars.length; i++) {
    const y = 1.75 + i * 1.5;
    await badge(s, pillars[i][0], 6.8, y + 0.1, 1.0, pillars[i][1], pillars[i][2]);
    text(s, pillars[i][2], { x: 8.05, y: y + 0.05, w: 4.7, h: 0.45, fontSize: 20, bold: true, color: C.text2 });
    text(s, pillars[i][3], { x: 8.05, y: y + 0.5, w: 4.7, h: 0.75, fontSize: 15, color: C.text1 });
  }
  s.addNotes('One sentence from the owner can open a bill for a customer, add items and put it on khata; Arth answers in the same language and waits for a yes before money moves.');

  // ---- 4. Surfaces ----------------------------------------------------------------------------------
  pres.addSection({ title: 'Product' });
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Product' });
  s.addText('One brain, on every surface the shop already has', { placeholder: 'title' });
  const surfaces = [
    [fa.FaTabletAlt, 'Soundbox device', 'Owner and staff', 'Billing, khata, stock and approvals by voice or tap'],
    [fa.FaMicrophone, 'Voice Soundbox', 'Shops without a screen', 'The same AI through speaker and button'],
    [fa.FaWhatsapp, 'WhatsApp', 'Customers, suppliers', 'Bills, pay links, dues reminders, orders, POs'],
    [fa.FaMobileAlt, 'Console app', 'Owner', 'Approvals, reports, loans with OTP'],
    [fa.FaQrcode, 'Display + UPI page', 'Customer', 'Sees the bill and pays by QR'],
  ];
  for (let i = 0; i < surfaces.length; i++) {
    const x = 0.6 + i * 2.46;
    card(s, x, 1.8, 2.25, 4.5, i === 0 ? ACC.sky : C.background2, surfaces[i][1]);
    await badge(s, surfaces[i][0], x + 0.6, 2.1, 1.05, ACC.blue, surfaces[i][1]);
    text(s, surfaces[i][1], { x: x + 0.2, y: 3.35, w: 1.85, h: 0.75, fontSize: 18, bold: true, color: C.text2, align: 'center' });
    text(s, surfaces[i][2], { x: x + 0.2, y: 4.1, w: 1.85, h: 0.45, fontSize: 12, color: ACC.cyan, align: 'center' });
    text(s, surfaces[i][3], { x: x + 0.2, y: 4.6, w: 1.85, h: 1.5, fontSize: 14, color: C.text1, align: 'center' });
  }
  s.addNotes('Every surface talks to the same backend and the same AI, so a reminder sent from WhatsApp shows up on the device and in the Console immediately.');

  // ---- 5. Modules -----------------------------------------------------------------------------------
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Product' });
  s.addText('Eleven modules cover the whole shop', { placeholder: 'title' });
  const modules = [
    [fa.FaReceipt, 'Billing', 'Voice, tap or scan; cash, QR or khata'],
    [fa.FaBook, 'Khata', 'Interest-free udhaar, reminders with pay links'],
    [fa.FaBoxes, 'Stock', 'Low stock, expiry, receiving, prices'],
    [fa.FaTruck, 'Supply', 'Auto purchase orders, short-delivery claims'],
    [fa.FaShoppingBag, 'Orders', 'WhatsApp and storefront orders to delivery'],
    [fa.FaTags, 'Offers', 'Cashback, coupons, budget caps'],
    [fa.FaChartLine, 'Growth', 'Why sales moved, festival plans, campaigns'],
    [fa.FaRupeeSign, 'Hisaab', 'Daily close, settlements, GST summary'],
    [fa.FaUniversity, 'Capital', 'Loan readiness from real sales'],
    [fa.FaRobot, 'Agents', 'Night Shift, Reorder, Collections run themselves'],
    [fa.FaShieldAlt, 'Trust', 'Verifiable audit, consent, data erasure'],
  ];
  for (let i = 0; i < 12; i++) {
    const col = i % 4, row = Math.floor(i / 4);
    const x = 0.6 + col * 3.08, y = 1.65 + row * 1.75;
    if (i === 11) {
      card(s, x, y, 2.85, 1.5, ACC.amber, 'Vertical packs');
      text(s, '4 vertical packs', { x: x + 0.25, y: y + 0.2, w: 2.4, h: 0.45, fontSize: 18, bold: true, color: C.text1 });
      text(s, 'Kirana · Café · Pharmacy · Salon', { x: x + 0.25, y: y + 0.7, w: 2.4, h: 0.6, fontSize: 14, color: C.text1 });
      continue;
    }
    card(s, x, y, 2.85, 1.5, C.background2, modules[i][1]);
    await badge(s, modules[i][0], x + 0.2, y + 0.25, 0.7, ACC.blue, modules[i][1]);
    text(s, modules[i][1], { x: x + 1.05, y: y + 0.22, w: 1.7, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
    text(s, modules[i][2], { x: x + 1.05, y: y + 0.65, w: 1.7, h: 0.8, fontSize: 12, color: C.text1 });
  }
  s.addNotes('Each module was tested end to end on a live shop in a fresh browser: real backend calls, real state changes.');

  // ---- 6. AI ----------------------------------------------------------------------------------------
  pres.addSection({ title: 'AI and trust' });
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'AI and trust' });
  s.addText('One AI agent with 30+ tools over the shop’s own data', { placeholder: 'title' });
  const flow = [
    [fa.FaMicrophone, 'Owner speaks', 'Any of 8 languages'],
    [fa.FaAssistiveListeningSystems, 'Sarvam Saaras', 'Speech to text'],
    [fa.FaBrain, 'GPT agent', 'Picks tools, chains actions'],
    [fa.FaUserShield, 'Command Bus', 'Tier, policy, owner’s haan'],
    [fa.FaVolumeUp, 'Bulbul speaks', 'Grounded answer'],
  ];
  for (let i = 0; i < flow.length; i++) {
    const x = 0.6 + i * 2.5;
    await badge(s, flow[i][0], x + 0.55, 1.65, 1.0, i === 3 ? ACC.amber : ACC.blue, flow[i][1]);
    text(s, flow[i][1], { x, y: 2.75, w: 2.1, h: 0.4, fontSize: 17, bold: true, color: C.text2, align: 'center' });
    text(s, flow[i][2], { x, y: 3.15, w: 2.1, h: 0.4, fontSize: 13, color: C.text1, align: 'center' });
    if (i < flow.length - 1) {
      s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.85, y: 2.0, w: 0.5, h: 0.3, fill: { color: ACC.cyan }, line: { color: ACC.cyan }, objectName: 'Flow arrow ' + (i + 1) });
    }
  }
  const stats = [['30+', 'tools: sales, stock, khata, forecast, festivals, actions'], ['2–6 s', 'per AI answer (measured)'], ['~₹0.75', 'per AI call (measured)'], ['8', 'Indian languages by voice']];
  for (let i = 0; i < stats.length; i++) {
    const x = 0.6 + i * 3.08;
    card(s, x, 3.9, 2.85, 1.5, i === 0 ? ACC.sky : C.background2, 'Stat ' + stats[i][0]);
    text(s, stats[i][0], { x: x + 0.25, y: 3.95, w: 2.4, h: 0.75, fontSize: 36, bold: true, color: C.text2 });
    text(s, stats[i][1], { x: x + 0.25, y: 4.7, w: 2.4, h: 0.65, fontSize: 13, color: C.text1 });
  }
  card(s, 0.6, 5.65, 12.1, 1.05, C.text2, 'Example turn');
  text(s, [
    { text: '“Meena ke liye 1 Toor Dal aur 1 Fortune Atta, udhaar mein likh do”', options: { italic: true, color: C.background1, breakLine: true } },
    { text: '→ opens Meena’s bill, adds both items, puts it on khata, and waits for the owner’s haan (R2)', options: { color: ACC.blue } },
  ], { x: 0.9, y: 5.7, w: 11.5, h: 0.95, fontSize: 15, valign: 'middle' });
  s.addNotes('Every number Arth says comes from a tool; a Grounding Guard blocks anything unsupported. Counter commands like hatao or QR dikhao are instant and skip the model.');

  // ---- 7. Trust -------------------------------------------------------------------------------------
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'AI and trust' });
  s.addText('Built for trust: no money moves without the owner’s haan', { placeholder: 'title' });
  const tiers = [
    ['R0', 'Reads', 'khud', C.background2, C.text2],
    ['R1', 'Small changes', 'undo 30s', C.background2, C.text2],
    ['R2', 'Money', 'aapki haan', ACC.amber, C.text1],
    ['R3', 'Messages, orders', 'do baar poochho', ACC.red, C.background1],
    ['R4', 'Loans, refunds', 'Console + OTP', C.text2, C.background1],
  ];
  for (let i = 0; i < tiers.length; i++) {
    const x = 0.6 + i * 2.46;
    card(s, x, 1.7, 2.25, 1.6, tiers[i][3], 'Tier ' + tiers[i][0]);
    text(s, tiers[i][0], { x: x + 0.2, y: 1.8, w: 1.85, h: 0.55, fontSize: 28, bold: true, color: tiers[i][4] });
    text(s, tiers[i][1], { x: x + 0.2, y: 2.35, w: 1.85, h: 0.4, fontSize: 15, bold: true, color: tiers[i][4] });
    text(s, tiers[i][2], { x: x + 0.2, y: 2.75, w: 1.85, h: 0.4, fontSize: 13, italic: true, color: tiers[i][4] });
  }
  const guards = [
    [fa.FaHandshake, 'Consent first', 'No WhatsApp to a customer without their own yes; the owner can still send a dues reminder any time to those who agreed'],
    [fa.FaBalanceScale, 'Fair khata', 'No interest, no late fees, no shaming words: a Critic blocks them'],
    [fa.FaUserSecret, 'Privacy', 'Customer names are masked before the AI sees them; erasure keeps the audit intact'],
    [fa.FaLink, 'Tamper-evident audit', 'Hash-chained log with a one-tap Verify; agents can never approve'],
  ];
  for (let i = 0; i < guards.length; i++) {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 6.15, y = 3.75 + row * 1.5;
    await badge(s, guards[i][0], x, y, 0.85, ACC.green, guards[i][1]);
    text(s, guards[i][1], { x: x + 1.05, y: y - 0.02, w: 4.85, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
    text(s, guards[i][2], { x: x + 1.05, y: y + 0.42, w: 4.85, h: 0.9, fontSize: 14, color: C.text1 });
  }
  s.addNotes('Risk tiers come from policy, not from the model. The AI can only propose; people approve.');

  // ---- 8. Demo --------------------------------------------------------------------------------------
  pres.addSection({ title: 'Demo' });
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Demo' });
  s.addText('Demo: Gupta General Store, ten days before Diwali', { placeholder: 'title' });
  const beats = [
    ['Morning brief', 'Night Shift ran; 3 reorders wait. “Haan, teeno.”'],
    ['Counter', 'Priya’s bill by voice, counter hint, paid by UPI QR'],
    ['Festival stock', 'Arth drafts a sugar PO; owner says yes'],
    ['Fraud check', 'A forwarded ₹450 screenshot is verified'],
    ['Diwali plan', 'Diagnosis, plan and live offers'],
    ['Khata by voice', '“Priya ne 50 jama kiye” → read-back → haan'],
    ['Trust', 'Ask in Tamil, then verify the audit'],
  ];
  s.addShape(pres.shapes.LINE, { x: 1.35, y: 2.15, w: 10.38, h: 0, line: { color: ACC.cyan, width: 2 }, objectName: 'Timeline' });
  for (let i = 0; i < beats.length; i++) {
    const x = 0.6 + i * 1.73;
    s.addShape(pres.shapes.OVAL, { x: x + 0.45, y: 1.85, w: 0.6, h: 0.6, fill: { color: i === 0 ? ACC.amber : ACC.blue }, line: { color: C.background1, width: 2 }, objectName: 'Beat ' + (i + 1) });
    text(s, String(i + 1), { x: x + 0.45, y: 1.85, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: C.background1, align: 'center', valign: 'middle' });
    text(s, beats[i][0], { x, y: 2.65, w: 1.55, h: 0.7, fontSize: 15, bold: true, color: C.text2, align: 'center' });
    text(s, beats[i][1], { x, y: 3.35, w: 1.55, h: 1.7, fontSize: 12, color: C.text1, align: 'center' });
  }
  card(s, 0.6, 4.75, 12.1, 1.3, ACC.sky, 'Stage note');
  await badge(s, fa.FaDesktop, 0.85, 4.95, 0.9, ACC.blue, 'Stage');
  text(s, 'One stage: the Soundbox device, customer and supplier phones, and live Trace, AI calls and Logs side by side. The saved demo restores in about 3 seconds.', { x: 2.0, y: 4.8, w: 10.5, h: 1.2, fontSize: 16, color: C.text2, valign: 'middle' });
  s.addNotes('Run python dev.py demo, open /stage and /director, and press Next beat. Each beat runs live on the backend.');

  // ---- 9. Architecture and scale ----------------------------------------------------------------------
  pres.addSection({ title: 'Scale and business' });
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Scale and business' });
  s.addText('Architected to scale from one shop to Paytm’s merchant base', { placeholder: 'title' });
  const stack = [
    ['Surfaces', 'Device · Voice · WhatsApp · Console · Display', C.background2, C.text2],
    ['Command Bus', 'Tier · policy · approval · audit · events', ACC.amber, C.text1],
    ['Modules + agents', '11 domains · playbooks · vertical packs', C.background2, C.text2],
    ['AI router', 'Azure GPT · Groq · Sarvam · replay', ACC.sky, C.text2],
    ['Data', 'Per-shop isolation · append-only money rows', C.text2, C.background1],
  ];
  for (let i = 0; i < stack.length; i++) {
    const y = 1.6 + i * 1.0;
    card(s, 0.6, y, 5.6, 0.85, stack[i][2], stack[i][0]);
    text(s, stack[i][0], { x: 0.85, y, w: 1.9, h: 0.85, fontSize: 16, bold: true, color: stack[i][3], valign: 'middle' });
    text(s, stack[i][1], { x: 2.75, y, w: 3.35, h: 0.85, fontSize: 13, color: stack[i][3], valign: 'middle' });
  }
  const scale = [
    'A new shop type is a config pack, not a rewrite',
    'Every write goes through one bus: new modules inherit safety',
    'Counter commands skip the model; AI spend is capped per agent per day',
    'Path to scale: Postgres with tenant sharding, Kafka events, stateless API pods, regional model deployments',
    'Billing keeps working offline and syncs later',
  ];
  text(s, scale.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < scale.length - 1 } })), { x: 6.7, y: 1.6, w: 6.0, h: 3.3, fontSize: 15, color: C.text1, paraSpaceAfter: 8 });
  const proof = [['1,350+', 'automated tests'], ['16', 'demo scenarios × 10 runs'], ['4', 'vertical packs'], ['< ₹1', 'back office per shop per day (target)']];
  for (let i = 0; i < proof.length; i++) {
    const x = 6.7 + (i % 2) * 3.05, y = 5.0 + Math.floor(i / 2) * 0.95;
    text(s, proof[i][0], { x, y, w: 1.35, h: 0.8, fontSize: 26, bold: true, color: ACC.cyan, valign: 'middle' });
    text(s, proof[i][1], { x: x + 1.35, y, w: 1.55, h: 0.8, fontSize: 12, color: C.text1, valign: 'middle' });
  }
  s.addNotes('Prototype runs on SQLite per environment; the production path swaps storage and transport, not the domain code.');

  // ---- 10. Business model -------------------------------------------------------------------------------
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Scale and business' });
  s.addText('Monetise through the Soundbox base Paytm already has', { placeholder: 'title' });
  const plans = [
    ['Arth Free', '₹0', '', 'Voice billing, today’s sales, khata balance, daily brief', C.background2, C.text2],
    ['Arth Pro', '₹99–199', ' / month', 'Reminders with pay links, stock and reorders, offers, festival plans, WhatsApp orders', ACC.sky, C.text2],
    ['Arth Business', '₹399+', ' / month', 'Multiple staff, pharmacy / café / salon packs, GST reports, storefront', C.text2, C.background1],
  ];
  for (let i = 0; i < plans.length; i++) {
    const x = 0.6 + i * 2.75;
    const price = i === 2 ? ACC.blue : ACC.cyan;
    card(s, x, 1.65, 2.55, 3.3, plans[i][4], plans[i][0]);
    text(s, plans[i][0], { x: x + 0.25, y: 1.85, w: 2.1, h: 0.45, fontSize: 18, bold: true, color: plans[i][5] });
    text(s, [
      { text: plans[i][1], options: { fontSize: 26, bold: true, color: price } },
      { text: plans[i][2], options: { fontSize: 14, color: price } },
    ], { x: x + 0.25, y: 2.35, w: 2.1, h: 0.6, valign: 'middle' });
    text(s, plans[i][3], { x: x + 0.25, y: 3.1, w: 2.1, h: 1.7, fontSize: 14, color: plans[i][5] });
  }
  text(s, 'Pricing is a proposal; it rides on the Soundbox rental, with no new hardware.', { x: 0.6, y: 5.15, w: 8.1, h: 0.4, fontSize: 12, italic: true, color: ACC.cyan });
  const streams = [
    [fa.FaUniversity, 'Lending', 'Sales-backed loan offers; distribution fees'],
    [fa.FaTags, 'Brand-funded offers', 'Brands pay for item coupons and cashback'],
    [fa.FaQrcode, 'Payment volume', 'Pay links in reminders recover udhaar via UPI'],
    [fa.FaTruck, 'Supplier network', 'Commission on POs placed through Arth'],
  ];
  text(s, 'Beyond subscriptions', { x: 9.0, y: 1.65, w: 3.7, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  for (let i = 0; i < streams.length; i++) {
    const y = 2.2 + i * 1.05;
    await badge(s, streams[i][0], 9.0, y, 0.7, ACC.green, streams[i][1]);
    text(s, streams[i][1], { x: 9.85, y: y - 0.03, w: 2.85, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
    text(s, streams[i][2], { x: 9.85, y: y + 0.32, w: 2.85, h: 0.6, fontSize: 12, color: C.text1 });
  }
  s.addNotes('Free tier drives adoption across the Soundbox base; Pro converts on recovered udhaar and festival sales; lending and brand offers grow revenue per merchant.');

  // ---- 11. Go to market and impact ----------------------------------------------------------------------
  s = pres.addSlide({ masterName: 'Arth Content', sectionTitle: 'Scale and business' });
  s.addText('Pilot at Diwali, sell outcomes, scale by language and vertical', { placeholder: 'title' });
  const steps = [
    ['Pilot', '2–3 cities, kirana first, timed with Diwali'],
    ['Sell outcomes', '“Udhaar recovered”, “no stock-out this Diwali”, “loan-ready”'],
    ['Onboard in 5 minutes', 'Paytm field agents set up by voice; Arth guides the owner'],
    ['Expand', 'Café, pharmacy, salon packs and more regional voices'],
  ];
  for (let i = 0; i < steps.length; i++) {
    const y = 1.65 + i * 1.2;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y, w: 0.75, h: 0.75, fill: { color: ACC.blue }, line: { color: ACC.blue }, objectName: 'Step ' + (i + 1) });
    text(s, String(i + 1), { x: 0.6, y, w: 0.75, h: 0.75, fontSize: 20, bold: true, color: C.background1, align: 'center', valign: 'middle' });
    text(s, steps[i][0], { x: 1.55, y: y - 0.02, w: 4.9, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
    text(s, steps[i][1], { x: 1.55, y: y + 0.38, w: 4.9, h: 0.6, fontSize: 14, color: C.text1 });
  }
  card(s, 6.9, 1.65, 5.8, 4.75, C.background2, 'Impact metrics');
  text(s, 'What we will measure', { x: 7.2, y: 1.85, w: 5.2, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  const metrics = [
    'Khata recovered per shop per month, days to collect',
    'Stock-outs in festival weeks',
    'Repeat customers and sales uplift against a holdout group',
    'UPI share of collections, loan-ready merchants',
    'Owner minutes saved per day',
  ];
  for (let i = 0; i < metrics.length; i++) {
    const y = 2.45 + i * 0.75;
    await badge(s, fa.FaCheck, 7.2, y + 0.05, 0.45, ACC.green, 'Metric ' + (i + 1));
    text(s, metrics[i], { x: 7.85, y, w: 4.6, h: 0.6, fontSize: 15, color: C.text1, valign: 'middle' });
  }
  s.addNotes('Every growth claim is measured against a holdout group, so merchants and Paytm see real uplift, not vanity numbers.');

  // ---- 12. Roadmap and close ----------------------------------------------------------------------------
  pres.addSection({ title: 'Close' });
  s = pres.addSlide({ masterName: 'Arth Dark Content', sectionTitle: 'Close' });
  s.addText('Roadmap: from pilot to every Paytm counter', { placeholder: 'title' });
  const horizons = [
    ['3 months', 'Live pilot · WhatsApp Business API · Paytm payment rails · more regional voices'],
    ['6 months', 'Supplier marketplace · brand-funded offers · Console lending with partners'],
    ['12 months', 'All vertical packs · multi-store chains · per-shop restock and credit-risk models'],
  ];
  for (let i = 0; i < horizons.length; i++) {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.65, w: 3.85, h: 2.2, rectRadius: 0.12, fill: { color: C.background1, transparency: 88 }, line: { color: ACC.blue, width: 1 }, objectName: horizons[i][0] });
    text(s, horizons[i][0], { x: x + 0.3, y: 1.85, w: 3.3, h: 0.5, fontSize: 22, bold: true, color: ACC.blue });
    text(s, horizons[i][1], { x: x + 0.3, y: 2.45, w: 3.3, h: 1.2, fontSize: 15, color: C.background1 });
  }
  await badge(s, fa.FaStore, 0.6, 4.55, 1.5, ACC.amber, 'Every shop');
  text(s, 'Arth: har dukaan ka AI partner', { x: 2.4, y: 4.6, w: 10, h: 0.8, fontSize: 36, bold: true, color: C.background1 });
  text(s, 'Thank you', { x: 2.4, y: 5.4, w: 9, h: 0.6, fontSize: 22, color: ACC.blue });
  s.addNotes('Ask: pilot Arth with a set of Soundbox merchants before Diwali and measure recovered udhaar and festival sales.');

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('wrote ' + OUT);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
