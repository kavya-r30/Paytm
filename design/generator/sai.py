from c2 import *
from ai import *
from sd import board, sec, ttl, row
OUT = '/home/claude/design/project/'

brief = ('<div style="width: 592px; border-radius: 24px; background: linear-gradient(100deg, #E8F8FE 0%%, #F4FBFF 55%%, #FFFFFF 100%%); box-shadow: %s, inset 0 0 0 1px #D3F1FC; padding: 16px 20px 16px 14px; display: flex; gap: 14px; align-items: center">%s'
  '<div style="display: flex; flex-direction: column; gap: 10px"><p style="margin: 0; font-size: 16.5px; line-height: 1.45; font-weight: 500">Dopahar tak <b>₹4,180</b>, aam guruvaar se <b style="color: %s">13%% aage</b>. Shaam 6–8 sabse zyada bheed hogi.</p>'
  '<div style="display: flex; align-items: center; gap: 10px">%s<span style="font-size: 12.5px; color: %s">0:06 / 0:14</span></div></div></div>') % (SH, mascot('speaking', 60), GRN, wave(28, 20), INK3)
live = ('<div style="width: 592px; height: 64px; border-radius: 999px; background: %s; box-shadow: %s, 0 0 0 4px rgba(0,186,242,0.18); display: flex; align-items: center; gap: 14px; padding: 0 8px 0 10px">'
        '%s<span style="font-size: 15px; color: #FFFFFF; flex-grow: 1; white-space: nowrap"><span style="opacity: 0.6">…aadha kilo cheeni</span> aur ek Parle-G</span>%s'
        '<span style="height: 34px; padding: 0 12px; border-radius: 999px; background: rgba(255,255,255,0.12); color: #FFFFFF; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px">%sParle-G ×1 · ₹10</span>'
        '<span style="width: 48px; height: 48px; border-radius: 999px; background: %s; display: flex; align-items: center; justify-content: center"><span style="width: 14px; height: 14px; border-radius: 4px; background: %s"></span></span></div>') % (MID, SH2, orb(44), wave(14, 24, '#7DE8FF'), svg(I['check'], 14, 2.6), CYAN, MID)
annot = ('<div style="width: 300px; height: 150px; border-radius: 20px; background: #FFFFFF; box-shadow: %s; position: relative; overflow: hidden">'
  '<svg width="300" height="150" aria-hidden="true"><path d="M10 130 L60 118 L100 84 L150 76 L200 60 L290 40" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="100" cy="84" r="5" fill="#FFFFFF" stroke="%s" stroke-width="2.6"/></svg>'
  '<div style="position: absolute; left: 112px; top: 92px; padding: 6px 10px 6px 6px; border-radius: 12px; background: #FFFFFF; box-shadow: %s, inset 3px 0 0 %s; display: flex; align-items: center; gap: 8px; font-size: 12px">%s<span><b>₹1,240</b> Diwali order</span></div></div>') % (SH, MID, AMB, SH2, AMB, orb(20))
chips_ai = row(''.join(chip(orb(18, False) + t, '#FFFFFF', MID, 36, 13.5, 600) for t in ['Kal kya mangwaun?', 'Aage kyun hain?', 'Kis ka khata baaki?']), 8)
states_strip = row(''.join('<div style="display: flex; flex-direction: column; align-items: center; gap: 4px">%s<span style="font-size: 11.5px; color: %s">%s</span></div>' % (mascot(s, 56), INK3, l) for s, l in [('listening', 'Sun raha'), ('thinking', 'Soch raha'), ('speaking', 'Bol raha'), ('confirming', 'Haan chahiye')]), 18)

col1 = (sec('1 · Arth brief · bol ke batata hai', brief) + sec('2 · Live voice · jo suna, jo samjha', live) +
        sec('3 · Pipeline · kaam kis step par hai', '<div style="width: 592px">' + pipeline([('Stock ne dekha', '8:02', 'done'), ('Kharid ne poocha', '8:05', 'done'), ('Pehredaar', 'Budget OK', 'done'), ('Aapki haan', 'Intezaar', 'wait'), ('WhatsApp order', 'Baad mein', 'next')]) + '</div>') +
        sec('4 · Proactive nudge · bina poochhe', '<div style="width: 592px">' + nudge('Ek baat dekhi', 'Raat ke hisaab mein cash drawer ₹20 kam hai. 7:52 pm ka ₹120 bill shayad do baar likha gaya.', 'Dekho') + '</div>') +
        sec('5 · Undo · har khud-kiye kaam ke baad', undo_toast('Mehta ji ko reminder bheja', '0:24')))
col2 = (sec('6 · Andaaza with confidence', '<div style="width: 300px">' + confidence('Aaj raat tak', '₹8,200', '₹9,400', '₹10,800', 46, '8/10 sahi', [('Diwali 4 din door', '+₹1,100'), ('Guruvaar halka din', '−₹400'), ('Mehta ji ka order', '+₹1,240')]) + '</div>') +
        sec('7 · Chart par Arth ka note', annot))
col3 = (sec('8 · Arth ne seekha · aap sikhate ho', '<div style="width: 340px">' + learned('Priya Verma har guruvaar 500 ml doodh leti hain', '6 hafton mein 5 baar · bill par yaad dilaunga') + '</div>') +
        sec('9 · Draft with tone', '<div style="width: 356px">' + tone_draft('नमस्ते मेहता जी 🙏 आपका ₹2,150 बाक़ी है। सुविधा हो तो लिंक से UPI कर दीजिए।') + '</div>') +
        sec('10 · Provenance · har jawab ke neeche', '<div style="width: 340px">' + provenance(['214 bills', 'UPI ledger', '3 cash entries']) + '</div>') +
        sec('11 · Smart chips · screen ke hisaab se', '<div style="width: 340px; display: flex; flex-direction: column; gap: 8px">' + chips_ai + '</div>') +
        sec('12 · Mini orb · har AI cheez ka nishaan', row(orb(18) + orb(24) + orb(32) + orb(44) + ticker('Arth abhi', 'Rate le raha hai'), 12, 'align-items: center')))
body = (ttl('Arth AI layer', 'Woh components jo isse billing app se AI saathi banate hain: bolta hai, sunta hai, seekhta hai, poochhta hai, aur hisaab deta hai') +
        '<div style="display: flex; gap: 40px"><div style="display: flex; flex-direction: column; gap: 26px">%s</div><div style="display: flex; flex-direction: column; gap: 26px">%s%s</div><div style="display: flex; flex-direction: column; gap: 22px">%s</div></div>') % (col1, col2, sec('Mascot · kaam ke hisaab se', states_strip), col3)
open(OUT + 'AILayer.dc.html', 'w').write(board('Arth AI layer', body, 1440, 1060))

# ---------- MASCOT STATES BOARD ----------
st = [('idle', 'Taiyaar', 'Halki saans, aankhein khuli', CYAN), ('listening', 'Sun raha', 'Rings andar aati hain, aankhein badi', CYAN), ('thinking', 'Soch raha', 'Arc ghoomta hai, nazar upar', CYAN),
      ('speaking', 'Bol raha', 'Waveform awaaz ke saath', CYAN), ('confirming', 'Haan chahiye', 'Amber dashed ring', AMB), ('success', 'Ho gaya', 'Hari ring, muskaan', GRNF),
      ('alert', 'Dhyan do', 'Amber glow, badge', AMB), ('resting', 'Aaram', 'Aankhein band, glow kam', '#98A2B3'), ('offline', 'Offline', 'Grey, bina glow', '#98A2B3')]
cards = ''.join('<div style="background: #FFFFFF; border-radius: 22px; box-shadow: %s; padding: 18px 10px 16px; display: flex; flex-direction: column; align-items: center; gap: 10px">%s'
                '<div style="display: flex; align-items: center; gap: 8px">%s<span style="font-size: 15px; font-weight: 700">%s</span></div><span style="font-size: 12px; color: %s; text-align: center; line-height: 1.4">%s</span></div>' % (SH, mascot(s, 110), dot(c, 9), n, INK3, d) for s, n, d, c in st)
sizes = row(''.join('<div style="display: flex; flex-direction: column; align-items: center; gap: 6px">%s<span style="font-size: 11.5px; color: %s">%dpx</span></div>' % (mascot('idle', z), INK3, z) for z in (24, 34, 50, 80, 120)), 22, 'align-items: flex-end; flex-wrap: nowrap')
dark = '<div style="height: 170px; padding: 0 28px; border-radius: 24px; background: %s; display: flex; align-items: center; gap: 28px">%s%s%s<span style="font-size: 13px; color: #9FB3D1; max-width: 220px; line-height: 1.5">Dark surfaces par bhi wahi orb. Soundbox ki light isi rang mein jalti hai.</span></div>' % (MID, mascot('idle', 100), mascot('listening', 100), mascot('success', 100))
rules = ''.join('<div style="display: flex; gap: 10px; font-size: 13.5px; line-height: 1.5"><span style="width: 58px; flex-shrink: 0; color: %s; font-weight: 700">%s</span><span>%s</span></div>' % (CYT, a, b) for a, b in [
    ('Shape', 'Ek gola. Na haath, na antenna, na body. Sirf aankhein expression deti hain.'),
    ('Rang', 'Paytm blue se midnight tak. Amber aur hara sirf ring/glow mein, orb kabhi rang nahi badalta.'),
    ('Motion', '2–4 second ki dheemi saans. Reduce-motion mein sab ruk jaata hai, state ring se dikhti hai.'),
    ('Text', 'Har state ka label screen reader ko jaata hai: "Arth, listening".')])
body = (ttl('Arth orb · mascot', 'Glass orb with pill eyes. Saaf, shaant, Paytm ke rang mein. State ring aur aankhon se, kabhi cartoon se nahi') +
        '<div style="display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); gap: 12px">%s</div>'
        '<div style="display: flex; gap: 40px; align-items: flex-start">%s%s%s</div>') % (cards, sec('Sizes', sizes), sec('On midnight', dark), sec('Rules', '<div style="width: 330px; display: flex; flex-direction: column; gap: 8px">' + rules + '</div>'))
open(OUT + 'MascotStates.dc.html', 'w').write(board('Arth mascot states', body, 1440, 760))
print('ok')
