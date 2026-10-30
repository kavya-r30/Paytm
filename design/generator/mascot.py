# Arth orb mascot: glass orb in Paytm blues, two pill eyes, state carried by halo/ring + eye shape.
svg = r'''<svg width="{{w}}" height="{{h}}" viewBox="0 0 200 220" role="img" aria-label="{{label}}" style="overflow: visible">
  <defs>
    <radialGradient id="arthOrb" cx="0.36" cy="0.3" r="0.78">
      <stop offset="0" stop-color="#8FE3FF"></stop>
      <stop offset="0.34" stop-color="#1CB8EE"></stop>
      <stop offset="0.72" stop-color="#0A63B5"></stop>
      <stop offset="1" stop-color="#05295F"></stop>
    </radialGradient>
    <radialGradient id="arthOrbOff" cx="0.36" cy="0.3" r="0.78">
      <stop offset="0" stop-color="#F2F4F7"></stop>
      <stop offset="0.5" stop-color="#C3CAD5"></stop>
      <stop offset="1" stop-color="#7D8898"></stop>
    </radialGradient>
    <radialGradient id="arthHalo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0.62" stop-color="{{halo}}" stop-opacity="0.55"></stop>
      <stop offset="1" stop-color="{{halo}}" stop-opacity="0"></stop>
    </radialGradient>
    <filter id="arthSoft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"></feGaussianBlur></filter>
    <clipPath id="arthClip"><circle cx="100" cy="100" r="78"></circle></clipPath>
  </defs>

  <ellipse cx="100" cy="204" rx="50" ry="6.5" fill="#002E6E" opacity="0.14"></ellipse>
  <circle cx="100" cy="100" r="100" fill="url(#arthHalo)" opacity="{{haloOp}}">
    <animate attributeName="opacity" values="{{haloOp}};{{haloOp2}};{{haloOp}}" dur="3.6s" repeatCount="indefinite"></animate>
  </circle>

  <circle cx="100" cy="100" r="86" fill="none" stroke="#00BAF2" stroke-width="2" opacity="{{listenOp}}">
    <animate attributeName="r" values="80;98" dur="1.6s" repeatCount="indefinite"></animate>
    <animate attributeName="stroke-opacity" values="0.9;0" dur="1.6s" repeatCount="indefinite"></animate>
  </circle>
  <circle cx="100" cy="100" r="86" fill="none" stroke="#00BAF2" stroke-width="2" opacity="{{listenOp}}">
    <animate attributeName="r" values="80;98" dur="1.6s" begin="0.8s" repeatCount="indefinite"></animate>
    <animate attributeName="stroke-opacity" values="0.9;0" dur="1.6s" begin="0.8s" repeatCount="indefinite"></animate>
  </circle>

  <circle cx="100" cy="100" r="88" fill="none" stroke="{{ring}}" stroke-width="3.5" opacity="{{ringOp}}" stroke-dasharray="{{ringDash}}" stroke-linecap="round"></circle>

  <g opacity="{{thinkOp}}">
    <circle cx="100" cy="100" r="88" fill="none" stroke="#00BAF2" stroke-width="4" stroke-dasharray="62 491" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 100 100" to="360 100 100" dur="1.8s" repeatCount="indefinite"></animateTransform>
    </circle>
  </g>

  <circle cx="100" cy="100" r="78" fill="{{orbFill}}"></circle>
  <g clip-path="url(#arthClip)">
    <ellipse cx="100" cy="176" rx="64" ry="26" fill="{{aurora}}" opacity="{{auroraOp}}" filter="url(#arthSoft)">
      <animate attributeName="rx" values="60;70;60" dur="4s" repeatCount="indefinite"></animate>
    </ellipse>
    <ellipse cx="72" cy="50" rx="34" ry="18" fill="#FFFFFF" opacity="0.32" transform="rotate(-24 72 50)" filter="url(#arthSoft)"></ellipse>
  </g>
  <circle cx="100" cy="100" r="77.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="1"></circle>

  <g opacity="{{eyeOp}}" fill="{{eye}}">
    <rect x="{{eyeLX}}" y="{{eyeY}}" width="13" height="{{eyeH}}" rx="6.5">
      <animate attributeName="height" values="{{eyeH}};{{eyeH}};2;{{eyeH}};{{eyeH}}" keyTimes="0;0.9;0.93;0.96;1" dur="5s" repeatCount="indefinite"></animate>
      <animate attributeName="y" values="{{eyeY}};{{eyeY}};{{blinkY}};{{eyeY}};{{eyeY}}" keyTimes="0;0.9;0.93;0.96;1" dur="5s" repeatCount="indefinite"></animate>
    </rect>
    <rect x="{{eyeRX}}" y="{{eyeY}}" width="13" height="{{eyeH}}" rx="6.5">
      <animate attributeName="height" values="{{eyeH}};{{eyeH}};2;{{eyeH}};{{eyeH}}" keyTimes="0;0.9;0.93;0.96;1" dur="5s" repeatCount="indefinite"></animate>
      <animate attributeName="y" values="{{eyeY}};{{eyeY}};{{blinkY}};{{eyeY}};{{eyeY}}" keyTimes="0;0.9;0.93;0.96;1" dur="5s" repeatCount="indefinite"></animate>
    </rect>
  </g>

  <g fill="none" stroke="{{eye}}" stroke-width="6" stroke-linecap="round" opacity="{{happyOp}}">
    <path d="M77 100 q8 -12 16 0"></path><path d="M107 100 q8 -12 16 0"></path>
  </g>
  <g fill="none" stroke="{{eye}}" stroke-width="5" stroke-linecap="round" opacity="{{closedOp}}">
    <path d="M77 98 q8 7 16 0"></path><path d="M107 98 q8 7 16 0"></path>
  </g>

  <g fill="#FFFFFF" opacity="{{speakOp}}">
    <rect x="82" y="128" width="5" height="10" rx="2.5"><animate attributeName="height" values="6;14;6" dur="0.9s" repeatCount="indefinite"></animate><animate attributeName="y" values="130;126;130" dur="0.9s" repeatCount="indefinite"></animate></rect>
    <rect x="91" y="124" width="5" height="18" rx="2.5"><animate attributeName="height" values="18;8;18" dur="0.7s" repeatCount="indefinite"></animate><animate attributeName="y" values="124;129;124" dur="0.7s" repeatCount="indefinite"></animate></rect>
    <rect x="100" y="122" width="5" height="22" rx="2.5"><animate attributeName="height" values="10;22;10" dur="0.8s" repeatCount="indefinite"></animate><animate attributeName="y" values="128;122;128" dur="0.8s" repeatCount="indefinite"></animate></rect>
    <rect x="109" y="125" width="5" height="16" rx="2.5"><animate attributeName="height" values="16;7;16" dur="0.75s" repeatCount="indefinite"></animate><animate attributeName="y" values="125;129.5;125" dur="0.75s" repeatCount="indefinite"></animate></rect>
    <rect x="118" y="129" width="5" height="8" rx="2.5"><animate attributeName="height" values="8;13;8" dur="0.95s" repeatCount="indefinite"></animate><animate attributeName="y" values="129;126.5;129" dur="0.95s" repeatCount="indefinite"></animate></rect>
  </g>

  <g opacity="{{badgeOp}}">
    <circle cx="160" cy="40" r="17" fill="{{badge}}" stroke="#FFFFFF" stroke-width="4"></circle>
    <rect x="157.5" y="30" width="5" height="12" rx="2.5" fill="#FFFFFF"></rect>
    <circle cx="160" cy="48" r="2.8" fill="#FFFFFF"></circle>
  </g>
</svg>'''

script = r'''class Component extends DCLogic {
  renderVals() {
    var state = this.props.state || 'idle';
    var size = parseInt(this.props.size, 10);
    if (!size || size < 16) { size = 200; }
    var base = {
      halo: '#00BAF2', haloOp: 0.35, haloOp2: 0.6, ring: '#00BAF2', ringOp: 0, ringDash: 'none',
      listenOp: 0, thinkOp: 0, orbFill: 'url(#arthOrb)', aurora: '#7DE8FF', auroraOp: 0.6,
      eye: '#FFFFFF', eyeOp: 1, eyeLX: 79, eyeRX: 107, eyeY: 84, eyeH: 30,
      happyOp: 0, closedOp: 0, speakOp: 0, badgeOp: 0, badge: '#F5A524',
      label: 'Arth, ready'
    };
    var s = {
      idle: {},
      listening: { haloOp: 0.6, haloOp2: 0.9, listenOp: 1, eyeH: 34, eyeY: 82, label: 'Arth, listening' },
      thinking: { haloOp: 0.45, haloOp2: 0.7, thinkOp: 1, eyeLX: 86, eyeRX: 114, eyeY: 76, eyeH: 22, auroraOp: 0.95, label: 'Arth, thinking' },
      speaking: { haloOp: 0.5, haloOp2: 0.85, eyeY: 74, eyeH: 26, speakOp: 1, label: 'Arth, speaking' },
      confirming: { halo: '#F5A524', haloOp: 0.4, haloOp2: 0.7, ring: '#F5A524', ringOp: 1, ringDash: '10 9', eyeY: 82, eyeH: 30, label: 'Arth, waiting for your haan' },
      success: { halo: '#12B76A', haloOp: 0.5, haloOp2: 0.8, ring: '#12B76A', ringOp: 1, eyeOp: 0, happyOp: 1, label: 'Arth, done' },
      alert: { halo: '#F5A524', haloOp: 0.5, haloOp2: 0.85, eyeY: 90, eyeH: 20, badgeOp: 1, label: 'Arth, needs attention' },
      resting: { haloOp: 0.12, haloOp2: 0.18, eyeOp: 0, closedOp: 1, auroraOp: 0.35, label: 'Arth, resting' },
      offline: { halo: '#98A2B3', haloOp: 0.1, haloOp2: 0.1, orbFill: 'url(#arthOrbOff)', aurora: '#FFFFFF', auroraOp: 0.2, eyeOp: 0, closedOp: 1, eye: '#F2F4F7', label: 'Arth, offline' }
    };
    var v = Object.assign({}, base, s[state] || {});
    v.blinkY = v.eyeY + v.eyeH / 2 - 1;
    v.w = size;
    v.h = Math.round(size * 1.1);
    return v;
  }
}'''

html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>Arth mascot</title>\n<script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n<style>\nbody{margin:0}\n</style>\n</helmet>\n'
        '<div style="width: {{w}}px; height: {{h}}px; display: flex; align-items: center; justify-content: center">\n' + svg + '\n</div>\n</x-dc>\n'
        '<script type="text/x-dc" data-dc-script data-props=\'{"state":{"editor":"enum","options":["idle","listening","thinking","speaking","confirming","success","alert","resting","offline"],"default":"idle"},"size":{"editor":"int","min":16,"max":400,"default":200},"$preview":{"width":200,"height":220}}\'>\n'
        + script + '\n</script>\n</body>\n</html>\n')
open('/home/claude/design/project/Mascot.dc.html', 'w').write(html)

# Static preview renderer (substitutes template values) for local checks
import re, json
def render(state, size):
    import subprocess
    js = script.replace('class Component extends DCLogic', 'class C').replace('this.props', 'P')
    out = subprocess.run(['node', '-e', js + '; var P=' + json.dumps({'state': state, 'size': size}) + '; console.log(JSON.stringify(new C().renderVals.call({props:P})))'], capture_output=True, text=True).stdout
    v = json.loads(out)
    return re.sub(r'\{\{(\w+)\}\}', lambda m: str(v[m.group(1)]), svg).replace('id="arth', 'id="a%s' % state).replace('#arth', '#a%s' % state)
if __name__ == '__main__':
    states = ['idle', 'listening', 'thinking', 'speaking', 'confirming', 'success', 'alert', 'resting', 'offline']
    page = '<body style="margin:0;background:#F5F7FA;display:flex;flex-wrap:wrap;gap:20px;padding:20px;width:1160px">' + ''.join('<div style="background:#fff;border-radius:20px;padding:10px">%s</div>' % render(s, 200) for s in states) + ''.join('<div style="background:#fff;border-radius:12px;padding:6px">%s</div>' % render('idle', z) for z in (34, 50, 80)) + '</body>'
    open('/tmp/mascot_prev.html', 'w').write(page)
