from c2 import *
OUT = '/home/claude/design/project/'

# ---------- BILLING ----------
items = [('noodle', 'Maggi 70 g', '₹14'), ('biscuit', 'Parle-G', '₹10'), ('milk', 'Amul Taaza 500 ml', '₹28'), ('salt', 'Tata Salt 1 kg', '₹28'),
         ('atta', 'Atta 5 kg', '₹265'), ('sugar', 'Sugar, loose', '₹48/kg'), ('oil', 'Oil 1 L', '₹165'), ('tea', 'Tea 250 g', '₹140')]
tiles = ''.join('<button style="height: 124px; border: none; border-radius: 22px; background: #FFFFFF; box-shadow: %s; padding: 14px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; font-family: inherit; text-align: left; color: %s">%s<span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 14.5px; font-weight: 600">%s</span><span style="font-size: 13.5px; color: %s; font-variant-numeric: tabular-nums">%s</span></span></button>' % (SH, INK, pack(k, 42), n, INK2, p) for k, n, p in items)

def bl(kind, name, sub, qty, amt, voice=False, fresh=False):
    v = ' · <span style="color: %s; font-weight: 600">bola gaya</span>' % CYT if voice else ''
    return ('<div style="display: flex; align-items: center; gap: 12px; padding: 9px 20px; %s">%s<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0"><span style="font-size: 15px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s%s</span></div><span style="font-size: 14px; color: %s; font-variant-numeric: tabular-nums">%s</span><span style="width: 48px; text-align: right; font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums">%s</span></div>'
            % ('background: %s' % SKY if fresh else '', pack(kind, 36), name, INK3, sub, v, INK2, qty, amt))

bill_body = ('<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 16px; min-width: 0">'
  '<div style="display: flex; gap: 10px">'
    '<label style="flex-grow: 1; height: 52px; padding: 0 16px; border-radius: 16px; background: #FFFFFF; box-shadow: %s; display: flex; align-items: center; gap: 10px">%s<input aria-label="Add item" placeholder="Item ka naam ya barcode" style="flex-grow: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; color: %s"></label>'
    '<button style="height: 52px; padding: 0 18px; border-radius: 16px; border: none; background: %s; color: #FFFFFF; font-family: inherit; font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px">%sScan</button></div>'
  '<div style="display: flex; gap: 8px">%s%s%s%s</div>'
  '<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px">%s</div></div>'
 '<section style="width: 330px; flex-shrink: 0; %s display: flex; flex-direction: column; overflow: hidden">'
  '<a href="ScreenCustomer.dc.html" style="margin: 14px 14px 6px; padding: 10px 12px; border-radius: 18px; background: %s; display: flex; align-items: center; gap: 12px; text-decoration: none; color: %s">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 700">Priya Verma</span><span style="font-size: 12.5px; color: %s">Reward 3/10 · khata saaf · हिंदी</span></div><span style="font-size: 13px; font-weight: 600; color: %s">Badlo</span></a>'
  '%s%s%s'
  '<div style="margin: 10px 14px 0; display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 16px; box-shadow: inset 0 0 0 1.5px %s"><span style="font-size: 13.5px; flex-grow: 1"><b style="color: %s">Arth:</b> Priya har guruvaar doodh leti hain</span><button style="height: 36px; padding: 0 12px; border-radius: 10px; border: none; background: %s; color: %s; font-family: inherit; font-size: 13px; font-weight: 700; white-space: nowrap">+ ₹28</button></div>'
  '<div style="margin-top: auto; padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 10px">'
    '<div style="display: flex; align-items: baseline; justify-content: space-between"><span style="font-size: 14px; color: %s">3 items</span><span style="font-size: 36px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums">₹62</span></div>'
    '<div style="display: flex; gap: 6px">%s%s%s</div>'
    '<a href="ScreenPayment.dc.html" style="height: 56px; border-radius: 16px; background: %s; color: %s; font-size: 16px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 10px; text-decoration: none">%sQR dikhao · ₹62</a></div></section>') % (
  SH, svg(I['search'], 19, 1.9, INK3), INK, MID, svg(I['scan'], 20, 1.9),
  chip('Aksar', MID, '#FFFFFF', 34, 13.5, 600, False), chip('Doodh, dahi', '#FFFFFF', INK, 34, 13.5), chip('Atta, chawal', '#FFFFFF', INK, 34, 13.5), chip('Diwali', AMBTINT, AMBT, 34, 13.5, 600, False),
  tiles, card(), SKY, INK, avatar('PV', MID, '#FFFFFF', 40), INK3, CYT,
  bl('noodle', 'Maggi 2-Minute', '70 g · scanned', '×2', '₹28'), bl('sugar', 'Sugar, loose', '0.5 kg', '', '₹24', voice=True), bl('biscuit', 'Parle-G Gold', '100 g', '×1', '₹10', voice=True, fresh=True),
  CYAN, MID, SKY, MID, INK3,
  chip('UPI', SKY, MID, 36, 13.5, 700, False), chip('Cash', '#FFFFFF', INK, 36, 13.5), chip('Khata', '#FFFFFF', RED, 36, 13.5, 600),
  CYAN, MID, svg(I['qr'], 20, 2))
open(OUT + 'ScreenBilling.dc.html', 'w').write(screen('Arth billing', 'bill', 'Bill 1042', 'Scan karo, tap karo ya bolo', bill_body,
    right=btn('Bill rok do', 'text', 40, 14), mstate='listening',
    live=('<span style="opacity: 0.6">…aadha kilo cheeni</span> aur ek Parle-G Gold', svg(I['check'], 14, 2.6) + 'Parle-G Gold ×1 · ₹10')))

# ---------- CUSTOMER PICKER + NEW CUSTOMER ----------
recent = [('PV', 'Priya Verma', '98•••• 3321', 'Reward 3/10', MID, '#FFFFFF', True), ('RS', 'Rakesh Sharma', '98•••• 4410', 'Khata ₹1,600', '#FDECEF', RED, False),
          ('MF', 'Mehta family', '97•••• 0712', 'Khata ₹2,150', '#FFF1E6', '#B45309', False), ('IQ', 'Imran Qureshi', '99•••• 5108', 'Regular', SKY, MID, False)]
rlist = ''.join('<div style="display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 16px; %s">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div><span style="font-size: 12.5px; font-weight: 600; color: %s">%s</span></div>' % ('background: %s' % SKY if sel else '', avatar(i, bg, fg, 38), n, INK3, ph, RED if 'Khata' in t else INK2, t) for i, n, ph, t, bg, fg, sel in recent)
def field(label, value, ph=False):
    return '<label style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 13px; font-weight: 600; color: %s">%s</span><input value="%s" style="height: 48px; padding: 0 14px; border-radius: 14px; border: none; box-shadow: inset 0 0 0 1.5px #D9DEE5; font-family: inherit; font-size: 15px; color: %s; outline: none; background: #FFFFFF"></label>' % (INK2, label, value, INK)
sheet = ('<div style="position: absolute; inset: 0; background: rgba(0,46,110,0.32); display: flex; align-items: center; justify-content: center">'
 '<section role="dialog" aria-label="Customer chunein" style="width: 800px; height: 600px; border-radius: 28px; background: #FFFFFF; box-shadow: 0 30px 80px rgba(0,30,80,0.35); display: flex; overflow: hidden">'
  '<div style="width: 360px; padding: 24px 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px; box-shadow: inset -1px 0 0 %s">'
    '<h2 style="margin: 0; font-size: 20px; font-weight: 700">Customer chunein</h2>'
    '<label style="height: 48px; padding: 0 14px; border-radius: 14px; background: %s; display: flex; align-items: center; gap: 10px">%s<input aria-label="Search customer" placeholder="Naam, phone ya UPI" style="flex-grow: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px"></label>'
    '<span style="font-size: 12.5px; font-weight: 600; color: %s; padding: 4px 4px 0">Haal hi mein</span>%s'
    '<div style="margin-top: auto">%s</div></div>'
  '<div style="flex-grow: 1; padding: 24px 28px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px">'
    '<div style="display: flex; align-items: center; justify-content: space-between"><h2 style="margin: 0; font-size: 20px; font-weight: 700">Naya customer</h2><button aria-label="Close" style="width: 40px; height: 40px; border-radius: 12px; border: none; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</button></div>'
    '%s'
    '<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px">%s%s</div>'
    '<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 13px; font-weight: 600; color: %s">Bhasha · messages isi mein jayenge</span><div style="display: flex; gap: 8px">%s%s%s%s</div></div>'
    '<div style="display: flex; flex-direction: column; border-radius: 16px; box-shadow: inset 0 0 0 1px %s">'
      '<div style="display: flex; align-items: center; gap: 12px; padding: 12px 14px"><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 14.5px; font-weight: 600">Bill WhatsApp pe bhejein</span><span style="font-size: 12.5px; color: %s">Customer ne haan kaha · receipts only</span></div>%s</div>'
      '<div style="display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-top: 1px solid %s"><div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 14.5px; font-weight: 600">Offers bhi bhejein</span><span style="font-size: 12.5px; color: %s">Alag se poochhein · hafte mein 1 se zyada nahi</span></div>%s</div></div>'
    '<div style="margin-top: auto; display: flex; gap: 10px">%s%s</div></div>'
 '</section></div>') % (
  LINE, GROUND, svg(I['search'], 18, 1.9, INK3), INK3, rlist, btn('Walk-in, bina naam', 'ghost', 46, 14, 'width: 100%'),
  GROUND, INK2, svg(I['x'], 18, 2),
  arth_note('Ye number pehle UPI se ₹340 pay kar chuka hai. Payer naam <b>Rohit K.</b> mila. Sahi hai?'),
  field('Naam', 'Rohit Kumar'), field('Phone', '+91 98765 01234'),
  INK2, chip('हिंदी', MID, '#FFFFFF', 38, 15, 600, False), chip('English', '#FFFFFF', INK, 38, 14), chip('Hinglish', '#FFFFFF', INK, 38, 14), chip('தமிழ்', '#FFFFFF', INK, 38, 15),
  LINE, INK3, toggle(True), LINE, INK3, toggle(False),
  btn('Jodo aur bill mein lagao', 'primary', 52, 15, 'flex: 1'), btn('Coupon ₹20 bhi', 'tint', 52, 14))
open(OUT + 'ScreenCustomer.dc.html', 'w').write(screen('Arth choose customer', 'bill', 'Bill 1043', 'Customer chunein ya naya jodein', '', overlay=sheet, nodock=True))

# ---------- PAYMENT ----------
QR = open('/home/claude/design/gen/screens2.py').read().split('QR_SCRIPT = r"""')[1].split('"""')[0]
pay_body = ('<section style="flex: 1; %s display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px">'
  '<span style="font-size: 15px; color: %s">Scan karke pay karein</span><span style="font-size: 56px; font-weight: 800; letter-spacing: -0.035em; line-height: 1; font-variant-numeric: tabular-nums">₹62</span>'
  '<div style="padding: 14px; border-radius: 22px; box-shadow: inset 0 0 0 1px %s; position: relative"><div role="img" aria-label="UPI QR code for 62 rupees" style="display: grid; grid-template-columns: repeat(25, 9px); grid-auto-rows: 9px"><sc-for list="{{cells}}" as="c" hint-placeholder-count="625"><span style="width: 9px; height: 9px; background: {{c.color}}; border-radius: {{c.r}}"></span></sc-for></div>'
  '<span style="position: absolute; left: 50%%; top: 50%%; width: 46px; height: 46px; margin: -23px 0 0 -23px; border-radius: 13px; background: %s; border: 4px solid #FFFFFF; color: %s; font-size: 16px; font-weight: 800; display: flex; align-items: center; justify-content: center; box-sizing: border-box">A</span></div>'
  '<span style="font-size: 13.5px; color: %s">gupta.general@upi · customer display par bhi</span></section>'
 '<div style="width: 330px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px">'
  '<section style="%s padding: 20px; display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center">%s<span style="font-size: 18px; font-weight: 700">Payment ka intezaar</span><span style="font-size: 13.5px; color: %s">Paisa aate hi bill band, receipt Priya ko</span><span style="margin-top: 6px; font-size: 26px; font-weight: 800; color: %s; font-variant-numeric: tabular-nums">0:18</span></section>'
  '<div style="margin-top: auto; display: flex; flex-direction: column; gap: 10px">%s%s</div></div>') % (
  card(), INK2, LINE, CYAN, MID, INK3, card(), mascot('thinking', 100), INK3, CYT,
  btn('Cash mein lo', 'ghost', 50, 15, 'width: 100%'), btn('Khate mein daalo', 'danger', 50, 15, 'width: 100%'))
open(OUT + 'ScreenPayment.dc.html', 'w').write(screen('Arth payment QR', 'bill', 'Bill 1042 · Priya Verma', 'QR ki validity 4:42', pay_body, chips=['Cash mein lo', 'Bill badlo'], script=QR, mstate='thinking'))

# ---------- PAID + WHATSAPP BILL ----------
paid_body = ('<section style="flex: 1; border-radius: 28px; background: %s; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px">%s'
  '<span style="font-size: 16px; font-weight: 600; color: %s">Mil gaye · UPI · 9:13 am</span><span style="font-size: 68px; font-weight: 800; letter-spacing: -0.04em; color: %s; line-height: 1.05; font-variant-numeric: tabular-nums">₹62</span>'
  '<span style="font-size: 14px; color: %s">Priya Verma · reward 4/10 · UTR ••4821</span>'
  '<div style="display: flex; gap: 10px; margin-top: 18px">%s%s</div></section>'
 '<section style="width: 340px; flex-shrink: 0; %s padding: 18px; display: flex; flex-direction: column; gap: 12px">'
  '<div style="display: flex; align-items: center; justify-content: space-between"><h2 style="margin: 0; font-size: 16px; font-weight: 700">WhatsApp bill</h2>%s</div>'
  '<div style="border-radius: 18px; background: #EFEAE2; padding: 14px 12px; display: flex; flex-direction: column; gap: 8px; flex-grow: 1">%s</div>'
  '<div style="display: flex; align-items: center; justify-content: space-between; font-size: 13.5px"><span style="color: %s">Bhasha: <b style="color: %s">हिंदी</b> · Priya ki pasand</span><a href="#" style="font-weight: 600; text-decoration: none">Badlo</a></div>'
  '<div style="display: flex; gap: 8px">%s%s</div></section>') % (
  GRNT, mascot('success', 150), GRN, GRN, INK2, btn('Naya bill', 'dark', 50, 15), btn('Print', 'ghost', 50, 15),
  card(), chip(svg(I['check'], 14, 2.6) + 'Bheja gaya', GRNT, GRN, 28, 12.5, 700, False),
  wa_bubble('<b>गुप्ता जनरल स्टोर</b><br>बिल 1042 · ₹62 मिल गए<br>मैगी ×2 · ₹28<br>चीनी 0.5 kg · ₹24<br>पारले-जी ×1 · ₹10<br><span style="color: %s">रिवॉर्ड 4/10 · 10 पर एक चाय मुफ़्त</span>' % CYT, 'Receipt · sent by Arth', '9:13 am'),
  INK3, INK, btn('PDF', 'tint', 44, 14, 'flex: 1'), btn('SMS bhi', 'ghost', 44, 14, 'flex: 1'))
open(OUT + 'ScreenPaid.dc.html', 'w').write(screen('Arth paid and receipt', 'bill', 'Bill 1042 band', 'Thu 29 Oct · 9:13 am', paid_body, chips=['Naya bill', 'Aaj kitna aaya?'], mstate='success'))
print('ok')
