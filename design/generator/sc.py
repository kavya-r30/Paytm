from c2 import *
from sb import W, h2, tier
OUT = '/home/claude/design/project/'

# ---------- FORECAST ----------
past = [6.9, 9.1, 10.4, 6.2, 7.3, 8.45]
fut = [(8.2, 9.4, 10.8), (8.8, 10.2, 11.8), (10.5, 12.4, 14.6), (12.0, 14.5, 17.5), (11.0, 13.6, 16.5), (13.0, 16.5, 20.5)]
labels = ['Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Aaj', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue']
X = lambda i: 30 + i * 46; Y = lambda v: 210 - v * 9
band_top = ' '.join('%d,%.1f' % (X(7 + i - 1), Y(h)) for i, (l, m, h) in enumerate(fut, 0) if False)
pts_hi = [(X(6 + i), Y(h)) for i, (l, m, h) in enumerate(fut)]
pts_lo = [(X(6 + i), Y(l)) for i, (l, m, h) in enumerate(fut)]
band = 'M%d,%.1f ' % (X(5), Y(past[-1])) + ' '.join('L%d,%.1f' % p for p in pts_hi) + ' ' + ' '.join('L%d,%.1f' % p for p in reversed(pts_lo)) + ' Z'
pline = ' '.join('%s%d,%.1f' % ('M' if i == 0 else 'L', X(i), Y(v)) for i, v in enumerate(past))
mline = 'M%d,%.1f ' % (X(5), Y(past[-1])) + ' '.join('L%d,%.1f' % (X(6 + i), Y(m)) for i, (l, m, h) in enumerate(fut))
lab = ''.join('<text x="%d" y="232" text-anchor="middle" font-size="12" fill="%s" font-weight="%s">%s</text>' % (X(i), MID if t == 'Aaj' else INK3, 700 if t == 'Aaj' else 400, t) for i, t in enumerate(labels))
grid = ''.join('<line x1="20" x2="560" y1="%.1f" y2="%.1f" stroke="%s"/><text x="0" y="%.1f" font-size="11" fill="%s">%dk</text>' % (Y(v), Y(v), LINE, Y(v) + 4, INK3, v) for v in (5, 10, 15, 20))
fc_chart = ('<svg viewBox="0 0 570 240" width="100%%" height="300" style="margin-top: auto" role="img" aria-label="Pichhle 7 din ki bikri aur agle 6 din ka andaaza, Diwali ki taraf badhta hua">%s'
  '<rect x="%d" y="0" width="%d" height="214" fill="%s" opacity="0.6"/><path d="%s" fill="#9BE3F9" opacity="0.45"/><path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
  '<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 6" stroke-linecap="round"/><circle cx="%d" cy="%.1f" r="6" fill="%s" stroke="#FFFFFF" stroke-width="3"/>%s</svg>') % (
  grid, X(6), X(11) - X(6) + 20, SKY, band, pline, MID, mline, CYT, X(6), Y(9.4), CYAN, lab)
why = [('Diwali 4 din door', 'pichhle saal isi hafte +38%'), ('Guruvaar', 'aapke guruvaar aam taur par Wed jaise'), ('Mausam saaf', 'koi asar nahi')]
wy = ''.join('<div style="display: flex; flex-direction: column; gap: 1px; padding: 10px 0; %s"><span style="font-size: 14.5px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div>' % ('' if i == 0 else 'border-top: 1px solid %s' % LINE, a, INK3, b) for i, (a, b) in enumerate(why))
fc_body = ('<section style="flex-grow: 1; %s padding: 20px 22px; display: flex; flex-direction: column; gap: 10px; min-width: 0">'
  '<div style="display: flex; align-items: flex-start; gap: 16px"><div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13.5px; color: %s">Aaj ki bikri, sabse sambhav</span><span style="font-size: 36px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums">₹9,400</span>'
  '<span style="font-size: 14px; color: %s; font-variant-numeric: tabular-nums">10 mein se 8 baar ₹8,200–10,800 ke beech</span></div><div style="margin-left: auto; display: flex; gap: 6px">%s%s</div></div>%s'
  '<div style="display: flex; gap: 16px; font-size: 12.5px; color: %s"><span style="display: flex; align-items: center; gap: 6px"><span style="width: 18px; height: 3px; background: %s; border-radius: 2px"></span>Asli bikri</span><span style="display: flex; align-items: center; gap: 6px"><span style="width: 18px; height: 10px; background: #9BE3F9; opacity: 0.6; border-radius: 3px"></span>Andaaze ki range</span></div></section>'
 '<section style="width: 270px; flex-shrink: 0; %s padding: 20px; display: flex; flex-direction: column; gap: 4px">%s%s'
  '<div style="margin-top: auto; display: flex; flex-direction: column; gap: 10px">%s%s</div></section>') % (
  card(), INK3, INK2, chip('Bikri', MID, '#FFFFFF', 32, 13, 600, False), chip('Items', '#FFFFFF', INK, 32, 13), fc_chart, INK3, MID,
  card(), h2('Arth: kyun?'), wy, arth_note('Pichhle 14 din mera andaaza 12 baar range ke andar tha. Diwali tak bikri lagbhag doguni.', 'padding: 12px 14px'), btn('Diwali stock plan', 'primary', 48, 15, 'width: 100%'))
W('ScreenForecast', screen('Arth forecast', 'grid', 'Andaaza', 'Aaj aur agle 5 din · range ke saath, pakka number nahi', fc_body, chips=['Diwali pe kya bikega?', 'Kal ke liye kitna doodh?'], mstate='thinking'))

# ---------- KHATA ----------
dues = [('MF', 'Mehta family', '₹2,150', '21 din', '#FFF1E6', '#B45309', True), ('RS', 'Rakesh Sharma', '₹1,600', '9 din', REDT, RED, False),
        ('SK', 'Sunita Kaur', '₹840', '4 din', SKY, MID, False), ('AD', 'Anil Dubey', '₹420', '2 din', GROUND, INK2, False)]
dl = ''.join('<div style="display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 16px; %s">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 15px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s purana</span></div><span style="font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums">%s</span></div>' % ('background: %s' % SKY if s else '', avatar(i, bg, fg, 40), n, INK3, d, a) for i, n, a, d, bg, fg, s in dues)
hist = [('17 Oct', 'Doodh, atta, tel', '+ ₹1,240'), ('22 Oct', 'Diwali saman', '+ ₹1,410'), ('25 Oct', 'UPI se diya', '− ₹500')]
hl = ''.join('<div style="display: flex; justify-content: space-between; font-size: 13.5px; padding: 6px 0"><span style="color: %s">%s · %s</span><b style="color: %s; font-variant-numeric: tabular-nums">%s</b></div>' % (INK3, a, b, GRN if c.startswith('−') else INK, c) for a, b, c in hist)
kh_body = ('<section style="width: 340px; flex-shrink: 0; %s padding: 16px 12px; display: flex; flex-direction: column; gap: 4px">'
  '<div style="padding: 4px 12px 10px; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13.5px; color: %s">Kul baaki · 4 grahak</span><span style="font-size: 30px; font-weight: 800; letter-spacing: -0.03em">₹5,010</span></div>%s'
  '<div style="margin-top: auto; padding: 0 4px">%s</div></section>'
 '<section style="flex-grow: 1; %s padding: 20px 22px; display: flex; flex-direction: column; gap: 14px; min-width: 0">'
  '<div style="display: flex; align-items: center; gap: 12px">%s<div style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 18px; font-weight: 700">Mehta family</span><span style="font-size: 12.5px; color: %s">Limit ₹3,000 · har mahine 1 tareekh ko chukate hain</span></div><span style="font-size: 24px; font-weight: 800">₹2,150</span></div>'
  '%s'
  '<div style="border-radius: 18px; background: #EFEAE2; padding: 12px; display: flex; flex-direction: column">%s</div>'
  '<div style="margin-top: auto; display: flex; gap: 10px">%s%s</div></section>') % (
  card(), INK3, dl, btn('+ Naya udhaar likho', 'ghost', 46, 14, 'width: 100%'),
  card(), avatar('MF', '#FFF1E6', '#B45309', 48), INK3, hl,
  wa_bubble('नमस्ते मेहता जी 🙏 गुप्ता जनरल स्टोर में आपका ₹2,150 बाक़ी है। सुविधा हो तो इस लिंक से UPI कर दीजिए।<br><span style="color: %s; font-weight: 600">paytm.me/gupta-general · ₹2,150</span>' % CYT, 'Reminder · Arth draft · हिंदी', 'kal 9:00 am'),
  btn(svg(I['send'], 18, 2) + 'WhatsApp reminder bhejo', 'primary', 52, 15, 'flex: 1'), btn('Paisa mila', 'ghost', 52, 15))
W('ScreenKhata', screen('Arth khata', 'khata', 'Khata', 'Udhaar ka hisaab · reminders grahak ki bhasha mein', kh_body, chips=['Sharma ji ka hisaab', 'Kis se kitna lena hai?'], mstate='idle'))

# ---------- INVENTORY ----------
stock = [('nuts', 'Kaju 1 kg', 4, 10, 'Diwali: 3× bikega', RED), ('diya', 'Diye pack', 6, 20, 'Diwali', RED), ('milk', 'Amul Taaza 500 ml', 18, 40, 'Kal subah aayega', AMB),
         ('noodle', 'Maggi 70 g', 46, 60, '', GRNF), ('atta', 'Atta 5 kg', 12, 15, '', GRNF), ('oil', 'Oil 1 L', 20, 24, '4 kam aaye · claim', AMB)]
sl = ''.join('<div style="display: flex; align-items: center; gap: 14px; padding: 11px 0; %s">%s<div style="display: flex; flex-direction: column; gap: 2px; width: 190px"><span style="font-size: 15px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div>'
             '<div style="flex-grow: 1; height: 8px; border-radius: 999px; background: %s; overflow: hidden"><div style="width: %d%%; height: 100%%; border-radius: 999px; background: %s"></div></div><span style="width: 64px; text-align: right; font-size: 14px; font-variant-numeric: tabular-nums"><b>%d</b> / %d</span></div>'
             % ('' if i == 0 else 'border-top: 1px solid %s' % LINE, pack(k, 38), n, INK3, note or 'Theek hai', '#EEF1F5', round(100 * a / b), c, a, b) for i, (k, n, a, b, note, c) in enumerate(stock))
inv_body = ('<section style="flex-grow: 1; %s padding: 14px 22px; display: flex; flex-direction: column; min-width: 0">%s</section>'
 '<div style="width: 280px; flex-shrink: 0; display: flex; flex-direction: column; gap: 14px">'
  '<section style="%s padding: 20px; display: flex; flex-direction: column; gap: 12px">%s<p style="margin: 0; font-size: 15px; line-height: 1.5">Diwali ke liye <b>kaju, badam, diye aur soan papdi</b> kam hain. Maine Balaji aur Agarwal se rate maange hain.</p>%s%s</section>'
  '<a href="ScreenClaim.dc.html" style="%s padding: 16px 18px; display: flex; align-items: center; gap: 12px; text-decoration: none; color: %s"><span style="width: 36px; height: 36px; border-radius: 12px; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</span><span style="display: flex; flex-direction: column; flex-grow: 1"><span style="font-size: 14.5px; font-weight: 600">Agarwal se 4 oil kam</span><span style="font-size: 12.5px; color: %s">Claim ₹660 draft ready</span></span>%s</a></div>') % (
  card(), sl, card('box-shadow: %s, inset 0 0 0 1.5px %s;' % (SH, CYAN)), h2('Arth ka sujhaav', mascot('idle', 34)),
  btn('Rates dekho', 'primary', 48, 15, 'width: 100%'), btn('Order khud banao', 'ghost', 44, 14, 'width: 100%'),
  card(), INK, AMBTINT, AMBT, svg(I['alert'], 18, 2), INK3, svg(I['chevron'], 18, 2, INK3))
W('ScreenInventory', screen('Arth stock', 'box', 'Stock', '312 items · 6 par dhyan dena hai', inv_body, right=btn(svg(I['scan'], 18, 2) + 'Maal aaya', 'dark', 42, 14), chips=['Kya khatam hone wala hai?', 'Expiry is hafte'], mstate='idle'))

# ---------- OFFERS ----------
def offer(title, rule, stat, on):
    return ('<div style="padding: 16px 18px; border-radius: 20px; background: #FFFFFF; box-shadow: inset 0 0 0 1px %s; display: flex; align-items: center; gap: 14px">'
            '<span style="width: 40px; height: 40px; border-radius: 12px; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</span>'
            '<div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1"><span style="font-size: 15.5px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div><span style="font-size: 13px; font-weight: 600; color: %s; margin-right: 6px">%s</span>%s</div>') % (
            LINE, SKY, MID, svg(I['gift'], 20, 1.9), title, INK3, rule, GRN, stat, toggle(on))
of_body = ('<section style="flex-grow: 1; %s padding: 20px 22px; display: flex; flex-direction: column; gap: 12px; min-width: 0">%s%s%s%s</section>'
 '<section style="width: 300px; flex-shrink: 0; %s padding: 20px; display: flex; flex-direction: column; gap: 12px">%s'
  '<span style="font-size: 18px; font-weight: 700; line-height: 1.35">Pehli baar aane walon ko agli khareed par ₹20 off</span>'
  '<span style="font-size: 13.5px; color: %s; line-height: 1.5">Is mahine 38 naye grahak aaye, sirf 9 dobara aaye.</span>'
  '<div style="display: flex; flex-direction: column; gap: 6px; padding: 12px 14px; border-radius: 16px; background: %s"><span style="font-size: 12.5px; color: %s">Andaaza · 30 din</span><span style="font-size: 18px; font-weight: 800">+6 to +11 grahak lautenge</span><span style="font-size: 12.5px; color: %s">Kharcha ₹200–400 · 1 mein se 5 ko nahi bhejenge, taaki asli asar naap sakein</span></div>'
  '<div style="margin-top: auto; display: flex; flex-direction: column; gap: 8px">%s%s</div></section>') % (
  card(), h2('Chal rahe offers'),
  offer('Chai reward · 10 pe 1 free', 'Har UPI bill par 1 stamp', '64 grahak', True),
  offer('Diwali combo · ₹20 off', '₹500 se upar · 5 Nov tak', '12 baar', True),
  offer('Purane grahak wapas', '30 din se nahi aaye · WhatsApp', 'Rukha hua', False),
  card('box-shadow: %s, inset 0 0 0 1.5px %s;' % (SH, CYAN)), h2('Arth ka naya idea', mascot('idle', 34)), INK2, SKY, CYT, INK3,
  btn('Shuru karo', 'primary', 50, 15, 'width: 100%'), btn('Message dekho', 'ghost', 44, 14, 'width: 100%'))
W('ScreenOffers', screen('Arth offers', 'grid', 'Offers aur coupons', 'Sirf unhe jinhone offers ke liye haan kaha', of_body, chips=['Naya coupon banao', 'Kaunsa offer chala?'], mstate='idle'))

# ---------- MENU ----------
tiles = [('trend', 'Andaaza', 'Kal aur Diwali', 'ScreenForecast'), ('gift', 'Offers', '2 chal rahe', 'ScreenOffers'), ('users', 'Arth ki team', '3 haan baaki', 'ScreenTeam'),
         ('chat', 'Arth se poochho', 'Chat aur reports', 'ScreenAsk'), ('truck', 'Suppliers', 'Rates, PO, claims', 'ScreenApproval'), ('wallet', 'Hisaab', 'Raat ka reconciliation', 'ScreenHome'),
         ('speaker', 'Soundbox', 'Juda hua · 82%', 'ScreenMenu'), ('settings', 'Bhasha', 'हिंदी · Hinglish', 'ScreenLanguage'), ('lock', 'Permissions', 'R0–R4 limits', 'ScreenTeam')]
mt = ''.join('<a href="%s.dc.html" style="%s padding: 18px; display: flex; flex-direction: column; gap: 14px; text-decoration: none; color: %s"><span style="width: 44px; height: 44px; border-radius: 14px; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</span><span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 16px; font-weight: 700">%s</span><span style="font-size: 13px; color: %s">%s</span></span></a>'
             % (h, card('border-radius: 22px;'), INK, SKY, MID, svg(I[ic], 22, 1.9), t, INK3, s) for ic, t, s, h in tiles)
mn_body = '<div style="flex-grow: 1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: min-content; gap: 14px">%s</div>' % mt
W('ScreenMenu', screen('Arth more', 'grid', 'Aur', 'Gupta General Store · Ramesh ji', mn_body, chips=['Soundbox ki awaaz badhao', 'Backup kab hua?']))
print('ok')
