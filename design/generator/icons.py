FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=Noto+Sans+Devanagari:wght@400;500;600&amp;display=swap">'

def svg(paths, size=22, sw=1.8, color='currentColor'):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>') % (size, size, color, sw, paths)

I = {
 'home': '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
 'bill': '<path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
 'mic': '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
 'khata': '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M9 7h6M9 11h4"/>',
 'grid': '<rect x="4" y="4" width="6.5" height="6.5" rx="1.6"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.6"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.6"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.6"/>',
 'scan': '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M7 12h10"/>',
 'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
 'box': '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
 'trend': '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 'users': '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M16 4a4 4 0 0 1 0 8M22 21a7 7 0 0 0-4-6.3"/>',
 'tag': '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
 'truck': '<path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
 'cart': '<path d="M3 4h2l2 12h11l2-8H6"/><circle cx="9" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'check': '<path d="m5 12 5 5 9-10"/>',
 'x': '<path d="M6 6l12 12M18 6 6 18"/>',
 'chat': '<path d="M4 5h16v11H9l-5 4z"/>',
 'settings': '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
 'speaker': '<path d="M4 10v4h4l5 4V6L8 10z"/><path d="M16 9a4 4 0 0 1 0 6M19 6a8 8 0 0 1 0 12"/>',
 'qr': '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2v2M20 14v6h-6M17 17v3"/>',
 'alert': '<path d="M12 3 2 21h20z"/><path d="M12 10v5M12 18h.01"/>',
 'gift': '<rect x="3" y="8" width="18" height="5" rx="1"/><path d="M5 13v8h14v-8M12 8v13"/><path d="M12 8c-2-4-6-4-6-1.5S12 8 12 8s6 1 6-1.5S14 4 12 8"/>',
 'percent': '<path d="M19 5 5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
 'back': '<path d="m15 6-6 6 6 6"/>',
 'plus': '<path d="M12 5v14M5 12h14"/>',
 'lock': '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
 'send': '<path d="M4 12 20 4l-6 16-3-7z"/>',
 'chevron': '<path d="m9 6 6 6-6 6"/>',
 'bell': '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21a2 2 0 0 0 4 0"/>',
 'phone': '<path d="M5 4h4l2 5-3 2a11 11 0 0 0 5 5l2-3 5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 6a2 2 0 0 1 2-2"/>',
 'wallet': '<rect x="3" y="6" width="18" height="14" rx="3"/><path d="M3 10h18M16 15h2"/>',
}

# product thumbnail tiles: generic pack shapes, no brand marks
def pack(kind, size=44):
    t = {
     'noodle': ('#FFF4CC', '<rect x="9" y="8" width="26" height="28" rx="4" fill="#F6C21C"/><path d="M9 14h26" stroke="#D9A400" stroke-width="2"/><rect x="14" y="19" width="16" height="9" rx="2" fill="#E2482F"/>'),
     'biscuit': ('#FFF1DC', '<rect x="8" y="12" width="28" height="20" rx="4" fill="#F2A33A"/><rect x="8" y="12" width="7" height="20" rx="3" fill="#E08A1E"/><circle cx="24" cy="22" r="5" fill="#FFF3D6"/>'),
     'sugar': ('#EEF2F6', '<path d="M12 12c0-3 2-4 10-4s10 1 10 4v20c0 2-2 4-10 4s-10-2-10-4z" fill="#FFFFFF" stroke="#C7D0DC" stroke-width="1.5"/><path d="M15 22h14" stroke="#9AA6B6" stroke-width="2" stroke-linecap="round"/>'),
     'milk': ('#E6F0FF', '<path d="M15 14l4-6h6l4 6v22H15z" fill="#FFFFFF" stroke="#2C66C8" stroke-width="1.5"/><rect x="15" y="22" width="14" height="8" fill="#2C66C8"/>'),
     'salt': ('#E6F0FF', '<rect x="12" y="10" width="20" height="26" rx="3" fill="#1F5FC4"/><rect x="12" y="18" width="20" height="9" fill="#FFFFFF"/>'),
     'atta': ('#FBF1E2', '<path d="M11 13c0-3 3-5 11-5s11 2 11 5v21c0 2-3 3-11 3s-11-1-11-3z" fill="#E7C48C"/><path d="M22 16v14M19 19l3-3 3 3M19 24l3-3 3 3" stroke="#9A6A22" stroke-width="1.6" fill="none" stroke-linecap="round"/>'),
     'nuts': ('#F7EDE4', '<rect x="12" y="13" width="20" height="23" rx="5" fill="#FFFFFF" stroke="#C9B19A" stroke-width="1.5"/><rect x="11" y="9" width="22" height="6" rx="2" fill="#8C5A33"/><ellipse cx="19" cy="25" rx="3.5" ry="5" fill="#D9A066"/><ellipse cx="25.5" cy="27" rx="3.5" ry="5" fill="#C98A4E"/>'),
     'diya': ('#FFF1E6', '<path d="M9 25c4 7 22 7 26 0z" fill="#C2622D"/><path d="M22 12c3 4 3 7 0 9-3-2-3-5 0-9z" fill="#F5A524"/>'),
     'oil': ('#FFF8DB', '<path d="M18 8h8v4l3 4v18a3 3 0 0 1-3 3h-8a3 3 0 0 1-3-3V16l3-4z" fill="#F2C94C" stroke="#C9A227" stroke-width="1.2"/><rect x="15" y="22" width="14" height="7" fill="#FFFFFF" opacity="0.8"/>'),
     'sweet': ('#FDECF2', '<rect x="9" y="14" width="26" height="18" rx="3" fill="#D94C7A"/><path d="M9 20h26" stroke="#B83260" stroke-width="2"/><rect x="18" y="14" width="8" height="18" fill="#F5C2D3"/>'),
     'tea': ('#EAF6EE', '<rect x="12" y="10" width="20" height="26" rx="3" fill="#2E8B57"/><circle cx="22" cy="22" r="5" fill="#E9F7EF"/>'),
     'rice': ('#F3F5F9', '<path d="M11 13c0-3 3-5 11-5s11 2 11 5v21c0 2-3 3-11 3s-11-1-11-3z" fill="#FFFFFF" stroke="#C7D0DC" stroke-width="1.5"/><ellipse cx="22" cy="24" rx="6" ry="4" fill="#E5D9C3"/>'),
    }[kind]
    return ('<span style="width: %dpx; height: %dpx; border-radius: 14px; background: %s; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
            '<svg width="%d" height="%d" viewBox="0 0 44 44" aria-hidden="true">%s</svg></span>') % (size, size, t[0], size, size, t[1])

SHADOW = '0 1px 2px rgba(15,23,42,0.04), 0 8px 24px rgba(15,23,42,0.06)'

def card(style_extra=''):
    return 'background: #FFFFFF; border-radius: 22px; box-shadow: %s; %s' % (SHADOW, style_extra)

NAV = [('home','Aaj','ScreenHome.dc.html'),('bill','Bill','ScreenBilling.dc.html'),('khata','Khata','ScreenKhata.dc.html'),
       ('box','Stock','ScreenInventory.dc.html'),('trend','Insights','ScreenForecast.dc.html'),('tag','Offers','ScreenOffers.dc.html'),
       ('clock','Work','ScreenWork.dc.html'),('grid','Menu','ScreenMenu.dc.html')]

def rail(active):
    items = []
    for key, label, href in NAV:
        badge = ''
        if key == 'clock':
            badge = '<span style="position: absolute; top: 2px; right: 10px; min-width: 18px; height: 18px; padding: 0 5px; box-sizing: border-box; border-radius: 999px; background: #F5A524; color: #0B1B33; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center">2</span>'
        if key == active:
            items.append('<a href="%s" aria-current="page" style="position: relative; display: flex; flex-direction: column; align-items: center; gap: 4px; text-decoration: none; color: #FFFFFF"><span style="width: 52px; height: 36px; border-radius: 12px; background: #FFFFFF; color: #002E6E; display: flex; align-items: center; justify-content: center">%s</span><span style="font-size: 11.5px; font-weight: 700">%s</span>%s</a>' % (href, svg(I[key], 21, 2), label, badge))
        else:
            items.append('<a href="%s" style="position: relative; display: flex; flex-direction: column; align-items: center; gap: 4px; text-decoration: none; color: #C3D4EE"><span style="width: 52px; height: 36px; border-radius: 12px; display: flex; align-items: center; justify-content: center">%s</span><span style="font-size: 11.5px; font-weight: 500">%s</span>%s</a>' % (href, svg(I[key], 21, 1.8), label, badge))
    return ('<nav aria-label="Main" style="width: 84px; flex-shrink: 0; background: #002E6E; display: flex; flex-direction: column; align-items: center; padding: 16px 0 18px; box-sizing: border-box; gap: 6px">'
            '<span style="width: 40px; height: 40px; border-radius: 13px; background: #FFFFFF; color: #002E6E; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 10px">A</span>'
            + ''.join(items) +
            '<a href="ScreenAsk.dc.html" aria-label="Hold to talk to Arth" style="margin-top: auto; width: 60px; height: 60px; border-radius: 999px; background: #00B9F1; color: #002E6E; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 5px rgba(0,185,241,0.22), 0 8px 18px rgba(0,0,0,0.25)">%s</a>'
            '</nav>') % svg(I['mic'], 26, 2.1)

def topbar(title, sub, right_extra=''):
    return ('<header style="height: 68px; flex-shrink: 0; padding: 0 24px; display: flex; align-items: center; gap: 16px">'
            '<div style="display: flex; flex-direction: column; gap: 1px; min-width: 0"><h1 style="margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap">%s</h1><span style="font-size: 13px; color: #5E6B7F; white-space: nowrap">%s</span></div>'
            '<div style="margin-left: auto; display: flex; align-items: center; gap: 10px">%s'
            '<label style="height: 44px; width: 250px; padding: 0 6px 0 14px; border-radius: 999px; background: #FFFFFF; box-shadow: %s; display: flex; align-items: center; gap: 8px; box-sizing: border-box">%s<input aria-label="Ask Arth" placeholder="Arth se poochho…" style="flex-grow: 1; min-width: 0; border: none; outline: none; background: transparent; font: inherit; font-size: 15px; color: #0B1B33"><span style="width: 34px; height: 34px; border-radius: 999px; background: #EAF2FF; color: #002E6E; display: flex; align-items: center; justify-content: center">%s</span></label>'
            '<span style="width: 10px; height: 10px; border-radius: 999px; background: #0A7A45; box-shadow: 0 0 0 4px #DDF3E7" aria-label="Synced"></span>'
            '<span style="width: 40px; height: 40px; border-radius: 999px; background: #0B1B33; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 600" aria-label="Ramesh, owner">R</span>'
            '</div></header>') % (title, sub, right_extra, SHADOW, svg(I['search'], 18, 1.9, '#5E6B7F'), svg(I['mic'], 17, 2))

def page(title, body, script='return {};', preview=(960, 720)):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>%s</title>\n<script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n%s\n<style>\nbody{margin:0}\na{color:#002E6E}\n</style>\n</helmet>\n%s\n</x-dc>\n'
            '<script type="text/x-dc" data-dc-script data-props=\'{"$preview":{"width":%d,"height":%d}}\'>\nclass Component extends DCLogic {\n  renderVals() {\n    %s\n  }\n}\n</script>\n</body>\n</html>\n') % (title, FONT_LINK, body, preview[0], preview[1], script)

def screen(title, active, top_title, top_sub, main, right_extra='', script='return {};'):
    body = ('<div style="width: 960px; height: 720px; background: #F2F4F8; font-family: \'Inter\', \'Noto Sans Devanagari\', system-ui, sans-serif; color: #0B1B33; display: flex; overflow: hidden">'
            + rail(active) +
            '<div style="flex-grow: 1; display: flex; flex-direction: column; min-width: 0">'
            + topbar(top_title, top_sub, right_extra) +
            '<main style="flex-grow: 1; min-height: 0; padding: 0 24px 22px; display: flex; gap: 18px; box-sizing: border-box">' + main + '</main>'
            '</div></div>')
    return page(title, body, script)

def chip(text, bg, fg, h=28, fs=13, w=600):
    return '<span style="height: %dpx; padding: 0 11px; border-radius: 999px; background: %s; color: %s; font-size: %dpx; font-weight: %d; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap">%s</span>' % (h, bg, fg, fs, w, text)

def dot(c, s=8):
    return '<span style="width: %dpx; height: %dpx; border-radius: 999px; background: %s; display: inline-block; flex-shrink: 0"></span>' % (s, s, c)

def btn(text, kind='primary', h=48, fs=15, extra=''):
    st = {
      'primary': 'border: none; background: #002E6E; color: #FFFFFF; font-weight: 600',
      'amber': 'border: none; background: #F5A524; color: #0B1B33; font-weight: 600',
      'ghost': 'border: 1px solid #D5DCE6; background: #FFFFFF; color: #0B1B33; font-weight: 500',
      'tonal': 'border: none; background: #EAF2FF; color: #002E6E; font-weight: 600',
      'danger': 'border: 1px solid #F3C2C4; background: #FFFFFF; color: #C4262E; font-weight: 600',
      'green': 'border: none; background: #0A7A45; color: #FFFFFF; font-weight: 600',
    }[kind]
    return '<button style="height: %dpx; padding: 0 18px; border-radius: 14px; %s; font-family: inherit; font-size: %dpx; display: inline-flex; align-items: center; justify-content: center; gap: 8px; %s">%s</button>' % (h, st, fs, extra, text)

def mascot(state, size):
    return '<dc-import name="Mascot" state="%s" size="%d" hint-size="%dpx,%dpx"></dc-import>' % (state, size, size, round(size*1.1))
