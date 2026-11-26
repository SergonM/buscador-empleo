"""Genera docs/index.html: "Rumbo", la app (PWA) de Sergio para buscar empleo desde el celular.

Todo lo que marca Sergio (guardada, postulé, entrevista, notas, meta semanal) vive en el navegador
(localStorage): no hay servidor ni cuentas. Desde "Progreso" se puede copiar un respaldo y restaurarlo.
"""
import json

PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f6f1e7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1424" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Rumbo">
<title>Rumbo · Ofertas para Sergio</title>
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icono.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icono-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f6f1e7;--bg2:#efe7d8;--card:#fffdf8;--ink:#14203b;--ink2:#4a5470;--mut:#7c8499;--line:#e6dccb;
  --acc:#ff5a36;--acc2:#ff8a3d;--acc-bg:#ffe8df;--ok:#14936f;--ok-bg:#dcf3ea;--warn:#b7791f;--warn-bg:#fbefd5;
  --datos:#5b4fe0;--datos-bg:#ebe8ff;--neg:#d9840b;--neg-bg:#fdf0d9;--ciber:#0f8f86;--ciber-bg:#d9f2ef;
  --sombra:0 1px 0 rgba(20,32,59,.04),0 8px 24px -12px rgba(20,32,59,.18);
  --serif:"Fraunces",Georgia,serif;--sans:"Plus Jakarta Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0f1424;--bg2:#161d33;--card:#18203a;--ink:#f1ede4;--ink2:#c4c8d6;--mut:#8e96ad;--line:#273152;
  --acc:#ff7752;--acc2:#ffa15c;--acc-bg:#3a2026;--ok:#3fd0a2;--ok-bg:#123329;--warn:#f0b65a;--warn-bg:#3a2d12;
  --datos:#9d95ff;--datos-bg:#26245a;--neg:#f6b552;--neg-bg:#3b2c10;--ciber:#4fd4c8;--ciber-bg:#103837;
  --sombra:0 1px 0 rgba(0,0,0,.2),0 10px 30px -14px rgba(0,0,0,.6);
}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.5 var(--sans);padding-bottom:calc(84px + env(safe-area-inset-bottom))}
button{font:inherit;color:inherit;cursor:pointer;border:0;background:none}
a{color:inherit}
.wrap{max-width:640px;margin:0 auto;padding:0 18px}
/* ---------- Encabezado ---------- */
.hero{position:relative;padding:calc(22px + env(safe-area-inset-top)) 0 18px;overflow:hidden}
.hero::before{content:"";position:absolute;inset:-40% -30% auto auto;width:340px;height:340px;border-radius:50%;
  background:radial-gradient(circle at 30% 30%,var(--acc2),var(--acc) 55%,transparent 70%);opacity:.18;filter:blur(8px);pointer-events:none}
.marca{display:flex;align-items:center;gap:8px;font-weight:700;letter-spacing:.14em;font-size:11.5px;text-transform:uppercase;color:var(--ink2)}
.marca svg{width:22px;height:22px}
.marca button{margin-left:auto;font-size:12px;letter-spacing:0;text-transform:none;font-weight:600;background:var(--ink);color:var(--bg);padding:6px 12px;border-radius:999px}
h1{font-family:var(--serif);font-weight:650;font-size:31px;line-height:1.1;margin:16px 0 6px;letter-spacing:-.01em}
h1 em{font-style:italic;color:var(--acc)}
.lead{color:var(--ink2);margin:0;font-size:15px}
.lead b{color:var(--ink)}
/* ---------- Meta semanal ---------- */
.meta-sem{display:flex;align-items:center;gap:14px;margin-top:18px;background:var(--card);border:1px solid var(--line);border-radius:20px;padding:14px 16px;box-shadow:var(--sombra)}
.anillo{--p:0;flex:0 0 auto;width:58px;height:58px;border-radius:50%;display:grid;place-items:center;
  background:conic-gradient(var(--acc) calc(var(--p)*1%),var(--bg2) 0)}
.anillo span{width:46px;height:46px;border-radius:50%;background:var(--card);display:grid;place-items:center;font-weight:700;font-size:15px}
.meta-sem p{margin:0;font-size:14px;color:var(--ink2)}
.meta-sem strong{display:block;color:var(--ink);font-size:15.5px}
.meta-sem button{margin-left:auto;font-size:13px;color:var(--acc);font-weight:600;padding:6px}
/* ---------- Destacada ---------- */
.titulo-sec{display:flex;align-items:baseline;justify-content:space-between;margin:26px 0 10px}
.titulo-sec h2{font-family:var(--serif);font-weight:650;font-size:21px;margin:0}
.titulo-sec small{color:var(--mut);font-size:13px}
.destacada{position:relative;border-radius:24px;padding:20px;color:#fff;overflow:hidden;
  background:linear-gradient(135deg,#14203b 0%,#2a2f6b 55%,#ff5a36 140%);box-shadow:0 18px 40px -20px rgba(20,32,59,.7)}
.destacada::after{content:"";position:absolute;right:-60px;top:-60px;width:200px;height:200px;border-radius:50%;border:28px solid rgba(255,255,255,.07)}
.destacada .eti{display:inline-flex;gap:6px;align-items:center;font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;background:rgba(255,255,255,.14);padding:5px 10px;border-radius:999px}
.destacada h3{font-family:var(--serif);font-weight:650;font-size:23px;line-height:1.2;margin:14px 0 4px;position:relative;z-index:1}
.destacada .emp{opacity:.85;font-size:14.5px}
.destacada .why{color:#fff;opacity:.9;font-size:14px;margin:12px 0 16px}
.destacada .acc{display:flex;gap:10px;position:relative;z-index:1}
.destacada a.ver{flex:1;background:#fff;color:#14203b;text-decoration:none;text-align:center;font-weight:700;border-radius:14px;padding:12px}
.destacada button{background:rgba(255,255,255,.16);color:#fff;border-radius:14px;padding:0 16px;font-weight:600}
.destacada .pts{position:absolute;right:18px;top:16px;z-index:1;font-family:var(--serif);font-size:34px;font-weight:650;line-height:1}
.destacada .pts small{display:block;font-family:var(--sans);font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;opacity:.7;text-align:right}
/* ---------- Filtros ---------- */
.barra{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);margin:0 -18px;padding:10px 18px 10px;border-bottom:1px solid transparent}
.barra.pegada{border-bottom-color:var(--line)}
.busca{display:flex;gap:8px}
.busca label{flex:1;display:flex;align-items:center;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:0 12px}
.busca svg{width:18px;height:18px;color:var(--mut);flex:0 0 auto}
.busca input{flex:1;min-width:0;border:0;background:none;color:var(--ink);font:inherit;padding:11px 0;outline:none}
.btn-f{display:flex;align-items:center;gap:6px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:0 13px;font-weight:600;font-size:14px}
.btn-f b{background:var(--acc);color:#fff;border-radius:999px;font-size:11px;padding:1px 6px}
.chips{display:flex;gap:8px;overflow-x:auto;padding-top:10px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;display:flex;align-items:center;gap:6px;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:7px 13px;font-size:13.5px;font-weight:600;color:var(--ink2)}
.chip i{width:8px;height:8px;border-radius:50%;background:var(--c,var(--mut))}
.chip[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:var(--bg)}
/* ---------- Tarjetas ---------- */
.lista{padding-top:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:16px;margin-bottom:12px;box-shadow:var(--sombra);position:relative;animation:entra .35s ease both}
@keyframes entra{from{opacity:0;transform:translateY(8px)}}
.card.marcada{border-color:color-mix(in srgb,var(--acc) 45%,var(--line))}
.fila{display:flex;gap:12px;align-items:flex-start}
.logo{flex:0 0 auto;width:44px;height:44px;border-radius:14px;display:grid;place-items:center;font-weight:700;font-size:15px;color:#fff;background:hsl(var(--h) 55% 48%)}
.info{flex:1;min-width:0}
.card h3{font-size:16px;font-weight:700;line-height:1.3;margin:0}
.card .emp{color:var(--ink2);font-size:13.5px;margin-top:2px}
.nota-p{flex:0 0 auto;width:48px;height:48px;border-radius:50%;display:grid;place-items:center;
  background:conic-gradient(var(--cn) calc(var(--p)*1%),var(--bg2) 0)}
.nota-p span{width:38px;height:38px;border-radius:50%;background:var(--card);display:grid;place-items:center;font-weight:700;font-size:14px;line-height:1}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 0}
.tag{font-size:12px;font-weight:600;border-radius:8px;padding:3px 8px;background:var(--bg2);color:var(--ink2)}
.tag.area{background:var(--cb);color:var(--c)}
.tag.nueva{background:var(--acc-bg);color:var(--acc)}
.tag.est{background:var(--ink);color:var(--bg)}
.tag.ok{background:var(--ok-bg);color:var(--ok)}
.why{font-size:14px;color:var(--ink2);margin:10px 0 14px}
.acc{display:flex;gap:8px}
.acc a.ver{flex:1;text-align:center;text-decoration:none;background:var(--acc);color:#fff;font-weight:700;border-radius:14px;padding:11px;font-size:14.5px}
.ico{flex:0 0 auto;width:46px;border-radius:14px;background:var(--bg2);display:grid;place-items:center}
.ico svg{width:20px;height:20px}
.ico[aria-pressed=true]{background:var(--acc-bg);color:var(--acc)}
.aviso{background:var(--warn-bg);color:var(--warn);border-radius:12px;padding:8px 11px;font-size:13px;font-weight:600;margin:0 0 12px}
.vacio{text-align:center;color:var(--mut);padding:40px 20px}
.vacio svg{width:120px;height:120px;margin-bottom:8px}
.vacio h3{font-family:var(--serif);color:var(--ink);font-size:20px;margin:0 0 6px}
.mas{display:block;width:100%;padding:13px;border-radius:14px;border:1px dashed var(--line);color:var(--ink2);font-weight:600;margin:4px 0 20px}
/* ---------- Navegación inferior ---------- */
nav.tab{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom));z-index:8;display:flex;gap:4px;
  background:color-mix(in srgb,var(--ink) 94%,transparent);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);padding:6px;border-radius:22px;box-shadow:0 16px 40px -12px rgba(15,20,36,.6);width:min(420px,calc(100% - 28px))}
nav.tab button{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;color:color-mix(in srgb,var(--bg) 60%,transparent);font-size:11px;font-weight:600;padding:7px 4px;border-radius:16px;position:relative}
nav.tab svg{width:22px;height:22px}
nav.tab button[aria-pressed=true]{color:var(--ink);background:var(--bg)}
nav.tab .n{position:absolute;top:3px;right:calc(50% - 20px);background:var(--acc);color:#fff;font-size:10px;border-radius:999px;padding:0 5px;min-width:16px;line-height:16px}
/* ---------- Hoja inferior ---------- */
.velo{position:fixed;inset:0;background:rgba(10,14,28,.45);z-index:20;opacity:0;pointer-events:none;transition:opacity .25s}
.velo.on{opacity:1;pointer-events:auto}
.hoja{position:fixed;left:0;right:0;bottom:0;z-index:21;max-height:88vh;overflow-y:auto;background:var(--bg);border-radius:26px 26px 0 0;
  padding:8px 18px calc(24px + env(safe-area-inset-bottom));transform:translateY(105%);visibility:hidden;transition:transform .32s cubic-bezier(.2,.8,.2,1),visibility 0s .32s;max-width:640px;margin:0 auto;overscroll-behavior:contain}
.hoja.on{transform:none;visibility:visible;transition:transform .32s cubic-bezier(.2,.8,.2,1)}
.asa{width:42px;height:5px;border-radius:9px;background:var(--line);margin:4px auto 14px}
.hoja h2{font-family:var(--serif);font-weight:650;font-size:22px;line-height:1.2;margin:0 0 4px}
.hoja .emp{color:var(--ink2);margin-bottom:14px}
.hoja h4{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);margin:20px 0 8px}
.seg{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.seg button{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:9px 4px;font-size:13px;font-weight:600}
.seg button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:var(--bg)}
.seg button.no[aria-pressed=true]{background:var(--acc);border-color:var(--acc)}
.kw{display:flex;flex-wrap:wrap;gap:6px}
.kw span{font-size:13px;font-weight:600;border-radius:8px;padding:4px 9px;background:var(--ok-bg);color:var(--ok)}
.kw.ref span{background:var(--warn-bg);color:var(--warn)}
textarea,select{width:100%;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:14px;padding:12px;font:inherit;font-size:14px}
textarea{min-height:200px;line-height:1.5;resize:vertical}
textarea.corta{min-height:70px}
.botones{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.botones button,.botones a{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 12px;font-size:13.5px;font-weight:600;text-decoration:none;color:var(--ink)}
.botones .fuerte{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.cerrar{position:sticky;top:0;float:right;background:var(--bg2);border-radius:50%;width:34px;height:34px;display:grid;place-items:center;margin:-4px -4px 0 8px}
.campo{display:flex;flex-direction:column;gap:6px;margin-bottom:12px;font-size:14px;font-weight:600}
.toggle{display:flex;align-items:center;justify-content:space-between;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:8px;font-weight:600;font-size:14.5px}
.toggle input{width:22px;height:22px;accent-color:var(--acc)}
/* ---------- Progreso ---------- */
.embudo{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.embudo div{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:12px 6px;text-align:center}
.embudo b{display:block;font-family:var(--serif);font-size:26px;font-weight:650}
.embudo small{color:var(--mut);font-size:11.5px;font-weight:600}
.panel{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px;margin-bottom:12px}
.panel h3{font-family:var(--serif);font-size:18px;margin:0 0 10px}
.fuente{display:flex;align-items:center;gap:10px;padding:8px 0;border-top:1px solid var(--line);font-size:14px}
.fuente:first-of-type{border-top:0}
.fuente .pt{width:9px;height:9px;border-radius:50%;background:var(--ok)}
.fuente .pt.mal{background:var(--acc)}
.fuente span{flex:1}
.fuente small{color:var(--mut)}
.barras{display:flex;align-items:flex-end;gap:6px;height:90px;margin-top:6px}
.barras div{flex:1;background:linear-gradient(var(--acc2),var(--acc));border-radius:6px 6px 3px 3px;min-height:4px;position:relative}
.barras div span{position:absolute;bottom:-18px;left:50%;transform:translateX(-50%);font-size:10px;color:var(--mut)}
.desc{display:flex;justify-content:space-between;font-size:13.5px;padding:5px 0;color:var(--ink2)}
.desc b{color:var(--ink)}
footer{color:var(--mut);font-size:12px;text-align:center;padding:10px 24px 20px}
footer a{color:var(--mut)}
#toast{position:fixed;left:50%;bottom:calc(96px + env(safe-area-inset-bottom));transform:translate(-50%,10px);background:var(--ink);color:var(--bg);padding:10px 18px;border-radius:999px;font-size:14px;font-weight:600;opacity:0;transition:.2s;pointer-events:none;z-index:30}
#toast.on{opacity:1;transform:translate(-50%,0)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
/* ---------- Escritorio: barra lateral, varias columnas y detalle a la derecha ---------- */
.lateral-marca,.lateral-pie,.hero[hidden]{display:none}
@media (min-width:1000px){
  body{padding-bottom:0}
  .wrap{max-width:1500px;margin:0 0 0 248px;padding:0 40px 0 36px}
  .hero{display:grid;grid-template-columns:1fr minmax(340px,420px);gap:12px 40px;align-items:end;padding-top:36px}
  .hero .marca{display:none}
  .hero h1{grid-column:1;font-size:44px;margin-top:0}
  .hero .lead{grid-column:1;font-size:16.5px;max-width:60ch}
  .meta-sem{grid-column:2;grid-row:1/3;margin:0}
  nav.tab{left:0;top:0;bottom:0;transform:none;width:224px;flex-direction:column;justify-content:flex-start;gap:6px;border-radius:0;padding:28px 14px;box-shadow:none;background:var(--ink)}
  nav.tab button{flex:0 0 auto;flex-direction:row;justify-content:flex-start;gap:12px;font-size:15px;padding:12px 14px;border-radius:14px}
  nav.tab .n{position:static;margin-left:auto}
  .lateral-marca{display:flex;align-items:center;gap:10px;color:var(--bg);font-family:var(--serif);font-size:24px;font-weight:650;padding:0 10px 22px}
  .lateral-marca svg{width:30px;height:30px}
  .lateral-pie{display:block;margin-top:auto;color:color-mix(in srgb,var(--bg) 55%,transparent);font-size:12px;padding:0 10px;line-height:1.5}
  .lista{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;align-items:start}
  .lista .card{margin:0}
  .lista .mas,.lista .vacio{grid-column:1/-1}
  .destacada{padding:28px 34px}
  .destacada .why{max-width:80ch;font-size:15px}
  .destacada h3{font-size:30px}
  .destacada .acc{max-width:420px}
  .barra{margin:0 -40px 0 -36px;padding:14px 40px 12px 36px}
  .busca{max-width:760px}
  .progreso{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}
  .progreso .panel{margin:0}
  .embudo{grid-template-columns:repeat(4,minmax(0,180px))}
  .velo,.velo.on{opacity:0;pointer-events:none}
  .hoja{left:auto;right:0;top:0;bottom:0;width:min(520px,42vw);max-height:none;height:100vh;margin:0;border-radius:28px 0 0 28px;padding:28px 30px 40px;transform:translateX(105%);box-shadow:-20px 0 60px -30px rgba(15,20,36,.5)}
  .hoja .asa{display:none}
  .hoja.on{transform:none}
  body.con-hoja .wrap{margin-right:min(520px,42vw)}
  body.con-hoja .hero{grid-template-columns:1fr}
  body.con-hoja .meta-sem{grid-column:1;grid-row:auto;max-width:520px}
  body.con-hoja .hero h1{font-size:36px}
  #toast{bottom:28px}
  footer{text-align:left;padding-left:0}
}
@media (min-width:1500px){.lista{grid-template-columns:repeat(3,minmax(0,1fr))}}
</style>
</head>
<body>
<div class="wrap">
  <section class="hero">
    <div class="marca">
      <svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M16 6l4.5 10L16 26l-4.5-10z" fill="#ff5a36"/><circle cx="16" cy="16" r="2.2" fill="currentColor"/></svg>
      Rumbo
      <button id="instalar" hidden>Instalar app</button>
    </div>
    <h1 id="saludo"></h1>
    <p class="lead" id="lead"></p>
    <div class="meta-sem" id="meta"></div>
  </section>
  <div id="vista"></div>
  <footer id="pie"></footer>
</div>
<nav class="tab" aria-label="Secciones">
  <div class="lateral-marca"><svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M16 6l4.5 10L16 26l-4.5-10z" fill="#ff5a36"/><circle cx="16" cy="16" r="2.2" fill="currentColor"/></svg>Rumbo</div>
  <button data-v="hoy"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/><circle cx="12" cy="12" r="4"/></svg>Hoy<span class="n" id="n-hoy"></span></button>
  <button data-v="explorar"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/></svg>Explorar</button>
  <button data-v="lista"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>Mi lista<span class="n" id="n-lista"></span></button>
  <button data-v="progreso"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>Progreso</button>
  <div class="lateral-pie" id="lateral-pie"></div>
</nav>
<div class="velo" id="velo"></div>
<div class="hoja" id="hoja" role="dialog" aria-modal="true"></div>
<div id="toast" role="status"></div>
<script>
const DATOS = __DATOS__;
const R = DATOS.resumen, O = DATOS.ofertas, P = DATOS.perfil || {};
const AREAS = {"Datos / ML":["datos","Datos / ML"],"Negocio / Producto":["neg","Negocio / Producto"],"Ciberseguridad / GRC":["ciber","Ciber / GRC"]};
const ESTADOS = [["guardada","Guardada"],["postulada","Postulé"],["entrevista","Entrevista"],["oferta","Oferta"],["descartada","No me interesa"]];
const NOMBRE_EST = Object.fromEntries(ESTADOS);
const LS = "buscador-empleo-v1";
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const MES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
const fmt = d => { if(!d) return ""; const [y,m,dd]=d.split("-"); return `${+dd} ${MES[m-1]}`; };
const hoyISO = () => new Date(Date.now()-5*3600e3).toISOString().slice(0,10);
const dias = d => d ? Math.round((new Date(hoyISO()) - new Date(d))/864e5) : 0;
const norm = s => String(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
const tono = s => { let h=0; for (const c of String(s)) h=(h*31+c.charCodeAt(0))%360; return h; };
const iniciales = s => (String(s||"?").replace(/[^\p{L}\p{N} &]/gu,"").split(/\s+/).filter(w=>w&&w!=="&").slice(0,2).map(w=>w[0]).join("")||"?").toUpperCase();
const ICO = {
  guardar:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>',
  guardada:'<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>',
  prep:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4z"/></svg>',
  cerrar:'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  lupa:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
  filtros:'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h16M7 12h10M10 18h4"/></svg>',
  brujula:'<svg viewBox="0 0 120 120" fill="none"><circle cx="60" cy="60" r="44" stroke="currentColor" stroke-opacity=".25" stroke-width="6"/><path d="M60 26l12 34-12 34-12-34z" fill="#ff5a36" fill-opacity=".85"/><circle cx="60" cy="60" r="6" fill="currentColor" fill-opacity=".5"/></svg>'
};

// ---------- Estado guardado en el navegador ----------
let M = {};
try { M = JSON.parse(localStorage.getItem(LS) || "{}") || {}; } catch(e) { M = {}; }
let AJ = {};
try { AJ = JSON.parse(localStorage.getItem(LS+"-ajustes") || "{}") || {}; } catch(e) { AJ = {}; }
const guardar = () => { try { localStorage.setItem(LS, JSON.stringify(M)); localStorage.setItem(LS+"-ajustes", JSON.stringify(AJ)); } catch(e) {} };
const POR_ID = Object.fromEntries(O.map(o => [o.id, o]));
const copiaDe = o => ({id:o.id,titulo:o.titulo,empresa:o.empresa,url:o.url,fuente:o.fuente,modalidad:o.modalidad,fecha:o.fecha,puntaje:o.puntaje,por_que:o.por_que,areas:o.areas||[],claves:o.claves||[],reforzar:o.reforzar||[],idioma:o.idioma||"es",salario:o.salario||"",seniority:o.seniority||""});
// Las ofertas marcadas guardan una copia para no perderlas cuando salgan del listado.
function marcar(id, estado){
  const o = POR_ID[id] || (M[id] && M[id].o);
  const prev = M[id] || {};
  if (prev.estado === estado) { delete prev.estado; } else {
    prev.estado = estado; prev.cuando = hoyISO();
    if (estado === "postulada" && !prev.postulada) prev.postulada = hoyISO();
  }
  if (o) prev.o = copiaDe(o);
  if (!prev.estado && !prev.nota && !prev.carta) delete M[id]; else M[id] = prev;
  guardar();
}
const estadoDe = id => (M[id] && M[id].estado) || "";
const ofertaDe = id => POR_ID[id] || (M[id]||{}).o;

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


// ---------- Estado de la vista ----------
let vista = ""; try { vista = localStorage.getItem(LS+"-vista") || ""; } catch(e) {}
if (!["hoy","explorar","lista","progreso"].includes(vista)) vista = "hoy";
const F = {area:"", q:"", mod:"", fuente:"", orden:"encaje", junior:false, sinIngles:false};
let limite = 30;
const fuentes = [...new Set(O.map(o => o.fuente))].sort();
const visibles = () => O.filter(o => estadoDe(o.id) !== "descartada");

function modalidadDe(o){ const m = norm(o.modalidad); return m.includes("remoto") ? "remoto" : m.includes("hibrido") ? "hibrido" : "presencial"; }
function esJunior(o){ return /junior|jr\b|trainee|practica|practicante|pasante|intern|aprendiz|entry|graduate|sin experiencia|poca o ninguna/.test(norm(o.titulo+" "+o.seniority+" "+o.por_que)); }
function pasa(o){
  if (F.area && !(o.areas||[]).includes(F.area)) return false;
  if (F.mod && modalidadDe(o) !== F.mod) return false;
  if (F.fuente && o.fuente !== F.fuente) return false;
  if (F.junior && !esJunior(o)) return false;
  if (F.sinIngles && o.idioma === "en") return false;
  if (F.q) { const t = norm(o.titulo+" "+o.empresa+" "+o.por_que+" "+(o.claves||[]).join(" ")+" "+(o.reforzar||[]).join(" ")); if (!norm(F.q).split(/\s+/).every(p => t.includes(p))) return false; }
  return true;
}
const nFiltros = () => [F.mod,F.fuente,F.junior,F.sinIngles,F.orden!=="encaje"].filter(Boolean).length;
const ORDEN = {encaje:(a,b)=>b.puntaje-a.puntaje||(b.fecha||"").localeCompare(a.fecha||""), fecha:(a,b)=>(b.fecha||"").localeCompare(a.fecha||"")||b.puntaje-a.puntaje, calidad:(a,b)=>(b.calidad||0)-(a.calidad||0)||b.puntaje-a.puntaje};

// ---------- Meta semanal ----------
function lunes(){ const d = new Date(hoyISO()); const w = (d.getUTCDay()+6)%7; d.setUTCDate(d.getUTCDate()-w); return d.toISOString().slice(0,10); }
function postuladasSemana(){ const l = lunes(); return Object.values(M).filter(m => m.postulada && m.postulada >= l).length; }
function pintarHero(){
  const h = new Date(Date.now()-5*3600e3).getUTCHours();
  const s = h < 12 ? "Buenos días" : h < 19 ? "Buenas tardes" : "Buenas noches";
  $("#saludo").innerHTML = `${s}, <em>${esc((P.nombre||"Sergio").split(" ")[0])}</em>.`;
  const nuevas = visibles().filter(o=>o.nueva).length;
  const act = new Date(R.actualizado).toLocaleString("es-CO",{day:"numeric",month:"short",hour:"numeric",minute:"2-digit"}).replace(/\.$/,"");
  $("#lead").innerHTML = nuevas
    ? `Hoy encontré <b>${nuevas} ofertas nuevas</b> para ti entre ${R.revisadas.toLocaleString("es-CO")} revisadas. Actualizado ${act}.`
    : `Hoy no hay ofertas nuevas, pero tienes <b>${visibles().length} activas</b> para revisar. Actualizado ${act}.`;
  const meta = AJ.meta || 5, n = postuladasSemana(), p = Math.min(100, Math.round(n/meta*100));
  $("#meta").innerHTML = `<div class="anillo" style="--p:${p}"><span>${n}/${meta}</span></div>
    <p><strong>${n>=meta?"¡Meta de la semana cumplida!":n?`Vas bien: ${meta-n} postulaciones más esta semana`:"Tu meta: "+meta+" postulaciones esta semana"}</strong>Marca “Postulé” en cada oferta y aquí verás tu avance.</p>
    <button data-acc="meta" aria-label="Cambiar meta">Editar</button>`;
}

// ---------- Tarjetas ----------
function anilloNota(n){ const c = n>=75?"var(--ok)":n>=55?"var(--acc2)":"var(--mut)"; return `<div class="nota-p" style="--p:${n};--cn:${c}" aria-label="Encaje ${n} de 100"><span>${n}</span></div>`; }
function tagsArea(o){ return (o.areas||[]).map(a => { const [k,l] = AREAS[a]||["",a]; return `<span class="tag area" style="--c:var(--${k});--cb:var(--${k}-bg)">${esc(l)}</span>`; }).join(""); }
function tarjeta(o, i){
  const st = estadoDe(o.id), m = M[o.id] || {};
  const seguimiento = st === "postulada" && dias(m.postulada||m.cuando) >= 7;
  const caduca = !POR_ID[o.id];
  return `<article class="card${st&&st!=="descartada"?" marcada":""}" data-id="${esc(o.id)}" style="animation-delay:${Math.min(i,8)*30}ms">
    <div class="fila">
      <div class="logo" style="--h:${tono(o.empresa)}">${esc(iniciales(o.empresa))}</div>
      <div class="info"><h3>${esc(o.titulo)}</h3><div class="emp">${esc(o.empresa||"Empresa sin nombre")} · ${esc(o.modalidad)}</div></div>
      ${anilloNota(o.puntaje)}
    </div>
    <div class="tags">${st?`<span class="tag est">${NOMBRE_EST[st]}${m.cuando?" · "+fmt(m.cuando):""}</span>`:""}${o.nueva&&!st?'<span class="tag nueva">Nueva</span>':""}${tagsArea(o)}${o.fecha?`<span class="tag">${fmt(o.fecha)}</span>`:""}${o.salario?`<span class="tag ok">${esc(o.salario)}</span>`:""}${o.idioma==="en"?'<span class="tag">En inglés</span>':""}${caduca?'<span class="tag">Ya no aparece</span>':""}</div>
    <p class="why">${esc(o.por_que)}</p>
    ${seguimiento?`<p class="aviso">Te postulaste hace ${dias(m.postulada||m.cuando)} días: escribe un mensaje corto de seguimiento.</p>`:""}
    <div class="acc">
      <a class="ver" href="${esc(o.url)}" target="_blank" rel="noopener">Ver en ${esc(o.fuente)}</a>
      <button class="ico" data-acc="guardada" aria-pressed="${st==="guardada"}" aria-label="Guardar">${st==="guardada"?ICO.guardada:ICO.guardar}</button>
      <button class="ico" data-acc="abrir" aria-label="Preparar postulación">${ICO.prep}</button>
    </div>
  </article>`;
}
function listado(l){
  if (!l.length) return "";
  const html = l.slice(0, limite).map(tarjeta).join("");
  return html + (l.length > limite ? `<button class="mas" data-acc="mas">Ver ${Math.min(30, l.length-limite)} más de ${l.length - limite}</button>` : "");
}
const vacio = (t, d) => `<div class="vacio">${ICO.brujula}<h3>${t}</h3><p>${d}</p></div>`;

// ---------- Vistas ----------
function vistaHoy(){
  const nuevas = visibles().filter(o => o.nueva).sort(ORDEN.encaje);
  const base = nuevas.length ? nuevas : visibles().sort(ORDEN.encaje);
  const top = base.find(o => !estadoDe(o.id));
  let h = "";
  if (top) {
    h += `<div class="titulo-sec"><h2>La mejor de hoy</h2><small>${esc(top.fuente)}</small></div>
    <article class="destacada" data-id="${esc(top.id)}">
      <span class="eti">★ ${esc(((top.areas||[])[0])||"Para ti")}</span>
      <div class="pts">${top.puntaje}<small>encaje</small></div>
      <h3>${esc(top.titulo)}</h3>
      <div class="emp">${esc(top.empresa)} · ${esc(top.modalidad)}</div>
      <p class="why">${esc(top.por_que)}</p>
      <div class="acc"><a class="ver" href="${esc(top.url)}" target="_blank" rel="noopener">Ver oferta</a><button data-acc="abrir">Preparar</button></div>
    </article>`;
  }
  const resto = base.filter(o => o !== top);
  h += `<div class="titulo-sec"><h2>${nuevas.length ? "Nuevas para ti" : "Tus mejores opciones"}</h2><small>${resto.length} ofertas</small></div>`;
  h += `<div class="lista">${listado(resto) || vacio("Todo revisado", "Mañana a las 7:00 a. m. llegan ofertas nuevas.")}</div>`;
  return h;
}
function vistaExplorar(){
  const l = visibles().filter(pasa).sort(ORDEN[F.orden]);
  const nf = nFiltros();
  const chips = [["","Todas",""],...Object.entries(AREAS).map(([a,[k,lab]])=>[a,lab,k])].map(([v,lab,k]) =>
    `<button class="chip" data-area="${esc(v)}" aria-pressed="${F.area===v}" style="--c:var(--${k||"mut"})">${k?"<i></i>":""}${esc(lab)}</button>`).join("");
  return `<div class="barra" id="barra">
      <div class="busca"><label>${ICO.lupa}<input id="q" type="search" placeholder="Cargo, empresa o habilidad" value="${esc(F.q)}" autocomplete="off"></label>
      <button class="btn-f" data-acc="filtros">${ICO.filtros}Filtros${nf?`<b>${nf}</b>`:""}</button></div>
      <div class="chips">${chips}</div>
    </div>
    <div class="titulo-sec"><h2>Explorar</h2><small>${l.length} de ${visibles().length}</small></div>
    <div class="lista" id="resultados">${listado(l) || vacio("Nada con estos filtros", "Prueba quitando algún filtro o buscando otra palabra.")}</div>`;
}
function marcadas(){ return Object.entries(M).filter(([id,m]) => m.estado).map(([id,m]) => ({...(m.o||{}), ...(POR_ID[id]||{}), id})); }
function embudo(){
  const ms = Object.values(M);
  const n = k => ms.filter(m => m.estado === k).length;
  const post = ms.filter(m => m.postulada).length;
  return `<div class="embudo"><div><b>${n("guardada")}</b><small>Guardadas</small></div><div><b>${post}</b><small>Postulé</small></div><div><b>${n("entrevista")}</b><small>Entrevistas</small></div><div><b>${n("oferta")}</b><small>Ofertas</small></div></div>`;
}
function vistaLista(){
  const rango = {oferta:0,entrevista:1,postulada:2,guardada:3,descartada:4};
  const l = marcadas().filter(o => estadoDe(o.id) !== "descartada").sort((a,b) => rango[estadoDe(a.id)]-rango[estadoDe(b.id)] || (M[b.id].cuando||"").localeCompare(M[a.id].cuando||""));
  const desc = marcadas().filter(o => estadoDe(o.id) === "descartada").length;
  return `<div class="titulo-sec"><h2>Mi lista</h2><small>${l.length} en seguimiento</small></div>${embudo()}
    <div class="lista" style="margin-top:14px">${listado(l) || vacio("Tu lista está vacía", "Toca el marcador para guardar una oferta, o el lápiz para preparar tu postulación y marcar “Postulé”.")}</div>
    ${desc?`<p style="text-align:center;color:var(--mut);font-size:13px">${desc} ofertas marcadas como “No me interesa” no se muestran.</p>`:""}`;
}
function vistaProgreso(){
  const est = R.estado_fuentes || {};
  const fuentesH = Object.entries(est).map(([f,e]) => `<div class="fuente"><i class="pt${e.ok?"":" mal"}"></i><span>${esc(f)}</span><small>${e.ok?`${e.ofertas.toLocaleString("es-CO")} ofertas · ${e.segundos} s`:esc(e.error||"falló")}</small></div>`).join("");
  const hist = (R.historia||[]).slice(-10);
  const max = Math.max(1, ...hist.map(h => h.nuevas));
  const barras = hist.map(h => `<div style="height:${Math.max(4, h.nuevas/max*100)}%" title="${h.nuevas} nuevas"><span>${fmt(h.fecha).split(" ")[0]}</span></div>`).join("");
  const desc = Object.entries(R.descartes||{}).slice(0,8).map(([k,n]) => `<div class="desc"><span>${esc(k)}</span><b>${n}</b></div>`).join("");
  return `<div class="titulo-sec"><h2>Tu progreso</h2><small>meta: ${AJ.meta||5} por semana</small></div>${embudo()}
    <div class="progreso" style="margin-top:14px"><div class="panel"><h3>Fuentes de hoy</h3>${fuentesH}
      <p style="color:var(--mut);font-size:13px;margin:10px 0 0">${R.revisadas.toLocaleString("es-CO")} revisadas → ${R.mostradas} pasan tus filtros${R.duracion?` · búsqueda de ${Math.round(R.duracion/60)} min`:""}.</p></div>
    ${hist.length>1?`<div class="panel"><h3>Ofertas nuevas por día</h3><div class="barras">${barras}</div><div style="height:18px"></div></div>`:""}
    ${desc?`<div class="panel"><h3>Por qué se descartaron</h3>${desc}</div>`:""}
    <div class="panel"><h3>Respaldo y ajustes</h3>
      <p style="color:var(--ink2);font-size:14px;margin:0">Tus marcas y notas se guardan solo en este celular. Copia el respaldo para no perderlas o pasarlas a otro equipo.</p>
      <div class="botones"><button class="fuerte" data-acc="exportar">Copiar respaldo</button><button data-acc="importar">Pegar respaldo</button><button data-acc="meta">Cambiar meta semanal</button></div></div></div>`;
}

function pintar(){
  document.querySelectorAll("nav.tab button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v===vista));
  const nuevas = visibles().filter(o=>o.nueva && !estadoDe(o.id)).length;
  $("#n-hoy").textContent = nuevas || ""; $("#n-hoy").hidden = !nuevas;
  const nl = marcadas().filter(o => estadoDe(o.id) !== "descartada").length;
  $("#n-lista").textContent = nl || ""; $("#n-lista").hidden = !nl;
  pintarHero();
  document.querySelector(".hero").hidden = vista === "explorar";
  $("#vista").innerHTML = {hoy:vistaHoy, explorar:vistaExplorar, lista:vistaLista, progreso:vistaProgreso}[vista]();
  const q = $("#q"); if (q) q.oninput = e => { F.q = e.target.value.trim(); limite = 30; repintarResultados(); };
  const lp = $("#lateral-pie"); if (lp) lp.innerHTML = `Actualizado ${new Date(R.actualizado).toLocaleString("es-CO",{day:"numeric",month:"short",hour:"numeric",minute:"2-digit"})}<br>${R.mostradas} ofertas · ${fuentes.length} fuentes`;
  $("#pie").innerHTML = `Rumbo revisa cada día ${fuentes.length} fuentes: ${fuentes.map(esc).join(", ")}. Cada oferta enlaza a su publicación original (Computrabajo, Get on Board, Remotive, Himalayas, Jobicy, Remote OK y portales de cada empresa). <a href="https://github.com/SergonM/buscador-empleo">Código</a>`;
}
function repintarResultados(){
  const l = visibles().filter(pasa).sort(ORDEN[F.orden]);
  $("#resultados").innerHTML = listado(l) || vacio("Nada con estos filtros", "Prueba quitando algún filtro o buscando otra palabra.");
  const s = document.querySelector(".titulo-sec small"); if (s) s.textContent = `${l.length} de ${visibles().length}`;
}

// ---------- Hoja inferior ----------
let abiertaId = null;
const ESCRITORIO = matchMedia("(min-width:1000px)");
function abrirHoja(html){ $("#hoja").innerHTML = `<div class="asa"></div>` + html; $("#hoja").scrollTop = 0; $("#hoja").classList.add("on"); $("#velo").classList.add("on"); document.body.classList.add("con-hoja"); if (!ESCRITORIO.matches) document.body.style.overflow = "hidden"; }
function cerrarHoja(){ $("#hoja").classList.remove("on"); $("#velo").classList.remove("on"); document.body.style.overflow = ""; document.body.classList.remove("con-hoja"); if (abiertaId) { abiertaId = null; pintar(); } }
function hojaOferta(id){
  const o = ofertaDe(id); if (!o) return;
  abiertaId = id;
  const st = estadoDe(id), m = M[id] || {}, emp = encodeURIComponent(o.empresa||"");
  abrirHoja(`<button class="cerrar" data-acc="cerrar" aria-label="Cerrar">${ICO.cerrar}</button>
    <h2>${esc(o.titulo)}</h2><div class="emp">${esc(o.empresa)} · ${esc(o.modalidad)} · encaje ${o.puntaje}/100</div>
    <div class="botones"><a class="fuerte" href="${esc(o.url)}" target="_blank" rel="noopener">Abrir oferta en ${esc(o.fuente)}</a></div>
    <h4>¿En qué vas?</h4>
    <div class="seg" data-id="${esc(id)}">${ESTADOS.map(([k,l]) => `<button data-acc="${k}" class="${k==="descartada"?"no":""}" aria-pressed="${st===k}">${l}</button>`).join("")}</div>
    ${(o.claves||[]).length ? `<h4>Ya las tienes · ponlas en tu hoja de vida</h4><div class="kw">${o.claves.map(k=>`<span>${esc(k)}</span>`).join("")}</div>` : ""}
    ${(o.reforzar||[]).length ? `<h4>La oferta también pide · menciónalas si las has usado</h4><div class="kw ref">${o.reforzar.map(k=>`<span>${esc(k)}</span>`).join("")}</div>` : ""}
    <h4>Carta breve ${o.idioma==="en"?"(en inglés) ":""}· edítala antes de enviar</h4>
    <textarea data-campo="carta" data-id="${esc(id)}">${esc(m.carta || carta(o))}</textarea>
    <div class="botones"><button class="fuerte" data-acc="copiar-carta">Copiar carta</button><button data-acc="copiar-msg" data-id="${esc(id)}">Copiar mensaje para reclutador</button><button data-acc="restaurar-carta" data-id="${esc(id)}">Restaurar carta</button></div>
    <h4>Investiga la empresa</h4>
    <div class="botones">
      <a href="https://www.linkedin.com/search/results/companies/?keywords=${emp}" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://www.linkedin.com/search/results/people/?keywords=${emp}%20talent%20acquisition" target="_blank" rel="noopener">Reclutadores</a>
      <a href="https://www.glassdoor.com/Search/results.htm?keyword=${emp}" target="_blank" rel="noopener">Opiniones</a>
      <a href="https://www.google.com/search?q=${emp}%20salario%20${encodeURIComponent(o.titulo)}%20Colombia" target="_blank" rel="noopener">Salario</a>
    </div>
    <h4>Mis notas</h4>
    <textarea class="corta" data-campo="nota" data-id="${esc(id)}" placeholder="Contacto, fecha de entrevista, salario conversado…">${esc(m.nota||"")}</textarea>`);
}
function hojaFiltros(){
  abrirHoja(`<button class="cerrar" data-acc="cerrar" aria-label="Cerrar">${ICO.cerrar}</button><h2>Filtros</h2><div class="emp">Afina lo que ves en Explorar</div>
    <label class="campo">Modalidad<select data-f="mod"><option value="">Todas</option><option value="remoto">Remoto</option><option value="hibrido">Híbrido</option><option value="presencial">Presencial o no indica</option></select></label>
    <label class="campo">Fuente<select data-f="fuente"><option value="">Todas</option>${fuentes.map(f=>`<option>${esc(f)}</option>`).join("")}</select></label>
    <label class="campo">Ordenar por<select data-f="orden"><option value="encaje">Mejor encaje</option><option value="fecha">Más recientes</option><option value="calidad">Ofertas más completas</option></select></label>
    <label class="toggle">Solo junior o práctica<input type="checkbox" data-f="junior"></label>
    <label class="toggle">Ocultar ofertas en inglés<input type="checkbox" data-f="sinIngles"></label>
    <div class="botones" style="margin-top:14px"><button class="fuerte" data-acc="cerrar">Ver resultados</button><button data-acc="limpiar">Limpiar filtros</button></div>`);
  document.querySelectorAll("[data-f]").forEach(el => { if (el.type === "checkbox") el.checked = F[el.dataset.f]; else el.value = F[el.dataset.f]; });
}
function hojaMeta(){
  abrirHoja(`<button class="cerrar" data-acc="cerrar" aria-label="Cerrar">${ICO.cerrar}</button><h2>Meta semanal</h2><div class="emp">¿Cuántas postulaciones quieres enviar cada semana?</div>
    <div class="seg">${[3,5,8,10,15,20].map(n => `<button data-meta="${n}" aria-pressed="${(AJ.meta||5)===n}">${n}</button>`).join("")}</div>
    <p style="color:var(--ink2);font-size:14px">Postular con constancia es lo que más mueve la aguja: 5 a 10 postulaciones bien preparadas por semana suele ser un buen ritmo.</p>`);
}

// ---------- Interacción ----------
let toastT;
function toast(t){ const e=$("#toast"); e.textContent=t; e.classList.add("on"); clearTimeout(toastT); toastT=setTimeout(()=>e.classList.remove("on"),1800); }
async function copiar(t){ try { await navigator.clipboard.writeText(t); toast("Copiado"); } catch(e) { prompt("Copia el texto:", t); } }

document.querySelector("nav.tab").onclick = e => { const b=e.target.closest("button"); if(!b) return; vista=b.dataset.v; limite=30; if ($("#hoja").classList.contains("on")) { abiertaId = null; cerrarHoja(); } try{localStorage.setItem(LS+"-vista",vista);}catch(_){} pintar(); scrollTo({top:0}); };
$("#velo").onclick = cerrarHoja;
document.body.addEventListener("click", e => {
  const chip = e.target.closest("[data-area]"); if (chip) { F.area = chip.dataset.area; limite = 30; pintar(); return; }
  const mt = e.target.closest("[data-meta]"); if (mt) { AJ.meta = +mt.dataset.meta; guardar(); cerrarHoja(); pintar(); toast("Meta actualizada"); return; }
  const b = e.target.closest("[data-acc]"); if (!b) return;
  const acc = b.dataset.acc, cont = b.closest("[data-id]"), id = cont && cont.dataset.id;
  if (acc === "abrir") return hojaOferta(id);
  if (acc === "cerrar") return cerrarHoja();
  if (acc === "filtros") return hojaFiltros();
  if (acc === "meta") return hojaMeta();
  if (acc === "mas") { limite += 30; pintar(); return; }
  if (acc === "limpiar") { Object.assign(F, {mod:"", fuente:"", orden:"encaje", junior:false, sinIngles:false}); cerrarHoja(); pintar(); return; }
  if (NOMBRE_EST[acc]) {
    marcar(id, acc); const st = estadoDe(id);
    toast(st ? (st==="postulada" ? "¡Bien! Postulación registrada" : NOMBRE_EST[acc]) : "Quitada de tu lista");
    if (b.closest(".hoja")) { b.parentElement.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x.dataset.acc===st)); pintarHero(); }
    else pintar();
    return;
  }
  if (acc === "copiar-carta") return copiar($("#hoja [data-campo=carta]").value);
  if (acc === "copiar-msg") return copiar(mensajeReclutador(ofertaDe(id)));
  if (acc === "restaurar-carta") { const m = M[id]; if (m) { delete m.carta; guardar(); } $("#hoja [data-campo=carta]").value = carta(ofertaDe(id)); return; }
  if (acc === "exportar") return copiar(JSON.stringify({marcas:M, ajustes:AJ}));
  if (acc === "importar") {
    const t = prompt("Pega aquí el respaldo:"); if (!t) return;
    try { const d = JSON.parse(t); if (typeof d !== "object" || !d) throw 0; Object.assign(M, d.marcas || d); if (d.ajustes) Object.assign(AJ, d.ajustes); guardar(); toast("Respaldo restaurado"); pintar(); } catch(_) { toast("Ese texto no es un respaldo válido"); }
  }
});
document.body.addEventListener("change", e => {
  const f = e.target.dataset.f; if (!f) return;
  F[f] = e.target.type === "checkbox" ? e.target.checked : e.target.value; limite = 30;
  if (vista === "explorar") pintar();
});
document.body.addEventListener("input", e => {
  const c = e.target.dataset.campo; if (!c) return;
  const id = e.target.dataset.id, o = ofertaDe(id);
  const m = M[id] || {}; m[c] = e.target.value;
  if (o && !m.o) m.o = copiaDe(o);
  M[id] = m; guardar();
});
addEventListener("keydown", e => { if (e.key === "Escape") cerrarHoja(); });
addEventListener("scroll", () => { const b = $("#barra"); if (b) b.classList.toggle("pegada", scrollY > 10); }, {passive:true});

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
    "name": "Rumbo · Ofertas para Sergio",
    "short_name": "Rumbo",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#f6f1e7",
    "theme_color": "#14203b",
    "lang": "es",
    "icons": [
        {"src": "icono-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icono-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icono-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

# Red primero (para ver siempre lo de hoy) y copia guardada si no hay señal.
SERVICE_WORKER = """const C = "rumbo-v2";
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
