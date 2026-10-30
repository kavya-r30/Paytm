from c2 import *
from ai import pipeline
OUT = '/home/claude/design/project/'
def W(name, s): open(OUT + name + '.dc.html', 'w').write(s)
def h2(t, right=''):
    return '<div style="display: flex; align-items: center; justify-content: space-between; gap: 10px"><h2 style="margin: 0; font-size: 17px; font-weight: 700">%s</h2>%s</div>' % (t, right)
def tier(t, txt):
    c = {'R0': (GROUND, INK2), 'R1': (GROUND, INK2), 'R2': (AMBTINT, AMBT), 'R3': (REDT, RED)}[t]
    return chip(t if txt in ('khud', 'haan') else '%s · %s' % (t, txt), c[0], c[1], 26, 12, 700, False)

# ---------- ASK ARTH (chat with chart + provenance) ----------
days = [('Fri', 6900), ('Sat', 9100), ('Sun', 10400), ('Mon', 6200), ('Tue', 7300), ('Wed', 8450), ('Thu', 3900)]
mx = 11000; bars = ''
for i, (d, v) in enumerate(days):
    hgt = round(120 * v / mx); x = 14 + i * 58; today = i == 6
    bars += '<rect x="%d" y="%d" width="34" height="%d" rx="8" fill="%s"/><text x="%d" y="160" text-anchor="middle" font-size="12" fill="%s">%s</text>' % (x, 140 - hgt, hgt, '#9BE3F9' if today else CYAN, x + 17, INK3, d)
bars += '<text x="%d" y="%d" text-anchor="middle" font-size="12" font-weight="700" fill="%s">₹10.4k</text>' % (14 + 2 * 58 + 17, 140 - round(120 * 10400 / mx) - 6, MID)
chart = '<svg viewBox="0 0 420 168" width="100%%" height="168" role="img" aria-label="Bikri pichhle 7 din, sabse zyada Ravivaar ₹10,400"><line x1="0" x2="420" y1="140" y2="140" stroke="%s"/>%s</svg>' % (LINE, bars)
ask_body = ('<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 14px; min-width: 0; overflow: hidden">'
  '<div style="align-self: flex-end; max-width: 70%%; padding: 12px 16px; border-radius: 20px 20px 6px 20px; background: %s; color: #FFFFFF; font-size: 15.5px; display: flex; align-items: center; gap: 10px">%s"Is hafte kitna kamaya?"</div>'
  '<div style="display: flex; gap: 14px; align-items: flex-start">%s'
   '<section style="flex-grow: 1; %s padding: 20px 22px; display: flex; flex-direction: column; gap: 12px">'
    '<p style="margin: 0; font-size: 18px; line-height: 1.5; font-weight: 500">Is hafte ab tak <b>₹52,250</b> ki bikri, pichhle hafte se <b style="color: %s">8%% zyada</b>. Ravivaar sabse achha raha.</p>'
    '%s'
    '<div style="display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: %s">%s<span>214 bills · UPI ledger · 3 cash entries aapne kiye · aaj ka din adhoora</span></div>'
    '<div style="display: flex; gap: 8px; flex-wrap: wrap">%s%s%s</div></section></div></div>'
 '<aside style="width: 250px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px">'
  '<span style="font-size: 13px; font-weight: 600; color: %s">Arth ne yeh bhi dekha</span>%s%s'
  '<div style="margin-top: auto; font-size: 12.5px; line-height: 1.5; color: %s">Arth sirf aapki dukaan ka data padhta hai. Paisa hilane wala koi kaam aapki haan ke bina nahi.</div></aside>') % (
  MID, svg(I['mic'], 16, 2), mascot('speaking', 54), card(), GRN, chart, INK3, svg(I['lock'], 14, 2),
  btn(svg(I['send'], 16, 2) + 'WhatsApp pe weekly report', 'primary', 42, 14), btn('Kharcha bhi dikhao', 'tint', 42, 14), btn('Rozana bhejo, 9 baje', 'ghost', 42, 14),
  INK3,
  arth_note('Ravivaar ko Maggi aur doodh do baar khatam hue. Agle Ravivaar 1 crate extra?'),
  arth_note('Mehta ji ka khata 21 din purana. Reminder kal 9 baje set hai.'), INK3)
W('ScreenAsk', screen('Ask Arth', 'home', 'Arth se poochho', 'Hindi, English ya Hinglish · bolo ya likho', ask_body,
  right=chip(dot(GRNF) + 'Sun raha hoon', GRNT, GRN, 32, 13, 600, False), chips=['Kal kya mangwaun?', 'Sabse zyada kya bika?', 'Kis ka khata baaki?'], mstate='speaking'))

# ---------- TEAM (agents) ----------
agents = [('Bikri', 'Billing, receipts, UPI match', 'Aaj 42 bills · 2 receipts pending', GRNF, 'R1', 'khud'),
          ('Stock', 'Kam stock, expiry, reorder', 'Dry fruits 40% · order suggest kiya', AMB, 'R2', 'haan'),
          ('Kharid', 'Supplier rates, PO, claims', '9 baje 2 suppliers se rate', CYAN, 'R2', 'haan'),
          ('Khata', 'Udhaar, reminders, limits', 'Mehta ji reminder 9 baje', CYAN, 'R2', 'haan'),
          ('Hisaab', 'Raat ka reconciliation', '3 payments mile · ₹20 cash kam', GRNF, 'R0', 'khud'),
          ('Grahak', 'Offers, coupons, win-back', '5 purane grahak · 1 holdout', AMB, 'R2', 'haan'),
          ('Andaaza', 'Forecast, Diwali demand', 'Aaj ₹8.2k–10.8k', GRNF, 'R0', 'khud'),
          ('Pehredaar', 'Rules, limits, audit log', 'Sab theek · 0 blocked', GRNF, 'R0', 'khud')]
ag = ''.join('<div style="%s padding: 14px 14px; display: flex; flex-direction: column; gap: 8px; min-width: 0">'
             '<div style="display: flex; align-items: center; gap: 10px">%s<span style="font-size: 16px; font-weight: 700">%s</span><span style="margin-left: auto">%s</span></div>'
             '<span style="font-size: 12.5px; color: %s">%s</span><span style="font-size: 14px; font-weight: 500">%s</span></div>' % (card('border-radius: 20px;'), dot(c, 10), n, tier(t, tt), INK3, role, st)
             for n, role, st, c, t, tt in agents)
team_body = ('<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 16px; min-width: 0">'
  '%s<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px">%s</div>%s</div>') % (
  arth_note('Kal raat se meri team ne <b>14 kaam</b> kiye. <b>3</b> aapki haan ka intezaar kar rahe hain, baaki sab apne aap ho gaye. Har kaam ka hisaab log mein hai.', 'align-items: center'), ag,
  '<section style="%s padding: 18px 22px 20px; display: flex; flex-direction: column; gap: 16px"><div style="display: flex; align-items: center; gap: 10px"><h2 style="margin: 0; font-size: 16px; font-weight: 700">Abhi chal raha · Diwali stock</h2><span style="margin-left: auto; font-size: 12.5px; color: %s">4 helpers · 8:02 se</span></div>%s</section>' % (card(), INK3, pipeline([('Stock ne dekha', 'Dry fruits 40% · 8:02', 'done'), ('Kharid ne poocha', '2 suppliers · 8:05', 'done'), ('Rates aaye', 'Balaji ₹850 sasta', 'done'), ('Pehredaar', 'Budget ke andar', 'done'), ('Aapki haan', 'Intezaar', 'wait'), ('WhatsApp order', 'Haan ke baad', 'next')])))
W('ScreenTeam', screen('Arth team', 'grid', 'Arth ki team', '8 helpers · R0 khud karte hain, R2 se upar aapki haan', team_body,
  right=btn('Activity log', 'ghost', 40, 14) + btn('3 haan baaki', 'amber', 40, 14), chips=['Kya kya kiya raat ko?', 'Stock ko rok do', 'Limit badlo'], mstate='idle'))

# ---------- APPROVAL (quote decision) ----------
def quote(name, lead, price, terms, best):
    return ('<div style="flex: 1; padding: 18px; border-radius: 20px; %s display: flex; flex-direction: column; gap: 6px">'
            '<div style="display: flex; align-items: center; justify-content: space-between"><span style="font-size: 16px; font-weight: 700">%s</span>%s</div>'
            '<span style="font-size: 30px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums">%s</span>'
            '<span style="font-size: 13px; color: %s">%s</span><span style="font-size: 13px; color: %s">%s</span></div>') % (
            'background: %s; box-shadow: inset 0 0 0 2px %s;' % (SKY, CYAN) if best else 'background: #FFFFFF; box-shadow: inset 0 0 0 1px %s;' % LINE,
            name, chip('Sasta', MID, '#FFFFFF', 26, 12, 700, False) if best else '', price, INK2, terms, INK3, lead)
lines = [('nuts', 'Kaju 1 kg', '×6'), ('nuts', 'Badam 1 kg', '×6'), ('diya', 'Diye (pack 12)', '×20'), ('sweet', 'Soan papdi 500 g', '×24')]
ll = ''.join('<div style="display: flex; align-items: center; gap: 12px; padding: 8px 0">%s<span style="font-size: 14.5px; font-weight: 500; flex-grow: 1">%s</span><span style="font-size: 14px; color: %s">%s</span></div>' % (pack(k, 32), n, INK2, q) for k, n, q in lines)
appr_body = ('<section style="flex-grow: 1; %s padding: 22px 24px; display: flex; flex-direction: column; gap: 16px; min-width: 0">'
  '%s<div style="display: flex; gap: 14px">%s%s</div>'
  '%s'
  '<div style="margin-top: auto; display: flex; gap: 10px; align-items: center">%s%s<span style="margin-left: auto; font-size: 12.5px; color: %s">Rok sakte hain 30 min tak</span></div></section>'
 '<section style="width: 280px; flex-shrink: 0; %s padding: 20px; display: flex; flex-direction: column; gap: 6px">%s%s'
  '<div style="margin-top: auto; padding-top: 12px; border-top: 1px solid %s; display: flex; justify-content: space-between; font-size: 13.5px"><span style="color: %s">Budget bacha</span><b style="font-variant-numeric: tabular-nums">₹31,600</b></div></section>') % (
  card(), h2('Diwali stock · 2 rates aaye', tier('R2', 'aapki haan')),
  quote('Balaji Traders', 'Kal shaam tak · 3 baar time pe', '₹18,400', '15 din udhaar · free delivery', True),
  quote('Agarwal & Sons', 'Parson · pichhli baar 2 din late', '₹19,250', '7 din udhaar', False),
  arth_note('Balaji <b>₹850 sasta</b> aur jaldi. Pichhle 3 order time pe aaye. Kaju ka rate dono jagah same, farak diye aur soan papdi mein hai.'),
  btn('Balaji ko order bhejo · ₹18,400', 'primary', 54, 16), btn('Mol-bhaav karo', 'ghost', 54, 15), INK3,
  card(), h2('Order mein kya hai'), ll, LINE, INK3)
W('ScreenApproval', screen('Arth approval', 'home', 'Ek faisla', 'Kharid helper ne 2 rates mangwaye · 8:10 am', appr_body,
  right=btn('Baad mein', 'text', 40, 14), chips=['Kaju 4 kg hi lo', 'Agarwal se 5% kam karwao'], mstate='confirming'))

# ---------- CLAIM (WhatsApp compose to supplier) ----------
claim_bg = ('<section style="flex-grow: 1; %s padding: 22px; display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 17px; font-weight: 700">PO-118 · Agarwal & Sons</h2>'
  '<div style="display: flex; justify-content: space-between; font-size: 14px; padding: 8px 0; border-bottom: 1px solid %s"><span>Oil 1 L · mangaya 24</span><b style="color: %s">aaye 20</b></div>'
  '<div style="display: flex; justify-content: space-between; font-size: 14px; padding: 8px 0"><span>Atta 5 kg · mangaya 10</span><b>aaye 10</b></div></section>') % (card(), LINE, RED)
def att(icon, t, s):
    return '<div style="display: flex; align-items: center; gap: 10px; padding: 8px 12px 8px 8px; border-radius: 14px; background: %s"><span style="width: 36px; height: 36px; border-radius: 10px; background: #FFFFFF; color: %s; display: flex; align-items: center; justify-content: center">%s</span><span style="display: flex; flex-direction: column"><span style="font-size: 13.5px; font-weight: 600">%s</span><span style="font-size: 12px; color: %s">%s</span></span></div>' % (GROUND, MID, svg(I[icon], 18, 1.9), t, INK3, s)
out_msg = ('<div style="align-self: flex-end; max-width: 88%%; padding: 10px 12px 7px; border-radius: 16px 16px 4px 16px; background: #D9FDD3; font-size: 14.5px; line-height: 1.5; color: %s">'
  'नमस्ते अग्रवाल जी, PO-118 में तेल 1 L के 24 मँगाए थे, 20 ही आए। बिल की फ़ोटो साथ में है। 4 × ₹165 = <b>₹660</b> अगले बिल में कम कर दीजिए या बाक़ी माल भेज दीजिए।<br>— रमेश, गुप्ता जनरल स्टोर'
  '<div style="text-align: right; font-size: 10.5px; color: %s; margin-top: 3px">draft</div></div>') % (INK, INK3)
claim_sheet = ('<div style="position: absolute; inset: 0; background: rgba(0,46,110,0.32); display: flex; align-items: center; justify-content: flex-end; padding-right: 40px">'
 '<section role="dialog" aria-label="Claim WhatsApp" style="width: 520px; height: 640px; border-radius: 28px; background: #FFFFFF; box-shadow: 0 30px 80px rgba(0,30,80,0.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px">'
  '<div style="display: flex; align-items: center; gap: 12px">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 17px; font-weight: 700">Agarwal & Sons</span><span style="font-size: 12.5px; color: %s">WhatsApp · +91 98•••• 2207 · हिंदी</span></div><button aria-label="Close" style="width: 40px; height: 40px; border-radius: 12px; border: none; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</button></div>'
  '<div style="flex-grow: 1; border-radius: 20px; background: #EFEAE2; padding: 14px; display: flex; flex-direction: column; justify-content: flex-end; gap: 8px">%s</div>'
  '<div style="display: flex; gap: 8px">%s%s</div>'
  '<div style="display: flex; gap: 8px">%s%s%s</div>'
  '<div style="display: flex; gap: 10px">%s%s</div>'
  '<span style="font-size: 12.5px; color: %s; display: flex; align-items: center; gap: 6px">%sArth ne draft kiya · aapki haan ke baad hi jayega · supplier ki bhasha mein</span></section></div>') % (
  avatar('AS', '#FFF1E6', '#B45309', 44), INK3, GROUND, INK2, svg(I['x'], 18, 2), out_msg,
  att('scan', 'Bill photo', 'Kal 6:40 pm'), att('bill', 'PO-118', '24 × Oil 1 L'),
  chip('हिंदी', MID, '#FFFFFF', 32, 13.5, 600, False), chip('English', '#FFFFFF', INK, 32, 13), chip('Narm lahja', '#FFFFFF', INK, 32, 13),
  btn(svg(I['send'], 18, 2) + 'WhatsApp pe bhejo', 'primary', 52, 15, 'flex: 1'), btn('Badlo', 'ghost', 52, 15), INK3, svg(I['lock'], 14, 2))
W('ScreenClaim', screen('Arth supplier claim', 'box', 'Maal kam aaya', 'Kal ki delivery · Arth ne bill se milaya', claim_bg, overlay=claim_sheet, nodock=True, mstate='confirming'))

# ---------- LANGUAGE ----------
langs = [('हिंदी', 'Hindi', True), ('English', 'English', False), ('Hinglish', 'Roman Hindi', False), ('मराठी', 'Marathi', False),
         ('தமிழ்', 'Tamil', False), ('বাংলা', 'Bengali', False), ('ગુજરાતી', 'Gujarati', False), ('తెలుగు', 'Telugu', False)]
lg = ''.join('<div style="height: 64px; padding: 0 16px; border-radius: 18px; display: flex; align-items: center; gap: 12px; %s"><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 18px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div>%s</div>'
             % ('background: %s; box-shadow: inset 0 0 0 2px %s' % (SKY, CYAN) if on else 'background: #FFFFFF; box-shadow: inset 0 0 0 1px %s' % LINE, n, INK3, e,
                '<span style="width: 26px; height: 26px; border-radius: 999px; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</span>' % (CYAN, MID, svg(I['check'], 15, 2.8)) if on else '') for n, e, on in langs)
def setrow(t, s, v, first=False):
    return '<div style="display: flex; align-items: center; gap: 12px; padding: 14px 0; %s"><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div>%s</div>' % ('' if first else 'border-top: 1px solid %s' % LINE, t, INK3, s, chip(v + svg(I['chevron'], 14, 2), GROUND, MID, 34, 14, 600, False))
lang_body = ('<section style="flex-grow: 1; %s padding: 20px; display: flex; flex-direction: column; gap: 12px; min-width: 0">%s<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px">%s</div></section>'
 '<div style="width: 320px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px">'
  '<section style="%s padding: 6px 20px">%s%s%s</section>'
  '<section style="%s padding: 18px 20px; display: flex; flex-direction: column; gap: 12px">%s'
   '<div style="display: flex; gap: 12px; align-items: center">%s<p style="margin: 0; font-family: %s; font-size: 16px; line-height: 1.55">कल ₹8,450 की बिक्री हुई। मेहता जी को याद दिलाऊँ?</p></div>%s</section></div>') % (
  card(), h2('Screen ki bhasha'), lg,
  card(), setrow('Awaaz', 'Arth kis bhasha mein bole · Sarvam AI', 'हिंदी', True), setrow('Main kya bolunga', 'Mix chalega, Arth samajh lega', 'Hinglish'), setrow('Grahak messages', 'Har grahak ki apni pasand', 'Grahak ki bhasha'),
  card(), h2('Aise dikhega', chip('Preview', SKY, CYT, 26, 12, 700, False)), mascot('speaking', 52), FF_HI, btn(svg(I['speaker'], 16, 2) + 'Sun ke dekho', 'tint', 42, 14, 'align-self: flex-start'))
W('ScreenLanguage', screen('Arth language', 'grid', 'Bhasha · भाषा', 'Screen, awaaz aur grahak messages alag-alag chun sakte hain', lang_body, nodock=True))
print('ok')
