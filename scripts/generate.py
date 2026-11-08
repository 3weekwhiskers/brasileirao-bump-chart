#!/usr/bin/env python3
"""Generate a self-contained interactive bump/bar-chart-race HTML.

Reads data/{teams,coaches,meta,standings}.json and the images under assets/,
embeds everything, and writes dist/index.html. Team crests and coach photos
are optional: a club with no crest file falls back to a colour monogram badge,
and a coach with no photo falls back to initials.
Run scripts/compute_standings.py first to refresh data/standings.json.
"""
import json, os, base64, mimetypes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)

def data_uri(relpath):
    full = os.path.join(ROOT, relpath)
    if not relpath or not os.path.isfile(full):
        return ""
    mime = mimetypes.guess_type(full)[0] or "application/octet-stream"
    b64 = base64.b64encode(open(full, "rb").read()).decode()
    return f"data:{mime};base64,{b64}"

def main():
    teams_meta = {t["name"]: t for t in load("data/teams.json")["teams"]}
    coaches = load("data/coaches.json")
    meta = load("data/meta.json")
    st = load("data/standings.json")
    R = st["max_round"]
    dates = meta["round_dates"][:R]

    payload = {"R": R, "dates": dates, "season": meta["season"],
               "zones": meta["zone_lines"],
               "coaches_through": meta.get("coaches_current_through_round", R),
               "teams": []}
    for name in st["teams"]:
        tm = teams_meta[name]
        cs = []
        for c in coaches.get(name, []):
            cs.append({"n": c["name"], "s": c["short"], "from": c["from_round"],
                       "img": data_uri(c.get("photo", ""))})
        payload["teams"].append({
            "name": name, "mono": tm["monogram"], "ring": tm["badge_ring"],
            "tc": tm["badge_text"], "colors": tm["colors"],
            "crest": data_uri(tm.get("crest", "")),
            "pos": st["rank"][name], "pts": st["points"][name],
            "played": st["played"][name], "coaches": cs})
    js = json.dumps(payload, ensure_ascii=False)

    html = TEMPLATE.replace("__DATA__", js).replace("__SEASON__", meta["season"]) \
                   .replace("__THROUGH__", str(meta.get("coaches_current_through_round", R)))
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    out = os.path.join(ROOT, "dist/index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    kb = os.path.getsize(out) // 1024
    print(f"Wrote dist/index.html ({kb} KB) — {R} rounds, {len(payload['teams'])} teams.")

TEMPLATE = r'''<!DOCTYPE html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Brasileirão __SEASON__ — Corrida pela Tabela</title>
<style>
:root{--bg:#0E1117;--fg:#E6E9EF;--mute:#8B93A7}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:14px 12px 30px}
.top{display:flex;justify-content:space-between;align-items:flex-end;gap:10px}
h1{font-size:clamp(16px,3.4vw,24px);margin:0;font-weight:800}
.sub{color:var(--mute);font-size:clamp(10px,2.2vw,13px);margin:2px 0 10px}
.rdnum{font-size:clamp(17px,4.4vw,26px);font-weight:800;text-align:right}
.rddate{color:#9fb0c8;font-weight:700;font-size:clamp(11px,2.4vw,14px);text-align:right}
.leader{color:#57C77E;font-weight:700;font-size:clamp(10px,2.3vw,13px);text-align:right}
.chgline{color:#FF7A7A;font-weight:700;font-size:clamp(10px,2.2vw,12px);text-align:right;min-height:14px}
#chart{position:relative}
.zoneln{position:absolute;left:0;right:0;height:0;border-top:2px dashed #57C77E;opacity:.75;z-index:6;pointer-events:none}
.zoneln.releg{border-top-color:#E5484D}
.zoneln span{position:absolute;right:2px;top:-16px;font-size:10.5px;font-weight:800;letter-spacing:.3px;color:#57C77E;background:var(--bg);padding:0 5px}
.zoneln.releg span{color:#E5484D}
.row{position:absolute;left:0;right:0;height:var(--rh);display:flex;align-items:center;gap:6px;cursor:pointer;
  transition:transform .7s cubic-bezier(.4,0,.2,1),opacity .3s;will-change:transform}
.chart-dim .row{opacity:.5}
.chart-dim .row.on{opacity:1}
.row.on .tname{color:#fff}
.coaches{flex:0 0 auto;display:flex;align-items:center;gap:2px;width:92px;justify-content:flex-end}
.cav{position:relative;flex:0 0 auto;width:0;height:30px;opacity:0;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800;color:#fff;
  background:#3a4356;border:2px solid #566;overflow:hidden;background-size:cover;background-position:center;
  transition:width .5s cubic-bezier(.4,0,.2,1),opacity .5s,filter .4s}
.cav.show{width:30px;opacity:1;margin-left:1px}
.cav.active{border-color:#57C77E;box-shadow:0 0 0 1px #57C77E}
.cav.crossed{filter:grayscale(1) brightness(.55)}
.cav .xmark{position:absolute;inset:0;display:none;align-items:center;justify-content:center;color:#FF3B3B;font-size:21px;font-weight:900;text-shadow:0 0 2px #000}
.cav.crossed .xmark{display:flex}
@keyframes pulseNew{0%{box-shadow:0 0 0 0 rgba(255,196,75,.9)}70%{box-shadow:0 0 0 10px rgba(255,196,75,0)}100%{box-shadow:0 0 0 0 rgba(255,196,75,0)}}
@keyframes popNew{0%{transform:scale(1)}35%{transform:scale(1.28)}100%{transform:scale(1)}}
.cav.pulse{border-color:#FFC24B!important;z-index:5;animation:pulseNew .8s ease-out 6, popNew .55s ease-out 1}
.crest{flex:0 0 auto;width:30px;height:30px;border-radius:50%;background:#12161d center/cover no-repeat;border:1.5px solid #2b3346;display:flex;align-items:center;justify-content:center;font-size:8.5px;font-weight:800}
.tblock{flex:0 0 auto;width:120px;min-width:96px;text-align:right;line-height:1.05;overflow:hidden}
.tname{font-weight:800;font-size:clamp(11px,2.4vw,14px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tcoach{font-size:10px;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.track{flex:1;display:flex;align-items:center;min-width:0}
.bar{height:calc(var(--rh) - 12px);border-radius:6px;transition:width .7s cubic-bezier(.4,0,.2,1);min-width:2px;border:1.2px solid rgba(255,255,255,.28)}
.val{font-weight:800;font-size:clamp(11px,2.5vw,14px);margin-left:6px;white-space:nowrap}
.val .g{color:var(--mute);font-weight:700;font-size:.82em}
.controls{display:flex;align-items:center;gap:10px;margin-top:12px;flex-wrap:wrap}
button{background:#1b2330;color:var(--fg);border:1px solid #2b3446;border-radius:10px;padding:9px 15px;font-size:14px;font-weight:700;min-width:88px;cursor:pointer}
select{background:#1b2330;color:var(--fg);border:1px solid #2b3446;border-radius:10px;padding:9px 10px;font-size:13px;font-weight:700}
input[type=range]{flex:1;min-width:160px;accent-color:#57C77E;height:26px}
.key{display:flex;gap:14px;flex-wrap:wrap;color:var(--mute);font-size:11.5px;margin-top:8px;align-items:center}
.foot{color:var(--mute);font-size:11px;margin-top:10px;line-height:1.5}
</style></head><body><div class="wrap">
<div class="top"><div><h1>BRASILEIRÃO __SEASON__ — CORRIDA PELA TABELA</h1>
<div class="sub">Pontos acumulados, jogos disputados e trocas de treinador — rodada a rodada</div></div>
<div><div class="rdnum" id="rdnum">RODADA 1</div><div class="rddate" id="rddate"></div><div class="leader" id="leader"></div><div class="chgline" id="chg"></div></div></div>
<div id="chart"></div>
<div class="controls"><button id="play">▶ Play</button>
<input type="range" id="slider" min="1" max="1" value="1" step="1">
<select id="hlsel"><option value="">Destacar time…</option></select></div>
<div class="key"><span><span style="display:inline-block;width:14px;height:0;border-top:2px dashed #57C77E;vertical-align:middle;margin-right:4px"></span>G4 · Libertadores</span>
<span><span style="display:inline-block;width:14px;height:0;border-top:2px dashed #E5484D;vertical-align:middle;margin-right:4px"></span>Z4 · Rebaixamento</span>
<span>✕ = técnico substituído · toque num time p/ destacar</span></div>
<div class="foot">Barras nas cores de cada clube; comprimento = pontos. Entre parênteses, os jogos disputados. Ordem = classificação oficial. Camada de técnicos completa até a rodada __THROUGH__.</div>
</div>
<script>
const DATA=__DATA__;const R=DATA.R,T=DATA.teams,N=T.length,DATES=DATA.dates;
const chart=document.getElementById('chart');
const RH=Math.max(33,Math.min(46,Math.floor((Math.min(window.innerHeight-250,760))/N)));
chart.style.height=(RH*N)+'px';chart.style.setProperty('--rh',RH+'px');
let maxpts=0;T.forEach(t=>t.pts.forEach(p=>maxpts=Math.max(maxpts,p)));
const SCALE=maxpts*1.06;
function barBg(c){if(c.length===1)return c[0];
 if(c.length===2)return `linear-gradient(180deg,${c[0]} 0 50%,${c[1]} 50% 100%)`;
 return `linear-gradient(180deg,${c[0]} 0 33.3%,${c[1]} 33.3% 66.6%,${c[2]} 66.6% 100%)`;}
const z=DATA.zones;
const g4=document.createElement('div');g4.className='zoneln';g4.style.top=(z.libertadores_top*RH)+'px';g4.innerHTML='<span>G4 · LIBERTADORES</span>';chart.appendChild(g4);
const z4=document.createElement('div');z4.className='zoneln releg';z4.style.top=((N-z.relegation_bottom)*RH)+'px';z4.innerHTML='<span>Z4 · REBAIXAMENTO</span>';chart.appendChild(z4);
const hlsel=document.getElementById('hlsel');
[...T].sort((a,b)=>a.name.localeCompare(b.name)).forEach(t=>{const o=document.createElement('option');o.value=t.name;o.textContent=t.name;hlsel.appendChild(o);});
const rows=T.map((tm)=>{
 const row=document.createElement('div');row.className='row';row.style.setProperty('--rh',RH+'px');row.dataset.team=tm.name;
 const cav=tm.coaches.map(c=>`<div class="cav${c.img?' hasimg':''}" data-from="${c.from}" title="${c.n} (rodada ${c.from})" style="${c.img?`background-image:url(${c.img})`:''}">${c.img?'':(c.s[0]||'?')}<span class="xmark">✕</span></div>`).join('');
 const crestInner=tm.crest?'':`<span style="color:${tm.ring}">${tm.mono}</span>`;
 row.innerHTML=`<div class="coaches">${cav}</div>
   <div class="crest" style="${tm.crest?`background-image:url(${tm.crest})`:`background:${tm.colors[0]}`}">${crestInner}</div>
   <div class="tblock"><div class="tname">${tm.name}</div><div class="tcoach"></div></div>
   <div class="track"><div class="bar" style="background:${barBg(tm.colors)}"></div><span class="val"></span></div>`;
 chart.appendChild(row);
 row.addEventListener('click',()=>toggleHL(tm.name));
 return {row,bar:row.querySelector('.bar'),val:row.querySelector('.val'),tcoach:row.querySelector('.tcoach'),cavs:[...row.querySelectorAll('.cav')],tm};
});
let HL="";
function toggleHL(n){HL=(HL===n)?"":n;applyHL();}
function applyHL(){chart.classList.toggle('chart-dim',!!HL);rows.forEach(o=>o.row.classList.toggle('on',o.tm.name===HL));hlsel.value=HL;}
hlsel.addEventListener('change',()=>{HL=hlsel.value;applyHL();});
function coachAt(tm,r){let cur=tm.coaches[0];for(const c of tm.coaches)if(c.from<=r)cur=c;return cur;}
function changesAt(r){const o=[];T.forEach(tm=>tm.coaches.forEach((c,i)=>{if(i>0&&c.from===r)o.push({tm,c,prev:tm.coaches[i-1]});}));return o;}
function setRound(r){
 r=Math.max(1,Math.min(R,r));
 rows.forEach(o=>{
   const pos=o.tm.pos[r-1],pts=o.tm.pts[r-1],pj=o.tm.played[r-1];
   o.row.style.transform=`translateY(${(pos-1)*RH}px)`;
   o.bar.style.width=(pts/SCALE*100)+'%';
   o.val.innerHTML=`${pts} <span class="g">(${pj})</span>`;
   const act=coachAt(o.tm,r);o.tcoach.textContent=act?act.s:'';
   o.cavs.forEach(el=>{const cf=+el.dataset.from;el.classList.toggle('show',cf<=r);
     const isA=act&&(cf===act.from);el.classList.toggle('active',isA&&cf<=r);el.classList.toggle('crossed',cf<=r&&!isA);
     el.classList.toggle('pulse',isA&&cf>1&&(cf===r||cf===r-1));});
 });
 document.getElementById('rdnum').textContent='RODADA '+r;
 document.getElementById('rddate').textContent=DATES[r-1]||'';
 const ld=T.reduce((a,b)=>a.pos[r-1]<b.pos[r-1]?a:b);
 document.getElementById('leader').textContent='Líder: '+ld.name+' · '+ld.pts[r-1]+' pts';
 const ch=changesAt(r);
 document.getElementById('chg').textContent=ch.length?('Troca: '+ch.map(x=>x.tm.name+': '+x.prev.s+' → '+x.c.s).join('  ·  ')):'';
 slider.value=r;
}
const slider=document.getElementById('slider');slider.max=R;
slider.addEventListener('input',()=>{stop();setRound(+slider.value)});
let timer=null,cur=1,playing=false;
function play(){if(cur>R)cur=1;playing=true;document.getElementById('play').textContent='❚❚ Pause';setRound(cur);
 timer=setInterval(()=>{cur++;if(cur>R){stop();return;}setRound(cur);},900);}
function stop(){playing=false;if(timer)clearInterval(timer);timer=null;cur=+slider.value;document.getElementById('play').textContent='▶ Play';}
document.getElementById('play').addEventListener('click',()=>{playing?stop():play()});
window.__setRound=setRound;window.__changesAt=changesAt;
setRound(1);
</script></body></html>'''

if __name__ == "__main__":
    main()
