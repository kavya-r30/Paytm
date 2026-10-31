from c2 import *
from sb import tier
OUT = '/home/claude/design/project/'
def board(title, body, w, h):
    b = '<div style="width: %dpx; height: %dpx; background: #FFFFFF; font-family: %s; color: %s; padding: 48px 56px; box-sizing: border-box; display: flex; flex-direction: column; gap: 32px; overflow: hidden">%s</div>' % (w, h, FF, INK, body)
    return page(title, b, w=w, h=h)
def sec(label, inner, extra=''):
    return '<section style="display: flex; flex-direction: column; gap: 14px; %s"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: %s">%s</span>%s</section>' % (extra, INK3, label, inner)
def ttl(t, s):
    return '<div style="display: flex; flex-direction: column; gap: 6px"><h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.025em">%s</h1><span style="font-size: 15px; color: %s">%s</span></div>' % (t, INK2, s)
row = lambda inner, gap=16, extra='': '<div style="display: flex; gap: %dpx; align-items: flex-start; flex-wrap: wrap; %s">%s</div>' % (gap, extra, inner)

# ---------- FOUNDATIONS ----------
sw = [('Midnight', MID, '#FFFFFF', 'Text, dark buttons, active nav'), ('Paytm Blue', CYAN, MID, 'Primary fill · midnight text 5.8:1'), ('Sky', SKY, MID, 'Arth notes, selection'),
      ('Ground', GROUND, INK, 'App background'), ('Ink', INK, '#FFFFFF', 'Body text'), ('Cyan text', CYT, '#FFFFFF', 'Links on white 4.9:1')]
st = [('Green', GRNF, GRN, GRNT, 'Paisa aaya, sab theek'), ('Amber', AMB, AMBT, AMBTINT, 'Aapki haan chahiye'), ('Red', '#F04438', RED, REDT, 'Udhaar, kam maal')]
swh = ''.join('<div style="width: 196px; display: flex; flex-direction: column; gap: 8px"><div style="height: 88px; border-radius: 18px; background: %s; box-shadow: inset 0 0 0 1px rgba(16,24,40,0.06); padding: 12px 14px; box-sizing: border-box; display: flex; align-items: flex-end; color: %s; font-size: 13px; font-weight: 700">%s</div><span style="font-size: 12.5px; color: %s">%s · %s</span></div>' % (b, f, n, INK3, b, u) for n, b, f, u in sw)
sth = ''.join('<div style="flex: 1; display: flex; gap: 10px; align-items: center; padding: 14px 16px; border-radius: 18px; background: %s">%s<div style="display: flex; flex-direction: column"><span style="font-size: 14px; font-weight: 700; color: %s">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div></div>' % (t, dot(f, 12), tx, n, INK2, u) for n, f, tx, t, u in st)
type_ = ''.join('<div style="display: flex; align-items: baseline; gap: 20px; padding: 8px 0; border-bottom: 1px solid %s"><span style="width: 120px; font-size: 12.5px; color: %s">%s</span><span style="font-size: %dpx; font-weight: %d; letter-spacing: %s">%s</span></div>' % (LINE, INK3, l, s, w, ls, t)
                for l, s, w, ls, t in [('Amount 56/800', 56, 800, '-0.035em', '₹9,400'), ('Title 24/700', 24, 700, '-0.02em', 'Namaste, Ramesh ji'), ('Arth voice 21/500', 21, 500, '-0.01em', 'Kal ₹8,450 ki bikri hui'), ('Body 15/500', 15, 500, '0', 'Mehta ji ko reminder 9 baje jayega'), ('Meta 12.5/500', 13, 500, '0', 'UPI · 9:13 am · UTR ••4821')])
scripts = ''.join('<div style="flex: 1; padding: 14px 16px; border-radius: 16px; background: %s; display: flex; flex-direction: column; gap: 4px"><span style="font-size: 22px; font-weight: 600">%s</span><span style="font-size: 12px; color: %s">%s</span></div>' % (GROUND, a, INK3, b)
                  for a, b in [('नमस्ते', 'Noto Sans Devanagari'), ('வணக்கம்', 'Noto Sans Tamil'), ('নমস্কার', 'Noto Sans Bengali'), ('નમસ્તે', 'Noto Sans Gujarati'), ('నమస్తే', 'Noto Sans Telugu')])
btns = btn('QR dikhao · ₹62', 'primary') + btn('Naya bill', 'dark') + btn('Teeno haan', 'amber') + btn('Ek-ek karke', 'ghost') + btn('Sun ke dekho', 'tint') + btn('Khate mein', 'danger') + btn('Baad mein', 'text')
chips = chip('Aaj ka hisaab', '#FFFFFF', MID, 34, 13.5, 600) + chip(dot(AMB) + 'Needs you', AMBTINT, AMBT, 28, 12.5, 700, False) + chip('UPI', SKY, MID, 36, 13.5, 700, False) + tier('R0', 'khud') + tier('R2', 'aapki haan') + tier('R3', 'do baar poochho') + toggle(True) + toggle(False)
main = (ttl('Arth foundations', 'Paytm palette · ek screen par ek main kaam · Arth hamesha dikhe, kabhi beech mein na aaye') +
  '<div style="display: flex; gap: 48px"><div style="flex: 1.25; display: flex; flex-direction: column; gap: 28px">' +
   sec('Colour', row(swh, 16) + row(sth, 12, 'flex-wrap: nowrap')) + sec('Buttons', row(btns, 10, 'align-items: center')) + sec('Chips, tiers, toggles', row(chips, 10, 'align-items: center')) +
  '</div><div style="flex: 1; display: flex; flex-direction: column; gap: 28px">' +
   sec('Type · Inter + Noto', type_) + sec('Har script ke liye font', row(scripts, 8, 'flex-wrap: nowrap')) +
   sec('Arth note · AI ki awaaz', arth_note('Ye number pehle UPI se ₹340 pay kar chuka hai. Payer naam <b>Rohit K.</b> mila. Sahi hai?')) +
   sec('Surfaces', row(''.join('<div style="flex: 1; height: 72px; %s display: flex; align-items: center; justify-content: center; font-size: 12.5px; color: %s">%s</div>' % (s, INK3, l) for s, l in [(card(), 'Card · r24 · soft'), (card('box-shadow: %s;' % SH2) , 'Dock · r999 · lifted'), ('background: %s; border-radius: 20px;' % GROUND, 'Ground · r20')]), 12, 'flex-wrap: nowrap')) +
  '</div></div>')
open(OUT + 'Main.dc.html', 'w').write(board('Arth foundations', main, 1440, 1080))

# ---------- NAVIGATION + SHELL ----------
frame = lambda inner, w, h, extra='': '<div style="width: %dpx; height: %dpx; border-radius: 24px; background: %s; box-shadow: inset 0 0 0 1px %s; overflow: hidden; display: flex; %s">%s</div>' % (w, h, GROUND, LINE, extra, inner)
rails = ''.join('<div style="display: flex; flex-direction: column; gap: 8px; align-items: center">%s<span style="font-size: 12px; color: %s">%s</span></div>' % (frame(rail(a, hi, m), 80, 600), INK3, l)
                for a, hi, m, l in [('home', False, 'idle', 'Aaj · idle'), ('bill', False, 'listening', 'Bill · sun raha'), ('khata', True, 'thinking', 'खाता · हिंदी'), ('grid', False, 'alert', 'More · alert')])
docks = (frame('<div style="width: 100%; padding-top: 20px">' + dock(['Aaj ka hisaab', 'Diwali ki taiyari', 'Khata kitna baaki?']) + '</div>', 760, 150, 'flex-direction: column') +
         frame('<div style="width: 100%; padding-top: 20px">' + dock(['आज का हिसाब', 'दिवाली की तैयारी'], 'बोलिए या लिखिए — जैसे "शर्मा जी का हिसाब"', True) + '</div>', 760, 150, 'flex-direction: column'))
hdrs = frame('<div style="width: 100%">' + header('Bill 1042', 'Scan karo, tap karo ya bolo', btn('Bill rok do', 'text', 40, 14)) + '</div>', 760, 76) + frame('<div style="width: 100%">' + header('Ek faisla', 'Kharid helper ne 2 rates mangwaye', tier('R2', 'aapki haan') + btn('Baad mein', 'text', 40, 14)) + '</div>', 760, 76)
lp = ''.join(chip(t, b, f, 34, 14, 600, bd) for t, b, f, bd in [('हि · En', '#FFFFFF', MID, True), ('हिंदी', MID, '#FFFFFF', False), ('English', '#FFFFFF', INK, True), ('Hinglish', '#FFFFFF', INK, True), ('தமிழ்', '#FFFFFF', INK, True)])
nav = (ttl('Navigation and shell', 'Safed patli rail · 5 jagah · upar Arth, neeche bhasha · har screen par Arth dock') +
  '<div style="display: flex; gap: 56px"><div style="display: flex; gap: 20px">%s</div><div style="display: flex; flex-direction: column; gap: 28px">%s%s%s%s</div></div>') % (
  rails, sec('Arth dock · har screen ke hisaab se chips', docks), sec('Header · ek title, ek sub, right side mein max 2 actions', hdrs), sec('Bhasha switch', row(lp, 8, 'align-items: center')),
  arth_note('Mascot rail ke upar hamesha dikhta hai aur apni state se batata hai Arth kya kar raha hai. Tap karo to "Arth se poochho" khulta hai.'))
open(OUT + 'Navigation.dc.html', 'w').write(board('Arth navigation', nav, 1440, 980))

# ---------- DETAILS: customer, WhatsApp, agents, language ----------
cust_sel = ('<div style="width: 330px; padding: 10px 12px; border-radius: 18px; background: %s; display: flex; align-items: center; gap: 12px">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 700">Priya Verma</span><span style="font-size: 12.5px; color: %s">Reward 3/10 · khata saaf · हिंदी</span></div><span style="font-size: 13px; font-weight: 600; color: %s">Badlo</span></div>') % (SKY, avatar('PV', MID, '#FFFFFF', 40), INK3, CYT)
cust_empty = ('<div style="width: 330px; padding: 10px 12px; border-radius: 18px; box-shadow: inset 0 0 0 1.5px dashed; box-shadow: inset 0 0 0 1.5px #D9DEE5; display: flex; align-items: center; gap: 12px"><span style="width: 40px; height: 40px; border-radius: 999px; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</span><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 600">Customer jodo</span><span style="font-size: 12.5px; color: %s">Phone bolo ya QR se pehchano</span></div></div>') % (GROUND, MID, svg(I['plus'], 18, 2.2), INK3)
cust_new = ('<div style="width: 330px; padding: 10px 12px; border-radius: 18px; background: %s; display: flex; align-items: center; gap: 12px">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 700">Rohit Kumar</span><span style="font-size: 12.5px; color: %s">Naya · pehli baar · coupon ₹20</span></div>%s</div>') % (GRNT, avatar('RK', GRNF, '#FFFFFF', 40), INK3, chip('Naya', '#FFFFFF', GRN, 24, 11.5, 700, False))
wa_in = '<div style="width: 330px; border-radius: 18px; background: #EFEAE2; padding: 12px; display: flex; flex-direction: column">%s</div>' % wa_bubble('<b>गुप्ता जनरल स्टोर</b><br>बिल 1042 · ₹62 मिल गए<br><span style="color: %s">रिवॉर्ड 4/10</span>' % CYT, 'Receipt · sent by Arth', '9:13 am')
wa_out = '<div style="width: 330px; border-radius: 18px; background: #EFEAE2; padding: 12px; display: flex; flex-direction: column"><div style="align-self: flex-end; padding: 10px 12px 7px; border-radius: 16px 16px 4px 16px; background: #D9FDD3; font-size: 14px; line-height: 1.45">PO-118 में 4 तेल कम आए। ₹660 अगले बिल में कम कर दीजिए।<div style="text-align: right; font-size: 10.5px; color: %s">draft · aapki haan ke baad</div></div></div>' % INK3
sendbar = '<div style="width: 330px; display: flex; gap: 8px">%s%s</div>' % (btn(svg(I['send'], 18, 2) + 'WhatsApp pe bhejo', 'primary', 50, 15, 'flex: 1'), btn('Badlo', 'ghost', 50, 15))
agent = lambda n, role, s, c, t, tt: '<div style="width: 236px; box-sizing: border-box; %s padding: 14px 16px; display: flex; flex-direction: column; gap: 8px"><div style="display: flex; align-items: center; gap: 10px">%s<span style="font-size: 16px; font-weight: 700">%s</span><span style="margin-left: auto">%s</span></div><span style="font-size: 12.5px; color: %s">%s</span><span style="font-size: 14px; font-weight: 500">%s</span></div>' % (card('border-radius: 20px;'), dot(c, 10), n, tier(t, tt), INK3, role, s)
langrow = ''.join('<div style="height: 56px; padding: 0 16px; border-radius: 16px; display: flex; align-items: center; %s"><span style="font-size: 17px; font-weight: 600">%s</span></div>' % ('background: %s; box-shadow: inset 0 0 0 2px %s' % (SKY, CYAN) if on else 'box-shadow: inset 0 0 0 1px %s' % LINE, n) for n, on in [('हिंदी', True), ('English', False), ('தமிழ்', False), ('বাংলা', False)])
consent = '<div style="width: 360px; display: flex; flex-direction: column; border-radius: 16px; box-shadow: inset 0 0 0 1px %s">%s%s</div>' % (LINE,
  '<div style="display: flex; align-items: center; gap: 12px; padding: 12px 14px"><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 14.5px; font-weight: 600">Bill WhatsApp pe</span><span style="font-size: 12.5px; color: %s">Receipts only</span></div>%s</div>' % (INK3, toggle(True)),
  '<div style="display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-top: 1px solid %s"><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 14.5px; font-weight: 600">Offers bhi</span><span style="font-size: 12.5px; color: %s">Alag haan · hafte mein max 1</span></div>%s</div>' % (LINE, INK3, toggle(False)))
det = (ttl('Details that matter', 'Grahak chunna, naya grahak, WhatsApp bill aur claim, Arth ke helpers, bhasha') +
  '<div style="display: flex; gap: 40px">' +
   '<div style="display: flex; flex-direction: column; gap: 28px">' + sec('Bill par customer · 3 states', '<div style="display: flex; flex-direction: column; gap: 10px">' + cust_sel + cust_empty + cust_new + '</div>') + sec('Consent', consent) + '</div>' +
   '<div style="display: flex; flex-direction: column; gap: 28px">' + sec('WhatsApp · receipt aur claim', '<div style="display: flex; flex-direction: column; gap: 10px">' + wa_in + wa_out + sendbar + '</div>') + '</div>' +
   '<div style="display: flex; flex-direction: column; gap: 28px">' + sec('Arth ke helpers', '<div style="display: grid; grid-template-columns: repeat(2, 236px); gap: 12px">' +
      agent('Kharid', 'Supplier rates, PO, claims', '9 baje 2 suppliers se rate', CYAN, 'R2', 'haan chahiye') + agent('Hisaab', 'Raat ka reconciliation', '3 payments mile · ₹20 cash kam', GRNF, 'R0', 'khud') +
      agent('Stock', 'Kam stock, expiry, reorder', 'Dry fruits 40%', AMB, 'R2', 'haan chahiye') + agent('Pehredaar', 'Rules, limits, audit log', 'Sab theek · 0 blocked', GRNF, 'R0', 'hamesha') + '</div>') +
     sec('Bhasha chunna', '<div style="display: grid; grid-template-columns: repeat(2, 236px); gap: 10px">' + langrow + '</div>') +
     arth_note('Customer ki bhasha uske record mein rehti hai. Receipt, reminder aur offer usi bhasha mein jaate hain, screen aapki bhasha mein rehti hai.', 'width: 484px; box-sizing: border-box') + '</div>' +
  '</div>')
open(OUT + 'Details.dc.html', 'w').write(board('Arth details', det, 1440, 1000))
print('ok')
