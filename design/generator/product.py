import sys; sys.path.insert(0, '/home/claude/design/gen2')
from c2 import *
OUT = '/home/claude/design/project/'
KNIT = lambda base, hi='0.08', lo='0.22': ('background-color: %s; background-image: linear-gradient(180deg, rgba(255,255,255,0.10) 0%%, rgba(255,255,255,0) 35%%, rgba(0,0,0,0.22) 100%%), radial-gradient(rgba(255,255,255,%s) 1px, transparent 1.5px), radial-gradient(rgba(0,0,0,%s) 1px, transparent 1.5px); background-size: 100%% 100%%, 6px 6px, 6px 6px; background-position: 0 0, 0 0, 3px 3px' % (base, hi, lo))
MIDK = '#122E5C'

# ---------- HERO: front view ----------
SC = 0.76; PW = round(960 * SC); PH = round(720 * SC); BZ = 16
panel = ('<div style="position: absolute; left: 50%%; margin-left: -%dpx; top: 0; width: %dpx; height: %dpx; border-radius: 34px; background: #0A101C; box-shadow: 0 1px 0 rgba(255,255,255,0.18) inset, 0 0 0 1.5px #1B2436, 0 40px 60px -20px rgba(5,20,50,0.55); transform: perspective(2200px) rotateX(5deg); transform-origin: 50%% 100%%">'
  '<span style="position: absolute; left: 50%%; top: 7px; margin-left: -14px; display: flex; gap: 16px">%s%s</span>'
  '<div style="position: absolute; left: %dpx; top: %dpx; width: %dpx; height: %dpx; border-radius: 20px; overflow: hidden; background: #F5F7FA">'
   '<div style="width: 960px; height: 720px; transform: scale(%s); transform-origin: 0 0"><dc-import name="ScreenHome" hint-size="960px,720px"></dc-import></div>'
   '<div style="position: absolute; inset: 0; background: linear-gradient(128deg, rgba(255,255,255,0.16) 0%%, rgba(255,255,255,0) 30%%); pointer-events: none"></div></div></div>') % (
  (PW + 2 * BZ) // 2, PW + 2 * BZ, PH + 2 * BZ, dot('#2A3550', 4), dot('#2A3550', 4), BZ, BZ, PW, PH, SC)
BW = PW + 2 * BZ + 96
base = ('<div style="position: absolute; left: 50%%; margin-left: -%dpx; top: %dpx; width: %dpx; height: 150px; border-radius: 44px 44px 80px 80px / 40px 40px 70px 70px; %s; box-shadow: inset 0 2px 0 rgba(255,255,255,0.16), inset 0 -18px 30px rgba(0,0,0,0.30), 0 30px 50px -10px rgba(5,20,50,0.45)">'
  '<span style="position: absolute; left: 50%%; bottom: 30px; margin-left: -80px; width: 160px; height: 7px; border-radius: 999px; background: #7DE8FF; box-shadow: 0 0 10px 2px rgba(0,186,242,0.85), 0 0 34px 8px rgba(0,186,242,0.35)"></span>'
  '<span style="position: absolute; left: 56px; bottom: 26px; font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: #1E3F78; text-shadow: 0 1px 0 rgba(255,255,255,0.06), 0 -1px 0 rgba(0,0,0,0.35)">arth</span>'
  '<span style="position: absolute; right: 52px; bottom: 18px; width: 44px; height: 44px; border-radius: 999px; background: radial-gradient(circle at 40%% 30%%, #24457E, #0C2249); box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 0 0 2px rgba(0,186,242,0.55), 0 2px 6px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; color: #7DE8FF">%s</span>'
  '</div>') % (BW // 2, PH + 2 * BZ - 64, BW, KNIT(MIDK), svg(I['mic'], 20, 2.1))
hero = ('<div style="position: relative; width: %dpx; height: %dpx">'
  '<div style="position: absolute; left: 50%%; margin-left: -%dpx; top: %dpx; width: %dpx; height: 60px; border-radius: 999px; background: radial-gradient(ellipse at center, rgba(5,20,50,0.38) 0%%, rgba(5,20,50,0) 70%%)"></div>'
  '%s%s</div>') % (BW + 40, PH + 2 * BZ - 64 + 150 + 40, (BW + 80) // 2, PH + 2 * BZ - 64 + 120, BW + 80, base, panel)

# ---------- SIDE PROFILE ----------
side = ('<svg width="300" height="210" viewBox="0 0 300 210" role="img" aria-label="Side profile: screen leans back 12 degrees on a knit speaker base">'
  '<defs><linearGradient id="kn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1C3E74"/><stop offset="1" stop-color="#0B2149"/></linearGradient>'
  '<pattern id="kd" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#FFFFFF" opacity="0.08"/><circle cx="4.5" cy="4.5" r="1" fill="#000000" opacity="0.2"/></pattern></defs>'
  '<ellipse cx="150" cy="198" rx="120" ry="8" fill="#0B1B33" opacity="0.14"/>'
  '<g transform="rotate(12 96 150)"><rect x="88" y="6" width="16" height="148" rx="8" fill="#0A101C"/><rect x="88" y="6" width="4" height="148" rx="2" fill="#3A4766"/></g>'
  '<path d="M64 196 Q40 196 46 170 L62 132 Q68 118 84 118 L206 118 Q228 118 236 136 L254 172 Q262 196 236 196 Z" fill="url(#kn)"/>'
  '<path d="M64 196 Q40 196 46 170 L62 132 Q68 118 84 118 L206 118 Q228 118 236 136 L254 172 Q262 196 236 196 Z" fill="url(#kd)"/>'
  '<rect x="44" y="164" width="6" height="16" rx="3" fill="#7DE8FF"/><rect x="44" y="164" width="6" height="16" rx="3" fill="#00BAF2" opacity="0.4" transform="translate(-2 0) scale(1)"/>'
  '</svg>')

# ---------- BACK VIEW: customer display ----------
back = ('<div style="position: relative; width: 300px; height: 210px">'
  '<div style="position: absolute; left: 30px; top: 6px; width: 240px; height: 132px; border-radius: 22px; background: linear-gradient(160deg, #1A2335, #0D1422); box-shadow: inset 0 1px 0 rgba(255,255,255,0.12); display: flex; align-items: center; justify-content: center">%s</div>'
  '<div style="position: absolute; left: 0; top: 110px; width: 300px; height: 92px; border-radius: 28px 28px 50px 50px / 26px 26px 44px 44px; %s; box-shadow: inset 0 2px 0 rgba(255,255,255,0.14), 0 16px 26px -10px rgba(5,20,50,0.45)">'
   '<div style="position: absolute; left: 50%%; top: 18px; margin-left: -78px; width: 156px; height: 54px; border-radius: 14px; background: #04070D; box-shadow: inset 0 0 0 1.5px #1B2436; display: flex; align-items: center; justify-content: center; gap: 10px">'
    '<span style="font-family: Doto, monospace; font-size: 30px; font-weight: 800; color: #7DE8FF; text-shadow: 0 0 8px rgba(0,186,242,0.7)">₹62</span>'
    '<span style="display: flex; flex-direction: column; gap: 2px; font-size: 9.5px; font-weight: 700; color: #7CF5B2; letter-spacing: 0.06em">PAID<span style="color: #6B7A93; font-weight: 600">UPI</span></span></div></div></div>') % (
  '<span style="width: 34px; height: 34px; border-radius: 999px; background: radial-gradient(circle at 36% 30%, #3A4A66, #121B2C); box-shadow: inset 0 1px 0 rgba(255,255,255,0.14)"></span>', KNIT(MIDK))

def finish(name, col, txt, sel):
    return ('<div style="display: flex; flex-direction: column; align-items: center; gap: 8px">'
            '<div style="width: 92px; height: 70px; position: relative">'
            '<span style="position: absolute; left: 14px; top: 0; width: 64px; height: 48px; border-radius: 8px; background: #0A101C; box-shadow: inset 0 0 0 3px #0A101C, inset 0 0 0 30px %s"></span>'
            '<span style="position: absolute; left: 0; top: 38px; width: 92px; height: 30px; border-radius: 12px 12px 18px 18px; %s"></span>'
            '<span style="position: absolute; left: 34px; top: 58px; width: 24px; height: 3px; border-radius: 3px; background: #7DE8FF; box-shadow: 0 0 6px #00BAF2"></span></div>'
            '<span style="font-size: 13px; font-weight: %d; color: %s">%s</span></div>') % (SKY, KNIT(col, '0.1', '0.12'), 700 if sel else 500, INK if sel else INK2, name)

lights = ''.join('<div style="display: flex; align-items: center; gap: 10px; height: 44px; padding: 0 16px 0 12px; border-radius: 14px; background: #FFFFFF; box-shadow: %s">'
                 '<span style="width: 40px; height: 6px; border-radius: 999px; background: %s; box-shadow: 0 0 10px 1px %s"></span><span style="font-size: 13px; font-weight: 600">%s</span><span style="font-size: 12px; color: %s">%s</span></div>' % (SH, c, g, a, INK3, b)
                 for c, g, a, b in [('#7DE8FF', 'rgba(0,186,242,0.8)', 'Sun raha', 'cyan, saans'), ('#F5A524', 'rgba(245,165,36,0.8)', 'Haan chahiye', 'amber'), ('#12B76A', 'rgba(18,183,106,0.8)', 'Paisa aaya', 'hara, 2 sec'), ('#98A2B3', 'rgba(152,162,179,0.4)', 'Offline', 'grey')])

specs = ''.join('<div style="display: flex; justify-content: space-between; gap: 12px; padding: 9px 0; border-top: 1px solid #DDE3EA; font-size: 13.5px"><span style="color: %s">%s</span><span style="font-weight: 600; text-align: right">%s</span></div>' % (INK2, a, b)
                for a, b in [('Display', '8" 4:3 touch, matte glass'), ('Awaaz', '5 W speaker · 2 far-field mics'), ('Grahak ke liye', 'Peeche dot display · amount + paid'), ('Connectivity', '4G + Wi-Fi · 10 h battery'), ('Privacy', 'Koi camera nahi · mic mute button')])

lab = lambda t: '<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: %s">%s</span>' % (INK3, t)
body = ('<div style="width: 1600px; height: 1100px; box-sizing: border-box; padding: 56px 64px; background: radial-gradient(ellipse at 38%% 45%%, #FFFFFF 0%%, #EEF2F7 45%%, #E1E7EF 100%%); font-family: %s; color: %s; display: flex; gap: 56px; overflow: hidden">'
  '<div style="flex-grow: 1; display: flex; flex-direction: column">'
   '<div style="display: flex; align-items: center; gap: 12px">%s<span style="font-size: 14px; font-weight: 600; color: %s">Concept render · dukaan ke counter ke liye</span></div>'
   '<h1 style="margin: 14px 0 6px; font-size: 52px; font-weight: 800; letter-spacing: -0.035em">Arth Display</h1>'
   '<p style="margin: 0; font-size: 18px; line-height: 1.5; color: %s; max-width: 640px">Ek hi cheez: knit speaker par tika 4:3 screen. Saamne dukaandar ke liye Arth, peeche grahak ke liye amount. Neeche ki light wahi batati hai jo orb batata hai.</p>'
   '<div style="margin-top: auto; display: flex; justify-content: center">%s</div>'
   '<div style="margin-top: 28px; display: flex; gap: 10px; justify-content: center">%s</div></div>'
  '<aside style="width: 380px; flex-shrink: 0; display: flex; flex-direction: column; gap: 22px; padding-top: 8px">'
   '<div style="display: flex; flex-direction: column; gap: 6px">%s%s</div>'
   '<div style="display: flex; flex-direction: column; gap: 6px">%s%s</div>'
   '<div style="display: flex; flex-direction: column; gap: 12px">%s<div style="display: flex; gap: 18px">%s%s%s</div></div>'
   '<div style="display: flex; flex-direction: column">%s<div style="margin-top: 10px">%s</div><span style="margin-top: 8px; font-size: 12px; color: %s">Concept specs · hackathon prototype tablet + speaker par chalta hai</span></div>'
  '</aside></div>') % (
  FF, INK, mascot('idle', 30), CYT, INK2, hero, lights,
  lab('Side · 12° jhukav'), side, lab('Peeche · grahak ki taraf'), back,
  lab('Finish'), finish('Midnight knit', MIDK, '', True), finish('Chalk knit', '#D9DEE5', '', False), finish('Sky knit', '#2BA8DA', '', False),
  lab('Andar kya hai'), specs, INK3)
html = page('Arth Display product render', body, w=1600, h=1100).replace('</helmet>', '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Doto:wght@600;800&amp;display=swap">\n</helmet>', 1)
open(OUT + 'Product.dc.html', 'w').write(html)
print('ok', BW, PH)
