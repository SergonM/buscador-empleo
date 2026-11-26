"""Genera docs/index.html: página estática para celular (PWA instalable) con seguimiento de postulaciones.

Todo lo que marca Sergio (guardada, postulé, entrevista, notas) vive en el navegador (localStorage):
no hay servidor ni cuentas. Desde "Mi lista" se puede copiar un respaldo y restaurarlo en otro equipo.
"""
import json

PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f766e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Ofertas">
<title>Mis ofertas de empleo</title>
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icono.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icono-192.png">
<style>
:root{--bg:#f6f7f9;--card:#fff;--tx:#14171a;--mut:#5b6470;--line:#e3e6ea;--acc:#0f766e;--acc-bg:#e6f4f2;--new:#b45309;--new-bg:#fdf1e3;--ok:#15803d;--ok-bg:#e7f6ec;--bad:#b91c1c;--bad-bg:#fdecec;--blue:#1d4ed8;--blue-bg:#e8efff}
@media (prefers-color-scheme:dark){:root{--bg:#0e1114;--card:#171b20;--tx:#e8ebee;--mut:#9aa3ad;--line:#2a3038;--acc:#2dd4bf;--acc-bg:#11302c;--new:#fbbf24;--new-bg:#3a2a0d;--ok:#4ade80;--ok-bg:#12301d;--bad:#f87171;--bad-bg:#3a1414;--blue:#93b4ff;--blue-bg:#16234a}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{position:sticky;top:0;z-index:3;background:var(--bg);padding:calc(12px + env(safe-area-inset-top)) 16px 8px;border-bottom:1px solid var(--line)}
.fila{display:flex;align-items:center;gap:8px}
h1{font-size:20px;margin:0;flex:1}
.sub{color:var(--mut);font-size:13px;margin-top:2px}
.tabs,.chips{display:flex;gap:8px;overflow-x:auto;padding-top:10px;scrollbar-width:none}
.tabs::-webkit-scrollbar,.chips::-webkit-scrollbar{display:none}
button{font:inherit;color:inherit;cursor:pointer}
.t,.c{flex:0 0 auto;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:7px 13px;font-size:14px}
.t[aria-pressed=true],.c[aria-pressed=true]{background:var(--acc);border-color:var(--acc);color:#fff}
.t b{font-weight:600;opacity:.8;margin-left:3px}
.buscar{display:flex;gap:8px;margin-top:10px}
input[type=search],select,textarea{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--tx);font:inherit}
select{width:auto;flex:1;min-width:0;font-size:14px;padding:8px}
.btn-f{flex:0 0 auto;border:1px solid var(--line);background:var(--card);border-radius:10px;padding:0 12px;font-size:14px}
.btn-f[aria-expanded=true]{border-color:var(--acc);color:var(--acc)}
#filtros{display:none;gap:8px;margin-top:8px;flex-wrap:wrap}
#filtros.on{display:flex}
#filtros label{display:flex;align-items:center;gap:6px;font-size:14px;color:var(--mut)}
main{padding:12px 16px 40px;max-width:720px;margin:0 auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px}
.card.marcada{border-color:var(--acc)}
.top{display:flex;gap:10px;align-items:flex-start}
.score{flex:0 0 auto;min-width:46px;text-align:center;font-weight:700;font-size:15px;color:var(--acc);background:var(--acc-bg);border-radius:10px;padding:6px 4px}
.score small{display:block;font-weight:500;font-size:10px;color:var(--mut)}
h2{font-size:16px;margin:0;line-height:1.3}
.emp{color:var(--mut);font-size:14px;margin-top:2px}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 8px;font-size:12.5px}
.meta span{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:2px 7px;color:var(--mut)}
.meta .nv{background:var(--new-bg);color:var(--new);border-color:transparent;font-weight:600}
.meta .st{background:var(--blue-bg);color:var(--blue);border-color:transparent;font-weight:600}
.why{font-size:14px;margin:0 0 10px}
.acciones{display:flex;gap:8px}
a.ver{flex:1;display:block;text-align:center;background:var(--acc);color:#fff;text-decoration:none;border-radius:10px;padding:10px;font-weight:600}
.ico{flex:0 0 auto;width:44px;border:1px solid var(--line);background:var(--card);border-radius:10px;font-size:18px}
.ico[aria-pressed=true]{background:var(--acc-bg);border-color:var(--acc)}
.estados{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.estados button{border:1px solid var(--line);background:var(--bg);border-radius:8px;padding:6px 9px;font-size:13px}
.estados button[aria-pressed=true]{background:var(--blue-bg);border-color:var(--blue);color:var(--blue);font-weight:600}
.estados button.no[aria-pressed=true]{background:var(--bad-bg);border-color:var(--bad);color:var(--bad)}
.prep{border-top:1px dashed var(--line);margin-top:12px;padding-top:10px;font-size:14px}
.prep h3{font-size:13px;text-transform:uppercase;letter-spacing:.03em;color:var(--mut);margin:12px 0 6px}
.prep h3:first-child{margin-top:0}
.kw{display:flex;flex-wrap:wrap;gap:6px}
.kw span{border-radius:6px;padding:2px 8px;font-size:13px;background:var(--ok-bg);color:var(--ok)}
.kw.ref span{background:var(--new-bg);color:var(--new)}
textarea{min-height:170px;font-size:14px;line-height:1.4;resize:vertical}
textarea.nota{min-height:60px}
.mini{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.mini button,.mini a{border:1px solid var(--line);background:var(--bg);border-radius:8px;padding:6px 10px;font-size:13px;color:var(--tx);text-decoration:none}
.aviso{background:var(--new-bg);color:var(--new);border-radius:8px;padding:6px 9px;font-size:13px;margin-top:8px}
.vacio{color:var(--mut);text-align:center;padding:40px 10px}
.resumen{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}
.resumen div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px;text-align:center}
.resumen b{display:block;font-size:20px}
.resumen small{color:var(--mut);font-size:11.5px}
details.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:18px 0 12px;font-size:14px}
details.panel summary{font-weight:600;cursor:pointer}
table{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}
td,th{padding:5px 4px;border-bottom:1px solid var(--line);text-align:left}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.okk{color:var(--ok)}.mal{color:var(--bad)}
footer{color:var(--mut);font-size:12px;text-align:center;padding:0 16px 30px}
footer a{color:var(--mut)}
#toast{position:fixed;left:50%;bottom:calc(20px + env(safe-area-inset-bottom));transform:translateX(-50%);background:var(--tx);color:var(--bg);padding:9px 16px;border-radius:999px;font-size:14px;opacity:0;transition:opacity .2s;pointer-events:none;z-index:5}
#toast.on{opacity:1}
</style>
</head>
<body>
<header>
  <div class="fila"><h1>Ofertas para Sergio</h1><button class="btn-f" id="instalar" hidden>Instalar</button></div>
  <div class="sub" id="sub"></div>
  <div class="tabs" role="group" aria-label="Vista">
    <button class="t" data-v="nuevas">Nuevas<b id="n-nuevas"></b></button>
    <button class="t" data-v="todas">Todas<b id="n-todas"></b></button>
    <button class="t" data-v="lista">Mi lista<b id="n-lista"></b></button>
  </div>
  <div class="chips" id="chips" role="group" aria-label="Área"></div>
  <div class="buscar">
    <input id="q" type="search" placeholder="Buscar cargo, empresa o palabra" autocomplete="off">
    <button class="btn-f" id="btn-filtros" aria-expanded="false" aria-controls="filtros">Filtros</button>
  </div>
  <div id="filtros">
    <select id="f-mod" aria-label="Modalidad"><option value="">Toda modalidad</option><option value="remoto">Remoto</option><option value="hibrido">Híbrido</option><option value="presencial">Presencial / no indica</option></select>
    <select id="f-fuente" aria-label="Fuente"><option value="">Toda fuente</option></select>
    <select id="f-orden" aria-label="Orden"><option value="encaje">Mejor encaje</option><option value="fecha">Más recientes</option><option value="calidad">Mejor calidad</option></select>
    <label><input type="checkbox" id="f-junior"> Solo junior / práctica</label>
    <label><input type="checkbox" id="f-ingles"> Sin inglés obligatorio</label>
  </div>
</header>
<main id="lista"></main>
<main id="extra" style="padding-top:0"></main>
<footer id="pie"></footer>
<div id="toast" role="status"></div>
<script>
const DATOS = __DATOS__;
const R = DATOS.resumen, O = DATOS.ofertas, P = DATOS.perfil || {};
const AREAS = ["Datos / ML","Negocio / Producto","Ciberseguridad / GRC"];
const ESTADOS = [["guardada","☆ Guardar"],["postulada","✓ Postulé"],["entrevista","💬 Entrevista"],["oferta","🎉 Oferta"],["descartada","✕ No me interesa"]];
const NOMBRE_EST = {guardada:"Guardada",postulada:"Postulada",entrevista:"Entrevista",oferta:"Oferta",descartada:"Descartada"};
const LS = "buscador-empleo-v1";
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const MES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
const fmt = d => { if(!d) return ""; const [y,m,dd]=d.split("-"); return `${+dd} ${MES[m-1]}`; };
const hoyISO = () => new Date(Date.now()-5*3600e3).toISOString().slice(0,10);
const dias = d => d ? Math.round((new Date(hoyISO()) - new Date(d))/864e5) : 0;
const norm = s => String(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();

// ---------- Estado guardado en el navegador ----------
let M = {};
try { M = JSON.parse(localStorage.getItem(LS) || "{}") || {}; } catch(e) { M = {}; }
const guardar = () => { try { localStorage.setItem(LS, JSON.stringify(M)); } catch(e) {} };
const POR_ID = Object.fromEntries(O.map(o => [o.id, o]));
// Las ofertas marcadas guardan una copia para no perderlas cuando salgan del listado.
function marcar(id, estado){
  const o = POR_ID[id] || (M[id] && M[id].o);
  const prev = M[id] || {};
  if (prev.estado === estado) { delete prev.estado; } else { prev.estado = estado; prev.cuando = hoyISO(); }
  if (o) prev.o = {id:o.id,titulo:o.titulo,empresa:o.empresa,url:o.url,fuente:o.fuente,modalidad:o.modalidad,fecha:o.fecha,puntaje:o.puntaje,por_que:o.por_que,areas:o.areas||[],claves:o.claves||[],reforzar:o.reforzar||[],idioma:o.idioma||"es",salario:o.salario||"",seniority:o.seniority||""};
  if (!prev.estado && !prev.nota) delete M[id]; else M[id] = prev;
  guardar();
}
const estadoDe = id => (M[id] && M[id].estado) || "";

// ---------- Textos de ayuda para postular ----------
function carta(o){
  const kw = (o.claves||[]).slice(0,3);
  const area = (o.areas||[])[0] || "";
  const en = o.idioma === "en";
  const nombre = P.nombre || "Sergio González";
  if (en) {
    const puente = {"Datos / ML":"turning data into decisions","Negocio / Producto":"connecting business needs with technology","Ciberseguridad / GRC":"risk, controls and compliance in a regulated environment"}[area] || "learning fast and delivering";
    return `Hello ${o.empresa} team,\n\nI am applying for the ${o.titulo} role. I am a Systems and Computing Engineer from Universidad de los Andes (Bogotá) and I am currently an intern in Health Care Compliance at Johnson & Johnson, where I work every day with ${area==="Ciberseguridad / GRC"?"controls, policies and regulatory requirements":"processes, data and stakeholders in a highly regulated company"}.\n\nI am excited about this role because it combines my engineering background with ${puente}.${kw.length?` I bring hands-on experience with ${kw.join(", ")}.`:""} I communicate fluently in English and Spanish.\n\nI would love to talk about how I can contribute. My resume is attached.\n\nBest regards,\n${nombre}`;
  }
  const puente = {"Datos / ML":"convertir datos en decisiones","Negocio / Producto":"conectar las necesidades del negocio con la tecnología","Ciberseguridad / GRC":"el riesgo, los controles y el cumplimiento en entornos regulados"}[area] || "aprender rápido y entregar resultados";
  return `Hola, equipo de ${o.empresa}:\n\nMe interesa la posición de ${o.titulo}. Soy Ingeniero de Sistemas y Computación de la Universidad de los Andes y actualmente hago mi práctica en Health Care Compliance en Johnson & Johnson, donde trabajo a diario con ${area==="Ciberseguridad / GRC"?"controles, políticas y requisitos regulatorios":"procesos, datos y distintas áreas de una compañía altamente regulada"}.\n\nEl cargo me motiva porque une mi formación de ingeniero con ${puente}.${kw.length?` Tengo experiencia práctica con ${kw.join(", ")}.`:""} Hablo inglés a nivel profesional.\n\nMe encantaría conversar sobre cómo puedo aportar. Adjunto mi hoja de vida.\n\nSaludos,\n${nombre}`;
}
function mensajeReclutador(o){
  return o.idioma === "en"
    ? `Hi! I just applied to ${o.titulo} at ${o.empresa}. I'm a Systems Engineer (Uniandes) interning in Health Care Compliance at J&J, and the role fits my profile well. Would you be open to a quick chat? Thanks!`
    : `¡Hola! Acabo de postularme a ${o.titulo} en ${o.empresa}. Soy Ingeniero de Sistemas (Uniandes) y hago mi práctica en Health Care Compliance en J&J; el cargo encaja muy bien con mi perfil. ¿Podríamos conversar unos minutos? ¡Gracias!`;
}

// ---------- Filtros y vista ----------
let vista = ""; try { vista = localStorage.getItem(LS+"-vista") || ""; } catch(e) {}
if (!["nuevas","todas","lista"].includes(vista)) vista = R.nuevas ? "nuevas" : "todas";
let area = "", q = "";
const F = {mod:"", fuente:"", orden:"encaje", junior:false, sinIngles:false};
const abiertas = new Set();
const fuentes = [...new Set(O.map(o => o.fuente))].sort();
$("#f-fuente").innerHTML += fuentes.map(f => `<option>${esc(f)}</option>`).join("");
$("#chips").innerHTML = [["","Todas las áreas"],...AREAS.map(a=>[a,a])].map(([v,l]) => `<button class="c" data-a="${esc(v)}">${esc(l)}</button>`).join("");
const act = new Date(R.actualizado);
$("#sub").textContent = `${R.nuevas} nuevas hoy · ${R.mostradas} activas · actualizado ${act.toLocaleString("es-CO",{day:"numeric",month:"short",hour:"numeric",minute:"2-digit"})}`;

function modalidadDe(o){ const m = norm(o.modalidad); return m.includes("remoto") ? "remoto" : m.includes("hibrido") ? "hibrido" : "presencial"; }
function esJunior(o){ return /junior|jr\b|trainee|practica|practicante|pasante|intern|aprendiz|entry|graduate|sin experiencia/.test(norm(o.titulo+" "+o.seniority+" "+o.por_que)); }

function pasa(o){
  if (area && !(o.areas||[]).includes(area)) return false;
  if (F.mod && modalidadDe(o) !== F.mod) return false;
  if (F.fuente && o.fuente !== F.fuente) return false;
  if (F.junior && !esJunior(o)) return false;
  if (F.sinIngles && o.idioma === "en") return false;
  if (q) { const t = norm(o.titulo+" "+o.empresa+" "+o.por_que+" "+(o.claves||[]).join(" ")+" "+(o.reforzar||[]).join(" ")); if (!norm(q).split(/\s+/).every(p => t.includes(p))) return false; }
  return true;
}
const ORDEN = {encaje:(a,b)=>b.puntaje-a.puntaje||(b.fecha||"").localeCompare(a.fecha||""), fecha:(a,b)=>(b.fecha||"").localeCompare(a.fecha||"")||b.puntaje-a.puntaje, calidad:(a,b)=>(b.calidad||0)-(a.calidad||0)||b.puntaje-a.puntaje};

function tarjeta(o){
  const st = estadoDe(o.id), m = M[o.id] || {};
  const abierta = abiertas.has(o.id);
  const caduca = !POR_ID[o.id];
  const seguimiento = st === "postulada" && dias(m.cuando) >= 7;
  const calidad = o.calidad != null ? (o.calidad >= 70 ? "Oferta completa" : o.calidad < 45 ? "Poca información" : "") : "";
  return `<article class="card${st&&st!=="descartada"?" marcada":""}" data-id="${esc(o.id)}">
    <div class="top"><div class="score">${o.puntaje}<small>encaje</small></div>
      <div><h2>${esc(o.titulo)}</h2><div class="emp">${esc(o.empresa||"Empresa sin nombre")}</div></div></div>
    <div class="meta">${st?`<span class="st">${NOMBRE_EST[st]}${m.cuando?" · "+fmt(m.cuando):""}</span>`:""}${o.nueva&&!st?'<span class="nv">Nueva</span>':""}<span>${esc(o.fuente)}</span><span>${esc(o.modalidad)}</span>${o.fecha?`<span>${fmt(o.fecha)}</span>`:""}${o.seniority?`<span>${esc(o.seniority)}</span>`:""}${o.salario?`<span>${esc(o.salario)}</span>`:""}${o.idioma==="en"?"<span>En inglés</span>":""}${calidad?`<span>${calidad}</span>`:""}${caduca?"<span>Ya no aparece en las fuentes</span>":""}</div>
    <p class="why">${esc(o.por_que)}</p>
    ${seguimiento?`<div class="aviso">Te postulaste hace ${dias(m.cuando)} días: buen momento para hacer seguimiento con un mensaje corto.</div>`:""}
    <div class="acciones">
      <a class="ver" href="${esc(o.url)}" target="_blank" rel="noopener">Ver oferta en ${esc(o.fuente)}</a>
      <button class="ico" data-acc="guardada" aria-pressed="${st==="guardada"}" aria-label="Guardar">${st==="guardada"?"★":"☆"}</button>
      <button class="ico" data-acc="prep" aria-pressed="${abierta}" aria-label="Preparar postulación">✍️</button>
    </div>
    ${abierta ? preparar(o, st, m) : ""}
  </article>`;
}
function preparar(o, st, m){
  const emp = encodeURIComponent(o.empresa||"");
  return `<div class="prep">
    <h3>Estado</h3>
    <div class="estados">${ESTADOS.map(([k,l]) => `<button data-acc="${k}" class="${k==="descartada"?"no":""}" aria-pressed="${st===k}">${l}</button>`).join("")}</div>
    ${(o.claves||[]).length ? `<h3>Ya tienes · ponlas en tu hoja de vida</h3><div class="kw">${o.claves.map(k=>`<span>${esc(k)}</span>`).join("")}</div>` : ""}
    ${(o.reforzar||[]).length ? `<h3>La oferta también pide · menciónalas si las has usado</h3><div class="kw ref">${o.reforzar.map(k=>`<span>${esc(k)}</span>`).join("")}</div>` : ""}
    <h3>Carta breve (edítala antes de enviar)</h3>
    <textarea data-campo="carta">${esc(m.carta || carta(o))}</textarea>
    <div class="mini"><button data-acc="copiar-carta">Copiar carta</button><button data-acc="copiar-msg">Copiar mensaje para reclutador</button></div>
    <h3>Investiga la empresa</h3>
    <div class="mini">
      <a href="https://www.linkedin.com/search/results/companies/?keywords=${emp}" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://www.linkedin.com/search/results/people/?keywords=${emp}%20recruiter" target="_blank" rel="noopener">Reclutadores</a>
      <a href="https://www.glassdoor.com/Search/results.htm?keyword=${emp}" target="_blank" rel="noopener">Opiniones (Glassdoor)</a>
      <a href="https://www.google.com/search?q=${emp}%20empresa%20Colombia" target="_blank" rel="noopener">Google</a>
    </div>
    <h3>Mis notas</h3>
    <textarea class="nota" data-campo="nota" placeholder="Contacto, fecha de entrevista, salario conversado…">${esc(m.nota||"")}</textarea>
  </div>`;
}

function contarLista(){ return Object.values(M).filter(m => m.estado && m.estado !== "descartada").length; }

function pintar(){
  document.querySelectorAll(".t").forEach(b => b.setAttribute("aria-pressed", b.dataset.v===vista));
  document.querySelectorAll(".c").forEach(b => b.setAttribute("aria-pressed", b.dataset.a===area));
  const visibles = O.filter(o => estadoDe(o.id) !== "descartada");
  $("#n-nuevas").textContent = visibles.filter(o=>o.nueva).length;
  $("#n-todas").textContent = visibles.length;
  $("#n-lista").textContent = contarLista();
  let l, html = "";
  if (vista === "lista") {
    const marcadas = Object.entries(M).filter(([id,m]) => m.estado).map(([id,m]) => ({...(m.o||{}), ...(POR_ID[id]||{}), id}));
    const cuenta = k => marcadas.filter(o => estadoDe(o.id)===k).length;
    html += `<div class="resumen"><div><b>${cuenta("guardada")}</b><small>Guardadas</small></div><div><b>${cuenta("postulada")}</b><small>Postulé</small></div><div><b>${cuenta("entrevista")}</b><small>Entrevistas</small></div><div><b>${cuenta("oferta")}</b><small>Ofertas</small></div></div>`;
    const rango = {entrevista:0,oferta:0,postulada:1,guardada:2,descartada:3};
    l = marcadas.filter(pasa).sort((a,b) => rango[estadoDe(a.id)]-rango[estadoDe(b.id)] || (M[b.id].cuando||"").localeCompare(M[a.id].cuando||""));
    html += l.length ? l.map(tarjeta).join("") : `<div class="vacio">Aún no has marcado ofertas. Toca ☆ para guardar una, o ✍️ para preparar la postulación y marcar “Postulé”.</div>`;
  } else {
    l = visibles.filter(o => (vista==="todas" || o.nueva) && pasa(o)).sort(ORDEN[F.orden]);
    html = l.length ? l.map(tarjeta).join("") : `<div class="vacio">${vista==="nuevas"?"Hoy no hay ofertas nuevas con estos filtros. Mira la pestaña “Todas”.":"No hay ofertas con estos filtros."}</div>`;
  }
  $("#lista").innerHTML = html;
  pintarExtra();
}

function pintarExtra(){
  const est = R.estado_fuentes || {};
  const filas = Object.entries(est).map(([f,e]) => `<tr><td>${esc(f)}</td><td class="n">${e.ofertas}</td><td class="n">${e.segundos ?? ""} s</td><td class="${e.ok?"okk":"mal"}">${e.ok?"OK":"Falló"}${e.error?": "+esc(e.error):""}</td></tr>`).join("");
  const desc = Object.entries(R.descartes||{}).map(([k,n]) => `<tr><td>${esc(k)}</td><td class="n">${n}</td></tr>`).join("");
  const hist = (R.historia||[]).slice(-14).map(h => `<tr><td>${fmt(h.fecha)}</td><td class="n">${h.revisadas}</td><td class="n">${h.nuevas}</td><td class="n">${h.mostradas}</td></tr>`).join("");
  $("#extra").innerHTML = `
  <details class="panel"><summary>Cómo fue la búsqueda de hoy</summary>
    <p>${R.revisadas} ofertas revisadas en ${Object.keys(est).length} fuentes, ${R.mostradas} pasan tus filtros${R.duracion?` · ${R.duracion} s`:""}.</p>
    ${filas?`<table><tr><th>Fuente</th><th>Ofertas</th><th>Tiempo</th><th>Estado</th></tr>${filas}</table>`:""}
    ${desc?`<h3 style="font-size:14px;margin:14px 0 0">Por qué se descartaron</h3><table>${desc}</table>`:""}
    ${hist?`<h3 style="font-size:14px;margin:14px 0 0">Últimos días</h3><table><tr><th>Día</th><th>Revisadas</th><th>Nuevas</th><th>Activas</th></tr>${hist}</table>`:""}
  </details>
  <details class="panel"><summary>Respaldo de mi lista</summary>
    <p>Tus marcas y notas se guardan solo en este navegador. Copia el respaldo para pasarlas a otro equipo o no perderlas.</p>
    <div class="mini"><button data-acc="exportar">Copiar respaldo</button><button data-acc="importar">Pegar respaldo</button></div>
  </details>`;
  $("#pie").innerHTML = `Fuentes: ${fuentes.map(esc).join(", ")}. Cada oferta enlaza a su publicación original (Get on Board, Remotive, Himalayas, Jobicy, Remote OK y portales de cada empresa). <a href="https://github.com/SergonM/buscador-empleo">Código</a>`;
}

let toastT;
function toast(t){ const e=$("#toast"); e.textContent=t; e.classList.add("on"); clearTimeout(toastT); toastT=setTimeout(()=>e.classList.remove("on"),1800); }
async function copiar(t){ try { await navigator.clipboard.writeText(t); toast("Copiado"); } catch(e) { prompt("Copia el texto:", t); } }

document.querySelector(".tabs").onclick = e => { const b=e.target.closest("button"); if(b){vista=b.dataset.v; try{localStorage.setItem(LS+"-vista",vista);}catch(_){} pintar(); scrollTo(0,0);} };
$("#chips").onclick = e => { const b=e.target.closest("button"); if(b){area=b.dataset.a; pintar();} };
$("#q").oninput = e => { q=e.target.value.trim(); pintar(); };
$("#btn-filtros").onclick = e => { const on = $("#filtros").classList.toggle("on"); e.currentTarget.setAttribute("aria-expanded", on); };
$("#f-mod").onchange = e => { F.mod=e.target.value; pintar(); };
$("#f-fuente").onchange = e => { F.fuente=e.target.value; pintar(); };
$("#f-orden").onchange = e => { F.orden=e.target.value; pintar(); };
$("#f-junior").onchange = e => { F.junior=e.target.checked; pintar(); };
$("#f-ingles").onchange = e => { F.sinIngles=e.target.checked; pintar(); };

document.body.addEventListener("click", e => {
  const b = e.target.closest("[data-acc]"); if (!b) return;
  const acc = b.dataset.acc, card = b.closest(".card"), id = card && card.dataset.id;
  const o = id && (POR_ID[id] || (M[id]||{}).o);
  if (acc === "prep") { abiertas.has(id) ? abiertas.delete(id) : abiertas.add(id); pintar(); return; }
  if (NOMBRE_EST[acc]) { marcar(id, acc); toast(estadoDe(id) ? NOMBRE_EST[acc] : "Quitada de tu lista"); pintar(); return; }
  if (acc === "copiar-carta") return copiar(card.querySelector("[data-campo=carta]").value);
  if (acc === "copiar-msg") return copiar(mensajeReclutador(o));
  if (acc === "exportar") return copiar(JSON.stringify(M));
  if (acc === "importar") {
    const t = prompt("Pega aquí el respaldo:"); if (!t) return;
    try { const d = JSON.parse(t); if (typeof d !== "object" || !d) throw 0; Object.assign(M, d); guardar(); toast("Respaldo restaurado"); pintar(); } catch(_) { toast("Ese texto no es un respaldo válido"); }
  }
});
document.body.addEventListener("input", e => {
  const c = e.target.dataset.campo; if (!c) return;
  const id = e.target.closest(".card").dataset.id, o = POR_ID[id] || (M[id]||{}).o;
  const m = M[id] || {}; m[c] = e.target.value;
  if (o && !m.o) m.o = {id:o.id,titulo:o.titulo,empresa:o.empresa,url:o.url,fuente:o.fuente,modalidad:o.modalidad,fecha:o.fecha,puntaje:o.puntaje,por_que:o.por_que,areas:o.areas||[],claves:o.claves||[],reforzar:o.reforzar||[],idioma:o.idioma||"es"};
  M[id] = m; guardar();
});

// ---------- App instalable (PWA) ----------
if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(()=>{}));
let pedirInstalar;
addEventListener("beforeinstallprompt", e => { e.preventDefault(); pedirInstalar = e; $("#instalar").hidden = false; });
$("#instalar").onclick = async () => { if (!pedirInstalar) return; pedirInstalar.prompt(); await pedirInstalar.userChoice; pedirInstalar = null; $("#instalar").hidden = true; };

pintar();
</script>
</body>
</html>
"""

MANIFIESTO = {
    "name": "Ofertas de empleo de Sergio",
    "short_name": "Ofertas",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#f6f7f9",
    "theme_color": "#0f766e",
    "lang": "es",
    "icons": [
        {"src": "icono-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icono-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icono-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

# Red primero (para ver siempre lo de hoy) y copia guardada si no hay señal.
SERVICE_WORKER = """const C = "ofertas-v1";
self.addEventListener("install", e => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => { const copia = r.clone(); caches.open(C).then(c => c.put(e.request, copia)); return r; })
    .catch(() => caches.match(e.request).then(r => r || caches.match("./"))));
});
"""


def generar(ofertas, resumen, perfil_publico=None):
    datos = json.dumps({"resumen": resumen, "ofertas": ofertas, "perfil": perfil_publico or {}}, ensure_ascii=False)
    datos = datos.replace("</", "<\\/")  # evita cerrar el <script> por accidente
    return PLANTILLA.replace("__DATOS__", datos)


def archivos_pwa():
    """Archivos fijos de la app instalable (se escriben junto a index.html)."""
    return {
        "manifest.webmanifest": json.dumps(MANIFIESTO, ensure_ascii=False, indent=1),
        "sw.js": SERVICE_WORKER,
    }
