from c2 import *

def pipeline(steps, w='100%'):
    """steps: (title, sub, state) state in done|wait|next"""
    out = ''
    for i, (t, sub, st) in enumerate(steps):
        if st == 'done':
            ic = '<span style="width: 28px; height: 28px; border-radius: 999px; background: %s; color: #FFFFFF; display: flex; align-items: center; justify-content: center">%s</span>' % (GRNF, svg(I['check'], 15, 2.8))
        elif st == 'wait':
            ic = '<span style="width: 28px; height: 28px; border-radius: 999px; background: %s; box-shadow: 0 0 0 5px rgba(245,165,36,0.22); display: flex; align-items: center; justify-content: center">%s</span>' % (AMB, dot('#FFFFFF', 8))
        else:
            ic = '<span style="width: 28px; height: 28px; border-radius: 999px; background: #FFFFFF; box-shadow: inset 0 0 0 2px #D0D5DD"></span>'
        line = '' if i == len(steps) - 1 else '<span style="position: absolute; left: 30px; right: -2px; top: 13px; height: 2px; background: %s"></span>' % (GRNF if st == 'done' else '#E4E7EC')
        out += ('<div style="flex: 1; position: relative; display: flex; flex-direction: column; gap: 8px; min-width: 0">%s<span style="position: relative">%s</span>'
                '<span style="font-size: 13.5px; font-weight: 600; color: %s">%s</span><span style="font-size: 12px; color: %s">%s</span></div>') % (line, ic, AMBT if st == 'wait' else INK, t, INK3, sub)
    return '<div style="display: flex; gap: 0; width: %s">%s</div>' % (w, out)

def ticker(label, what, extra=''):
    return ('<div style="height: 40px; padding: 0 14px 0 6px; border-radius: 999px; background: #FFFFFF; box-shadow: %s; display: inline-flex; align-items: center; gap: 10px; font-size: 13px; %s">%s'
            '<span style="color: %s">%s</span><b style="font-weight: 600">%s</b><span style="display: flex; gap: 3px">%s%s%s</span></div>') % (SH, extra, orb(28), INK3, label, what, dot(CYAN, 6), dot(CYAN, 6), dot('#C9EFFC', 6))

def learned(text, sub):
    return ('<div style="padding: 14px 16px; border-radius: 18px; background: #FFFFFF; box-shadow: %s; display: flex; flex-direction: column; gap: 10px">'
            '<div style="display: flex; align-items: center; gap: 10px">%s<span style="font-size: 12px; font-weight: 700; letter-spacing: 0.04em; color: %s">ARTH NE SEEKHA</span></div>'
            '<span style="font-size: 15px; font-weight: 600; line-height: 1.4">%s</span><span style="font-size: 12.5px; color: %s">%s</span>'
            '<div style="display: flex; gap: 8px">%s%s%s</div></div>') % (SH, orb(22), CYT, text, INK3, sub,
            btn(svg(I['check'], 15, 2.4) + 'Sahi hai', 'tint', 36, 13), btn('Galat', 'ghost', 36, 13), btn('Bhool jao', 'text', 36, 13))

def undo_toast(text, secs):
    return ('<div style="height: 56px; padding: 0 8px 0 10px; border-radius: 18px; background: %s; color: #FFFFFF; box-shadow: %s; display: inline-flex; align-items: center; gap: 12px">%s'
            '<span style="font-size: 14px">%s</span><span style="width: 1px; height: 24px; background: rgba(255,255,255,0.2)"></span>'
            '<button style="height: 40px; padding: 0 14px; border-radius: 12px; border: none; background: rgba(255,255,255,0.12); color: #7DE8FF; font-family: inherit; font-size: 14px; font-weight: 700">Wapas lo · %s</button></div>') % (MID, SH2, orb(30), text, secs)

def nudge(title, text, cta):
    return ('<div style="padding: 14px 16px; border-radius: 18px; background: %s; box-shadow: inset 0 0 0 1px #F8DFA6; display: flex; align-items: flex-start; gap: 12px">%s'
            '<div style="display: flex; flex-direction: column; gap: 3px; flex-grow: 1"><span style="font-size: 14.5px; font-weight: 700; color: %s">%s</span><span style="font-size: 13.5px; line-height: 1.45; color: %s">%s</span></div>%s</div>') % (
            AMBTINT, orb(28), AMBT, title, INK, text, btn(cta, 'ghost', 36, 13, 'flex-shrink: 0'))

def provenance(items):
    return '<div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 12px; color: %s">%s<span>Kahaan se:</span>%s</div>' % (INK3, svg(I['lock'], 13, 2), ''.join(chip(i, GROUND, INK2, 24, 12, 500, False) for i in items))

def confidence(label, lo, mid, hi, pos, conf, reasons):
    rs = ''.join('<div style="display: flex; justify-content: space-between; gap: 12px; font-size: 13px; padding: 6px 0; %s"><span>%s</span><b style="color: %s; white-space: nowrap">%s</b></div>' % ('' if i == 0 else 'border-top: 1px solid %s' % LINE, a, GRN if b.startswith('+') else RED if b.startswith('−') else INK2, b) for i, (a, b) in enumerate(reasons))
    return ('<div style="padding: 16px 18px; border-radius: 20px; background: #FFFFFF; box-shadow: %s; display: flex; flex-direction: column; gap: 8px">'
            '<div style="display: flex; justify-content: space-between; align-items: center"><span style="font-size: 12.5px; color: %s">%s</span>%s</div>'
            '<span style="font-size: 28px; font-weight: 800; letter-spacing: -0.03em">%s</span>'
            '<div style="position: relative; height: 18px"><div style="position: absolute; left: 0; right: 0; top: 6px; height: 6px; border-radius: 999px; background: #EEF1F5"></div><div style="position: absolute; left: 16%%; right: 20%%; top: 6px; height: 6px; border-radius: 999px; background: #9BE3F9"></div><div style="position: absolute; left: %d%%; top: 0; width: 4px; height: 18px; border-radius: 2px; background: %s"></div></div>'
            '<div style="display: flex; justify-content: space-between; font-size: 12px; color: %s"><span>%s</span><span>%s</span></div>'
            '<div style="margin-top: 4px; padding: 10px 12px; border-radius: 14px; background: %s"><div style="display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 700; color: %s; padding-bottom: 2px">%sKyun?</div>%s</div></div>') % (
            SH, INK3, label, chip(conf, SKY, CYT, 24, 11.5, 700, False), mid, pos, MID, INK3, lo, hi, GROUND, CYT, orb(18, False), rs)

def tone_draft(msg):
    return ('<div style="padding: 14px; border-radius: 20px; background: #FFFFFF; box-shadow: %s; display: flex; flex-direction: column; gap: 10px">'
            '<div style="display: flex; align-items: center; gap: 8px">%s<span style="font-size: 13px; font-weight: 700; color: %s; white-space: nowrap">Arth ne likha</span><span style="margin-left: auto; display: flex; gap: 4px; padding: 3px; border-radius: 999px; background: %s">%s%s%s</span></div>'
            '<div style="padding: 12px 14px; border-radius: 14px; background: #D9FDD3; font-size: 14px; line-height: 1.5">%s</div>'
            '<div style="display: flex; gap: 8px">%s%s</div></div>') % (
            SH, orb(22), CYT, GROUND, chip('Narm', '#FFFFFF', MID, 28, 12.5, 700, False).replace('box-shadow', 'x') , chip('Seedha', GROUND, INK2, 28, 12.5, 500, False), chip('Formal', GROUND, INK2, 28, 12.5, 500, False),
            msg, btn(svg(I['send'], 16, 2) + 'Bhejo', 'primary', 40, 13.5, 'flex: 1'), btn('Hindi → English', 'ghost', 40, 13))
