from c2 import *
OUT = '/home/claude/design/project/'

def sales_chart(T):
    # cumulative sales by hour, 8am..10pm; now = 2:10pm
    hrs = list(range(8, 23))
    X = lambda h: 34 + (h - 8) * 27.4
    Y = lambda v: 150 - v * 13.2   # v in thousands
    actual = [(8, 0), (9, 0.42), (10, 1.05), (11, 2.45), (12, 2.95), (13, 3.55), (14, 4.0), (14.17, 4.18)]
    typical = [(8, 0), (9, 0.35), (10, 0.9), (11, 1.4), (12, 1.95), (13, 2.6), (14, 3.6), (16, 4.6), (18, 6.0), (20, 7.9), (22, 8.6)]
    med = [(14.17, 4.18), (16, 5.2), (18, 6.9), (20, 8.8), (22, 9.4)]
    hi = [(14.17, 4.18), (16, 5.6), (18, 7.6), (20, 9.9), (22, 10.8)]
    lo = [(14.17, 4.18), (16, 4.8), (18, 6.2), (20, 7.7), (22, 8.2)]
    P = lambda pts: ' '.join('%s%.1f,%.1f' % ('M' if i == 0 else 'L', X(h), Y(v)) for i, (h, v) in enumerate(pts))
    band = P(hi) + ' ' + ' '.join('L%.1f,%.1f' % (X(h), Y(v)) for h, v in reversed(lo)) + ' Z'
    area = P(actual) + ' L%.1f,%.1f L%.1f,%.1f Z' % (X(14.17), Y(0), X(8), Y(0))
    grid = ''.join('<line x1="34" x2="420" y1="%.1f" y2="%.1f" stroke="%s"/><text x="0" y="%.1f" font-size="10.5" fill="%s">%s</text>' % (Y(v), Y(v), LINE, Y(v) + 4, INK3, '₹%dk' % v if v else '0') for v in (0, 5, 10))
    xl = ''.join('<text x="%.1f" y="168" text-anchor="middle" font-size="10.5" fill="%s">%s</text>' % (X(h), INK3, t) for h, t in [(8, '8am'), (11, '11'), (14, '2pm'), (17, '5'), (20, '8'), (22, '10pm')])
    ax, ay = X(11), Y(2.45)
    return ('<svg viewBox="0 0 434 172" width="100%%" height="172" role="img" aria-label="%s">'
      '<defs><linearGradient id="hArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00BAF2" stop-opacity="0.32"/><stop offset="1" stop-color="#00BAF2" stop-opacity="0"/></linearGradient></defs>%s'
      '<path d="%s" fill="#9BE3F9" opacity="0.38"/><path d="%s" fill="none" stroke="#98A2B3" stroke-width="1.6" stroke-dasharray="3 4"/>'
      '<path d="%s" fill="url(#hArea)"/><path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 5" stroke-linecap="round"/>'
      '<line x1="%.1f" x2="%.1f" y1="18" y2="150" stroke="%s" stroke-width="1"/>'
      '<circle cx="%.1f" cy="%.1f" r="5.5" fill="%s" stroke="#FFFFFF" stroke-width="3"/>'
      '<circle cx="%.1f" cy="%.1f" r="4" fill="#FFFFFF" stroke="%s" stroke-width="2.4"/>'
      '<text x="%.1f" y="%.1f" text-anchor="end" font-size="11.5" font-weight="700" fill="%s">₹9,400</text>%s</svg>') % (
      T('Aaj ki bikri ghante ke hisaab se, aam guruvaar se aage, raat tak ₹9,400 ka andaaza', 'आज की बिक्री, आम गुरुवार से आगे, रात तक ₹9,400 का अनुमान'),
      grid, band, P(typical), area, P(actual), MID, P(med), CYT, X(14.17), X(14.17), '#C9D1DB', X(14.17), Y(4.18), CYAN, ax, ay, AMB, X(22) - 2, Y(9.4) - 10, CYT, xl), (ax, ay)

def donut(parts, size=60, sw=10):
    import math
    r = (size - sw) / 2; c = 2 * math.pi * r; off = 0; out = ''
    for frac, col in parts:
        out += '<circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" stroke-width="%d" stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f" transform="rotate(-90 %g %g)"/>' % (size / 2, size / 2, r, col, sw, c * frac - 2, c - c * frac + 2, -off, size / 2, size / 2)
        off += c * frac
    return '<svg width="%d" height="%d" viewBox="0 0 %d %d" aria-hidden="true">%s</svg>' % (size, size, size, size, out)

def spark(vals, w=120, h=34, col=CYAN, bars=False, hl=None):
    mx = max(vals); mn = 0 if bars else min(vals)
    if bars:
        bw = w / len(vals)
        return '<svg width="%d" height="%d" aria-hidden="true">%s</svg>' % (w, h, ''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/>' % (i * bw + 2, h - h * v / mx, bw - 5, h * v / mx, col if i == (hl if hl is not None else len(vals) - 1) else '#D5EEF8') for i, v in enumerate(vals)))
    pts = ' '.join('%.1f,%.1f' % (i * (w - 6) / (len(vals) - 1) + 3, h - 4 - (h - 8) * (v - mn) / (mx - mn)) for i, v in enumerate(vals))
    lx, ly = pts.split(' ')[-1].split(',')
    return '<svg width="%d" height="%d" aria-hidden="true"><polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="%s" cy="%s" r="3.5" fill="%s"/></svg>' % (w, h, pts, col, lx, ly, col)

def home(hi):
    T = (lambda en, h: h if hi else en)
    chart, (ax, ay) = sales_chart(T)
    rows = [(T('Mehta ji ko yaad dilana', 'मेहता जी को याद दिलाना'), T('₹2,150 · kal 9 baje', '₹2,150 · कल 9 बजे'), 'chat'),
            (T('Diwali stock mangwana', 'दिवाली का स्टॉक मँगवाना'), T('Balaji · ₹18,400 · ₹850 sasta', 'बालाजी · ₹18,400 · ₹850 सस्ता'), 'truck'),
            (T('5 purane grahak bulana', '5 पुराने ग्राहक बुलाना'), T('4 ko message, 1 naap ke liye', '4 को मैसेज, 1 नापने के लिए'), 'users')]
    rhtml = ''.join('<div style="display: flex; align-items: center; gap: 12px; padding: 11px 0; %s"><span style="width: 34px; height: 34px; border-radius: 11px; background: %s; color: %s; display: flex; align-items: center; justify-content: center; flex-shrink: 0">%s</span><div style="display: flex; flex-direction: column; gap: 1px; flex-grow: 1; min-width: 0"><span style="font-size: 14.5px; font-weight: 600">%s</span><span style="font-size: 12.5px; color: %s">%s</span></div>%s</div>'
                    % ('' if i == 0 else 'border-top: 1px solid %s' % LINE, GROUND, MID, svg(I[ic], 17, 1.9), a, INK3, b, svg(I['check'], 17, 2.4, CYAN)) for i, (a, b, ic) in enumerate(rows))
    brief = ('<section style="height: 128px; flex-shrink: 0; border-radius: 24px; background: linear-gradient(100deg, #E8F8FE 0%%, #F4FBFF 55%%, #FFFFFF 100%%); box-shadow: %s, inset 0 0 0 1px #D3F1FC; padding: 16px 20px 16px 14px; box-sizing: border-box; display: flex; gap: 14px; align-items: center">'
      '%s<div style="display: flex; flex-direction: column; gap: 10px; min-width: 0; flex-grow: 1">'
      '<p style="margin: 0; font-size: 17.5px; line-height: 1.45; font-weight: 500; letter-spacing: -0.01em">%s</p>'
      '<div style="display: flex; align-items: center; gap: 10px">'
        '<button style="height: 34px; padding: 0 12px 0 6px; border-radius: 999px; border: none; background: %s; color: #FFFFFF; font-family: inherit; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px"><span style="width: 24px; height: 24px; border-radius: 999px; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</span>%s</button>'
        '%s<span style="font-size: 12.5px; color: %s; font-variant-numeric: tabular-nums">0:06 / 0:14</span>'
        '<span style="margin-left: auto; display: flex; gap: 6px">%s%s</span></div></div></section>') % (
      SH, mascot('speaking', 64),
      T('Dopahar tak <b style="font-weight: 700">₹4,180</b>, aam guruvaar se <b style="color: %s; font-weight: 700">13%% aage</b>. Shaam 6–8 sabse zyada bheed hogi, doodh aur Maggi pehle se aage rakh lijiye.' % GRN,
        'दोपहर तक <b style="font-weight: 700">₹4,180</b>, आम गुरुवार से <b style="color: %s; font-weight: 700">13%% आगे</b>। शाम 6–8 सबसे ज़्यादा भीड़ होगी, दूध और मैगी पहले से आगे रख लीजिए।' % GRN),
      MID, CYAN, MID, svg(I['speaker'], 13, 2.2), T('Arth bol raha hai', 'अर्थ बोल रहा है'), wave(22, 20), INK3,
      chip(T('Aage kyun hain?', 'आगे क्यों हैं?'), '#FFFFFF', MID, 30, 12.5, 600), chip(T('Shaam ki taiyari', 'शाम की तैयारी'), '#FFFFFF', MID, 30, 12.5, 600))
    note_left = 0
    chart_card = ('<section style="height: 280px; %s padding: 16px 18px 10px; box-sizing: border-box; display: flex; flex-direction: column; gap: 4px; position: relative">'
      '<div style="display: flex; align-items: flex-start; gap: 10px"><div style="display: flex; flex-direction: column; gap: 1px"><span style="font-size: 13px; color: %s">%s</span>'
      '<div style="display: flex; align-items: baseline; gap: 10px"><span style="font-size: 30px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums">₹4,180</span>%s</div></div>'
      '<div style="margin-left: auto; display: flex; flex-direction: column; gap: 4px; font-size: 11.5px; color: %s; padding-top: 4px">'
        '<span style="display: flex; align-items: center; gap: 6px"><span style="width: 14px; height: 3px; border-radius: 2px; background: %s"></span>%s</span>'
        '<span style="display: flex; align-items: center; gap: 6px"><span style="width: 14px; height: 0; border-top: 2px dashed #98A2B3"></span>%s</span>'
        '<span style="display: flex; align-items: center; gap: 6px"><span style="width: 14px; height: 8px; border-radius: 2px; background: #9BE3F9"></span>%s</span></div></div>'
      '%s'
      '<div style="position: absolute; left: calc(64px + %.1f%%); top: 92px; padding: 6px 10px 6px 6px; border-radius: 12px; background: #FFFFFF; box-shadow: %s, inset 3px 0 0 #F5A524; display: flex; align-items: center; gap: 8px; font-size: 12px; line-height: 1.3; max-width: 200px">%s<span><b>11:20 · ₹1,240</b> %s</span></div></section>') % (
      card(), INK3, T('Aaj ki bikri · abhi tak', 'आज की बिक्री · अभी तक'), chip('▲ 13%', GRNT, GRN, 26, 12.5, 700, False), INK3,
      MID, T('Aaj', 'आज'), T('Aam guruvaar', 'आम गुरुवार'), T('Andaaza', 'अनुमान'), chart, note_left, SH2, orb(22),
      T('Mehta ji ka Diwali order. Isliye aage hain.', 'मेहता जी का दिवाली ऑर्डर। इसलिए आगे हैं।'))
    tile = lambda inner: '<div style="flex: 1; min-width: 0; height: 112px; %s padding: 14px 16px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between">%s</div>' % (card('border-radius: 20px;'), inner)
    t1 = tile('<span style="font-size: 12.5px; color: %s">%s</span><div style="display: flex; align-items: center; gap: 12px">%s<div style="display: flex; flex-direction: column; gap: 2px; font-size: 11.5px; white-space: nowrap; color: %s">'
              '<span style="display: flex; align-items: center; gap: 6px">%s<b style="color: %s">UPI 78%%</b></span><span style="display: flex; align-items: center; gap: 6px">%s%s 16%%</span><span style="display: flex; align-items: center; gap: 6px">%s%s 6%%</span></div></div>' % (
              INK3, T('Paisa kaise aaya', 'पैसा कैसे आया'), donut([(0.78, CYAN), (0.16, MID), (0.06, '#F04438')], 48, 8), INK2, dot(CYAN), INK, dot(MID), T('Cash', 'कैश'), dot('#F04438'), T('Khata', 'खाता')))
    t2 = tile('<div style="display: flex; justify-content: space-between; align-items: baseline"><span style="font-size: 12.5px; color: %s">%s</span>%s</div><div style="display: flex; align-items: flex-end; justify-content: space-between; gap: 8px"><span style="font-size: 24px; font-weight: 800; letter-spacing: -0.02em">38</span>%s</div>' % (
              INK3, T('Grahak', 'ग्राहक'), '<span style="font-size: 11.5px; font-weight: 700; color: %s; white-space: nowrap">+6 %s</span>' % (CYT, T('naye', 'नए')), spark([31, 44, 52, 29, 33, 41, 38], 92, 36, CYAN, True)))
    t3 = tile('<div style="display: flex; justify-content: space-between; align-items: baseline"><span style="font-size: 12.5px; color: %s">%s</span><span style="font-size: 11.5px; font-weight: 700; color: %s">−₹500</span></div><div style="display: flex; align-items: flex-end; justify-content: space-between; gap: 8px"><span style="font-size: 22px; font-weight: 800; letter-spacing: -0.02em">₹5,010</span>%s</div>' % (
              INK3, T('Khata baaki', 'खाता बाक़ी'), GRN, spark([6.2, 6.0, 5.9, 5.6, 5.5, 5.2, 5.01], 52, 30, GRNF)))
    decision = ('<section style="flex: 1; %s padding: 18px 20px; display: flex; flex-direction: column">'
      '<div style="display: flex; align-items: center; gap: 10px">%s<h2 style="margin: 0; font-size: 16px; font-weight: 700; flex-grow: 1; white-space: nowrap">%s</h2>%s</div>'
      '<span style="font-size: 12.5px; color: %s; margin: 6px 0 4px">%s</span>%s'
      '<div style="margin-top: auto; display: flex; flex-direction: column; gap: 8px">%s%s</div></section>') % (
      card('box-shadow: %s, inset 0 0 0 1.5px %s;' % (SH, AMB)), orb(26), T('Aapka ek haan, teen kaam', 'आपकी एक हाँ, तीन काम'), '',
      INK3, T('Arth ne taiyar kiya · Pehredaar ne check kiya', 'अर्थ ने तैयार किया · पहरेदार ने जाँचा'), rhtml,
      btn(T('Teeno haan', 'तीनों हाँ'), 'primary', 52, 16, 'width: 100%'), btn(T('Ek-ek karke dekho', 'एक-एक करके देखिए'), 'ghost', 46, 14.5, 'width: 100%'))
    body = ('<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 16px; min-width: 0">%s'
      '<div style="display: flex; gap: 16px; flex-grow: 1; min-height: 0"><div style="width: 470px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px">%s<div style="display: flex; gap: 12px">%s%s%s</div></div>%s</div></div>') % (brief, chart_card, t1, t2, t3, decision)
    ticker = ('<div style="height: 40px; padding: 0 14px 0 6px; border-radius: 999px; background: #FFFFFF; box-shadow: %s; display: flex; align-items: center; gap: 10px; font-size: 13px">%s'
              '<span style="color: %s">%s</span><b style="font-weight: 600">%s</b><span style="display: flex; gap: 3px">%s%s%s</span></div>') % (
              SH, orb(28), INK3, T('Arth abhi', 'अर्थ अभी'), T('Balaji se rate le raha hai', 'बालाजी से रेट ले रहा है'), dot(CYAN, 6), dot(CYAN, 6), dot('#C9EFFC', 6))
    return screen('Arth home' + (' Hindi' if hi else ''), 'home', T('Namaste, Ramesh ji', 'नमस्ते, रमेश जी'), T('Gupta General Store · Thu 29 Oct · 2:10 pm', 'गुप्ता जनरल स्टोर · गुरु 29 अक्टूबर · 2:10 pm'), body,
                  right=ticker, hindi=hi, mstate='speaking')
open(OUT + 'ScreenHome.dc.html', 'w').write(home(False))
open(OUT + 'ScreenHomeHindi.dc.html', 'w').write(home(True))
print('home ok')
