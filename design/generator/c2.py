from icons import I, svg, pack
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
         '&amp;family=Noto+Sans+Devanagari:wght@400;500;600;700&amp;family=Noto+Sans+Tamil:wght@400;600'
         '&amp;family=Noto+Sans+Bengali:wght@500&amp;family=Noto+Sans+Gujarati:wght@500&amp;family=Noto+Sans+Telugu:wght@500&amp;display=swap">')
FF = "'Inter', 'Noto Sans Devanagari', 'Noto Sans Tamil', system-ui, sans-serif"
FF_HI = "'Noto Sans Devanagari', 'Inter', system-ui, sans-serif"
# Paytm palette
MID = '#002E6E'; CYAN = '#00BAF2'; SKY = '#E8F8FE'; GROUND = '#F5F7FA'; LINE = '#EDEFF0'
INK = '#0B1B33'; INK2 = '#475467'; INK3 = '#5B6475'; CYT = '#0077B6'
RED = '#D0103F'; REDT = '#FDECEF'; GRN = '#067647'; GRNF = '#12B76A'; GRNT = '#E7F8EF'
AMB = '#F5A524'; AMBT = '#8A5300'; AMBTINT = '#FFF6E0'
SH = '0 1px 2px rgba(16,24,40,0.04), 0 6px 20px rgba(16,24,40,0.05)'
SH2 = '0 2px 6px rgba(16,24,40,0.06), 0 16px 40px rgba(16,24,40,0.10)'

def card(extra=''):
    return 'background: #FFFFFF; border-radius: 24px; box-shadow: %s; %s' % (SH, extra)

def chip(text, bg='#FFFFFF', fg=INK, h=36, fs=14, w=500, border=True):
    b = 'box-shadow: inset 0 0 0 1px %s;' % LINE if border and bg == '#FFFFFF' else ''
    return '<span style="height: %dpx; padding: 0 14px; border-radius: 999px; background: %s; color: %s; font-size: %spx; font-weight: %d; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; %s">%s</span>' % (h, bg, fg, fs, w, b, text)

def dot(c, s=8):
    return '<span style="width: %dpx; height: %dpx; border-radius: 999px; background: %s; display: inline-block; flex-shrink: 0"></span>' % (s, s, c)

def btn(text, kind='primary', h=52, fs=16, extra=''):
    st = {'primary': 'border: none; background: %s; color: %s; font-weight: 700' % (CYAN, MID),
          'dark': 'border: none; background: %s; color: #FFFFFF; font-weight: 600' % MID,
          'amber': 'border: none; background: %s; color: %s; font-weight: 700' % (AMB, INK),
          'ghost': 'border: none; background: #FFFFFF; box-shadow: inset 0 0 0 1.5px #D9DEE5; color: %s; font-weight: 600' % INK,
          'text': 'border: none; background: transparent; color: %s; font-weight: 600; padding: 0 8px' % MID,
          'tint': 'border: none; background: %s; color: %s; font-weight: 600' % (SKY, MID),
          'danger': 'border: none; background: #FFFFFF; box-shadow: inset 0 0 0 1.5px #F5C2CD; color: %s; font-weight: 600' % RED}[kind]
    return '<button style="height: %dpx; padding: 0 22px; border-radius: 16px; %s; font-family: inherit; font-size: %dpx; display: inline-flex; align-items: center; justify-content: center; gap: 8px; %s">%s</button>' % (h, st, fs, extra, text)

def mascot(state, size):
    return '<dc-import name="Mascot" state="%s" size="%d" hint-size="%dpx,%dpx"></dc-import>' % (state, size, size, round(size * 1.1))

NAV = [('home', 'Aaj', 'आज', 'ScreenHome.dc.html'), ('bill', 'Bill', 'बिल', 'ScreenBilling.dc.html'), ('khata', 'Khata', 'खाता', 'ScreenKhata.dc.html'),
       ('box', 'Stock', 'स्टॉक', 'ScreenInventory.dc.html'), ('grid', 'More', 'और', 'ScreenMenu.dc.html')]

def rail(active, hindi=False, mstate='idle'):
    items = ''
    for key, en, hi, href in NAV:
        lab = hi if hindi else en
        on = key == active
        items += ('<a href="%s"%s style="width: 60px; height: 58px; border-radius: 16px; background: %s; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; text-decoration: none; color: %s">%s<span style="font-size: 11.5px; font-weight: %s">%s</span></a>'
                  % (href, ' aria-current="page"' if on else '', SKY if on else 'transparent', MID if on else INK3, svg(I[key], 22, 2 if on else 1.8), 700 if on else 500, lab))
    return ('<nav aria-label="Main" style="width: 80px; flex-shrink: 0; background: #FFFFFF; box-shadow: inset -1px 0 0 %s; display: flex; flex-direction: column; align-items: center; padding: 12px 0 16px; box-sizing: border-box; gap: 6px">'
            '<a href="ScreenAsk.dc.html" aria-label="Arth" style="display: flex; margin-bottom: 8px">%s</a>%s'
            '<div style="margin-top: auto; display: flex; flex-direction: column; align-items: center; gap: 10px">'
            '<a href="ScreenLanguage.dc.html" aria-label="Language" style="height: 30px; padding: 0 10px; border-radius: 999px; box-shadow: inset 0 0 0 1px %s; display: flex; align-items: center; font-size: 12px; font-weight: 600; color: %s; text-decoration: none; font-family: %s">%s</a>'
            '<span style="width: 36px; height: 36px; border-radius: 999px; background: %s; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700" aria-label="Ramesh, owner">R</span></div></nav>') % (
            LINE, mascot(mstate, 50), items, LINE, MID, FF_HI, 'हि · En' if not hindi else 'En · हि', MID)

def header(title, sub, right=''):
    return ('<header style="height: 76px; flex-shrink: 0; padding: 0 32px; display: flex; align-items: center; gap: 16px">'
            '<div style="display: flex; flex-direction: column; gap: 2px; min-width: 0"><h1 style="margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap">%s</h1>'
            '<span style="font-size: 13.5px; color: %s; white-space: nowrap">%s</span></div><div style="margin-left: auto; display: flex; align-items: center; gap: 10px">%s</div></header>') % (title, INK3, sub, right)

def dock(chips=None, placeholder='Bolo ya likho — jaise "Sharma ji ka hisaab"', hindi=False):
    ch = ''
    if chips:
        ch = '<div style="display: flex; gap: 8px; padding-left: 4px">' + ''.join(chip(c, '#FFFFFF', MID, 34, 13.5, 600) for c in chips) + '</div>'
    return ('<div style="flex-shrink: 0; padding: 0 32px 20px; display: flex; flex-direction: column; gap: 10px">%s'
            '<div style="height: 60px; border-radius: 999px; background: #FFFFFF; box-shadow: %s; display: flex; align-items: center; gap: 10px; padding: 0 8px 0 18px">'
            '<span style="width: 10px; height: 10px; border-radius: 999px; background: %s; box-shadow: 0 0 0 4px %s"></span>'
            '<input aria-label="Ask Arth" placeholder=\'%s\' style="flex-grow: 1; min-width: 0; border: none; outline: none; background: transparent; font-family: %s; font-size: 15.5px; color: %s">'
            '<button aria-label="Hold to talk" style="width: 46px; height: 46px; border-radius: 999px; border: none; background: %s; color: %s; display: flex; align-items: center; justify-content: center">%s</button></div></div>') % (
            ch, SH2, CYAN, SKY, placeholder, FF_HI if hindi else FF, INK, CYAN, MID, svg(I['mic'], 22, 2.1))

def page(title, body, script='return {};', w=960, h=720, lang='en'):
    return ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n<title>%s</title>\n<script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n%s\n<style>\nbody{margin:0}\na{color:#002E6E}\n</style>\n</helmet>\n%s\n</x-dc>\n'
            '<script type="text/x-dc" data-dc-script data-props=\'{"$preview":{"width":%d,"height":%d}}\'>\nclass Component extends DCLogic {\n  renderVals() {\n    %s\n  }\n}\n</script>\n</body>\n</html>\n') % (lang, title, FONTS, body, w, h, script)

def screen(title, active, htitle, hsub, body, right='', chips=None, placeholder=None, hindi=False, overlay='', mstate='idle', nodock=False, script='return {};', live=None):
    d = dock_live(*live) if live else '' if nodock else dock(chips, placeholder or ('बोलिए या लिखिए — जैसे "शर्मा जी का हिसाब"' if hindi else 'Bolo ya likho — jaise "Sharma ji ka hisaab"'), hindi)
    b = ('<div style="width: 960px; height: 720px; background: %s; font-family: %s; color: %s; display: flex; overflow: hidden; position: relative">' % (GROUND, FF_HI if hindi else FF, INK)
         + rail(active, hindi, mstate) +
         '<div style="flex-grow: 1; display: flex; flex-direction: column; min-width: 0">' + header(htitle, hsub, right) +
         '<main style="flex-grow: 1; min-height: 0; padding: 0 32px 16px; display: flex; gap: 20px; box-sizing: border-box">' + body + '</main>' + d + '</div>' + overlay + '</div>')
    return page(title, b, script, lang='hi' if hindi else 'en')

def avatar(ini, bg, fg, s=40):
    return '<span style="width: %dpx; height: %dpx; border-radius: 999px; background: %s; color: %s; display: flex; align-items: center; justify-content: center; font-size: %dpx; font-weight: 700; flex-shrink: 0">%s</span>' % (s, s, bg, fg, int(s * 0.34), ini)

def arth_note(text, extra=''):
    return ('<div style="display: flex; gap: 12px; align-items: flex-start; padding: 14px 16px; border-radius: 18px; background: %s; %s">'
            '%s<span style="font-size: 14.5px; line-height: 1.5; color: %s">%s</span></div>') % (SKY, extra, orb(26), INK, text)

def toggle(on):
    return ('<span role="switch" aria-checked="%s" style="width: 44px; height: 26px; border-radius: 999px; background: %s; position: relative; display: inline-block; flex-shrink: 0"><span style="position: absolute; top: 3px; %s: 3px; width: 20px; height: 20px; border-radius: 999px; background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.2)"></span></span>') % (
            'true' if on else 'false', CYAN if on else '#D0D5DD', 'right' if on else 'left')

def wa_bubble(text, by='Sent by Arth', time='9:13 am', extra=''):
    return ('<div style="align-self: flex-start; max-width: 92%%; padding: 10px 12px 7px; border-radius: 16px 16px 16px 4px; background: #FFFFFF; box-shadow: 0 1px 1px rgba(16,24,40,0.08); font-size: 14px; line-height: 1.45; color: %s">'
            '<div style="font-size: 11px; font-weight: 600; color: %s; margin-bottom: 3px">%s</div>%s%s<div style="text-align: right; font-size: 10.5px; color: %s; margin-top: 3px">%s</div></div>') % (INK, CYT, by, text, extra, INK3, time)

ORBG = 'radial-gradient(circle at 36% 30%, #8FE3FF 0%, #1CB8EE 34%, #0A63B5 72%, #05295F 100%)'
def orb(s=24, eyes=True, extra=''):
    """Mini Arth orb, the AI marker used across the UI."""
    e = ''
    if eyes and s >= 18:
        ew = max(2, round(s * 0.075)); eh = max(4, round(s * 0.17))
        e = '<span style="width: %dpx; height: %dpx; border-radius: 9px; background: #FFFFFF"></span>' % (ew, eh)
        e = e + e
    return '<span style="width: %dpx; height: %dpx; border-radius: 999px; background: %s; box-shadow: 0 0 0 3px rgba(0,186,242,0.12), inset 0 -%dpx %dpx rgba(125,232,255,0.55); display: inline-flex; align-items: center; justify-content: center; gap: %dpx; flex-shrink: 0; %s">%s</span>' % (s, s, ORBG, max(2, s // 6), max(3, s // 4), max(2, round(s * 0.11)), extra, e)

def wave(n=24, h=26, color=None, seed=3):
    import math
    c = color or CYAN
    bars = ''.join('<span style="width: 3px; height: %dpx; border-radius: 3px; background: %s; opacity: %.2f"></span>' % (max(4, round(h * (0.35 + 0.65 * abs(math.sin(i * 0.9 + seed) * math.cos(i * 0.37))))), c, 0.55 + 0.45 * abs(math.sin(i * 0.5))) for i in range(n))
    return '<span style="display: inline-flex; align-items: center; gap: 3px; height: %dpx">%s</span>' % (h, bars)

def dock_live(heard, parsed, hindi=False):
    """Dock in listening state: live transcript + what Arth understood."""
    return ('<div style="flex-shrink: 0; padding: 0 32px 20px; display: flex; flex-direction: column; gap: 10px">'
            '<div style="height: 64px; border-radius: 999px; background: %s; box-shadow: %s, 0 0 0 4px rgba(0,186,242,0.18); display: flex; align-items: center; gap: 14px; padding: 0 8px 0 10px">'
            '%s<span style="font-size: 15.5px; color: #FFFFFF; flex-grow: 1; white-space: nowrap; overflow: hidden">%s</span>%s'
            '<span style="height: 34px; padding: 0 12px; border-radius: 999px; background: rgba(255,255,255,0.12); color: #FFFFFF; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap">%s</span>'
            '<button aria-label="Stop listening" style="width: 48px; height: 48px; border-radius: 999px; border: none; background: %s; color: %s; display: flex; align-items: center; justify-content: center"><span style="width: 14px; height: 14px; border-radius: 4px; background: %s"></span></button></div></div>') % (
            MID, SH2, orb(44), heard, wave(16, 24, '#7DE8FF'), parsed, CYAN, MID, MID)
