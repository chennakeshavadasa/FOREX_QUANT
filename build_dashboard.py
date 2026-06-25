#!/usr/bin/env python3
"""Build the final fixed dashboard with data embedded - ready for GitHub Pages."""
import json, re

with open('multi_data.json') as f:
    data = json.load(f)
data_json = json.dumps(data, separators=(',',':'))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>FX Quant – EUR/INR & USD/INR Transfer Intelligence</title>
<meta name="description" content="Institutional quant analysis for EUR/INR and USD/INR. ARIMA, Holt-Winters, Monte Carlo, RSI, MACD, Bollinger Bands, VaR, Hurst Exponent and optimal transfer window."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg0:#030712;--bg1:#080e1c;--bg2:#0d1526;--bg3:#111d33;
  --card:rgba(13,21,38,.9);--border:rgba(80,110,255,.11);--borderB:rgba(80,110,255,.28);
  --blue:#5e7fff;--purple:#a259f7;--cyan:#21d0ec;
  --green:#10b981;--red:#ef4444;--orange:#f59e0b;--gold:#fbbf24;
  --slate:#94a3b8;--muted:#475569;--dim:#2d3a52;
  --r:14px;--rs:9px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg0);color:#f1f5f9;font-family:'Inter',sans-serif;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;z-index:-1;
  background:radial-gradient(ellipse 70% 50% at 15% 5%,rgba(94,127,255,.07) 0%,transparent 60%),
             radial-gradient(ellipse 50% 40% at 85% 90%,rgba(162,89,247,.06) 0%,transparent 60%);
  animation:bgP 10s ease-in-out infinite alternate}
@keyframes bgP{0%{opacity:.6}100%{opacity:1}}

/* HEADER */
.hdr{padding:18px 32px;border-bottom:1px solid var(--border);background:rgba(8,14,28,.97);
  backdrop-filter:blur(24px);position:sticky;top:0;z-index:200;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
.hdr-logo{width:40px;height:40px;border-radius:11px;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;font-size:21px;
  animation:lp 3s ease-in-out infinite}
@keyframes lp{0%,100%{box-shadow:0 0 20px rgba(94,127,255,.4)}50%{box-shadow:0 0 40px rgba(94,127,255,.7),0 0 60px rgba(162,89,247,.3)}}
.hdr-title h1{font-size:21px;font-weight:800;letter-spacing:-.4px}
.hdr-title h1 em{font-style:normal;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hdr-title p{font-size:13px;color:var(--muted);margin-top:2px}
.live-pip{display:flex;align-items:center;gap:6px;background:rgba(16,185,129,.1);
  border:1px solid rgba(16,185,129,.28);padding:5px 12px;border-radius:50px;font-size:14px;font-weight:700;color:var(--green)}
.pip-dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:blink 1.4s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.hdr-rates{display:flex;gap:18px;flex-wrap:wrap;align-items:center}
.hdr-rate-item{text-align:right}
.hdr-rate-label{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--muted)}
.hdr-rate-val{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700}
.eur-c{color:#6b8fff}.usd-c{color:#4ade80}

/* CONTROL BAR */
.ctrl{padding:12px 32px;background:rgba(8,14,28,.7);border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.ctrl-lbl{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--muted);white-space:nowrap}
.pg{display:flex;gap:3px;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:50px;padding:3px}
.pl{padding:6px 15px;border-radius:50px;font-size:15px;font-weight:700;cursor:pointer;
  color:var(--muted);border:none;background:transparent;transition:all .18s;white-space:nowrap}
.pl:hover{color:#f1f5f9;background:rgba(255,255,255,.05)}
.pl.active{background:rgba(94,127,255,.18);color:#a5b8ff;border:1px solid rgba(94,127,255,.32)}
.pl.eur-a{background:rgba(107,143,255,.18);color:#7aa3ff;border:1px solid rgba(107,143,255,.32)}
.pl.usd-a{background:rgba(74,222,128,.14);color:#4ade80;border:1px solid rgba(74,222,128,.28)}
.pl.gbp-a{background:rgba(216,180,226,.14);color:#d8b4e2;border:1px solid rgba(216,180,226,.28)}
.pl.jpy-a{background:rgba(252,165,165,.14);color:#fca5a5;border:1px solid rgba(252,165,165,.28)}
.pl.cny-a{background:rgba(248,113,113,.14);color:#f87171;border:1px solid rgba(248,113,113,.28)}
.pl.sgd-a{background:rgba(252,211,77,.14);color:#fcd34d;border:1px solid rgba(252,211,77,.28)}
.pl.hkd-a{background:rgba(167,139,250,.14);color:#a78bfa;border:1px solid rgba(167,139,250,.28)}
.pl.dur-a{background:rgba(251,191,36,.14);color:#fbbf24;border:1px solid rgba(251,191,36,.28)}
.ctrl-ts{margin-left:auto;font-size:13px;color:var(--muted);font-family:'JetBrains Mono',monospace}

/* TAB NAV */
.tnav{padding:0 32px;background:rgba(8,14,28,.5);border-bottom:1px solid var(--border);display:flex;gap:2px;overflow-x:auto}
.tbtn{padding:11px 18px;font-size:15px;font-weight:700;cursor:pointer;white-space:nowrap;
  border:none;background:transparent;color:var(--muted);border-bottom:2px solid transparent;transition:all .18s}
.tbtn:hover{color:#f1f5f9}
.tbtn.active{color:#a5b8ff;border-bottom-color:var(--blue)}

/* MAIN */
.main{padding:22px 32px 60px;max-width:1640px;margin:0 auto}
.sec{display:none}.sec.active{display:block}

/* METRIC CARDS */
.hg{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:13px;margin-bottom:22px}
.mc{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:16px;
  position:relative;overflow:hidden;transition:all .22s;backdrop-filter:blur(12px);animation:ci .4s ease both}
.mc:hover{border-color:var(--borderB);transform:translateY(-2px);box-shadow:0 0 24px rgba(94,127,255,.12)}
@keyframes ci{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.mc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--blue),transparent);opacity:0;transition:.3s}
.mc:hover::before{opacity:1}
.ml{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px}
.mv{font-size:25px;font-weight:900;font-family:'JetBrains Mono',monospace;line-height:1}
.ms{font-size:13px;color:var(--slate);margin-top:4px}
.mv.g{color:var(--green)}.mv.r{color:var(--red)}.mv.b{color:var(--blue)}
.mv.go{color:var(--gold)}.mv.p{color:var(--purple)}.mv.c{color:var(--cyan)}.mv.o{color:var(--orange)}

/* REC BANNER */
.rec{background:linear-gradient(135deg,rgba(251,191,36,.07),rgba(94,127,255,.07));
  border:1px solid rgba(251,191,36,.2);border-radius:var(--r);padding:20px 24px;
  margin-bottom:22px;display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:14px;animation:ci .5s ease both}
.rec-icon{font-size:35px;flex-shrink:0}
.rec-body{flex:1;min-width:180px}
.rec-tag{font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:var(--gold);margin-bottom:3px}
.rec-head{font-size:21px;font-weight:900;margin-bottom:3px}
.rec-sub{font-size:15px;color:var(--slate)}
.rec-stats{display:flex;gap:24px;flex-wrap:wrap}
.rst{text-align:center}
.rst-v{font-family:'JetBrains Mono',monospace;font-size:19px;font-weight:800;color:var(--cyan)}
.rst-l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-top:2px}

/* GRIDS */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}
@media(max-width:1100px){.g3{grid-template-columns:1fr 1fr}}
@media(max-width:800px){.g2,.g3{grid-template-columns:1fr}}

/* CHART CARD */
.cc{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px;
  backdrop-filter:blur(12px);transition:all .22s;animation:ci .4s ease both;margin-bottom:16px}
.cc:hover{border-color:var(--borderB)}
.cc.s2{grid-column:span 2}
.ch{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:5px}
.ct{font-size:16px;font-weight:800}
.cs{font-size:14px;color:var(--muted);margin-top:2px}
.cbdg{font-size:12px;font-weight:800;padding:3px 8px;border-radius:18px;text-transform:uppercase;
  letter-spacing:.8px;background:rgba(94,127,255,.12);color:#a5b8ff;border:1px solid rgba(94,127,255,.2);white-space:nowrap}
.cbdg.g{background:rgba(16,185,129,.12);color:#34d399;border-color:rgba(16,185,129,.2)}
.cbdg.r{background:rgba(239,68,68,.12);color:#f87171;border-color:rgba(239,68,68,.2)}
.cbdg.go{background:rgba(251,191,36,.12);color:#fbbf24;border-color:rgba(251,191,36,.2)}
.cbdg.p{background:rgba(162,89,247,.12);color:#c084fc;border-color:rgba(162,89,247,.2)}
.cw{position:relative}
@media(max-width:800px){.cc.s2{grid-column:span 1}}

/* SIGNALS */
.sgg{display:grid;grid-template-columns:1fr 1fr;gap:9px}
@media(max-width:650px){.sgg{grid-template-columns:1fr}}
.si{display:flex;align-items:center;justify-content:space-between;padding:11px 14px;
  border-radius:8px;background:rgba(255,255,255,.02);border:1px solid var(--border);transition:.18s}
.si:hover{background:rgba(255,255,255,.04);border-color:var(--borderB)}
.si-name{font-size:14px;font-weight:700;color:var(--slate)}
.si-val{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--muted)}
.si-b{font-size:12px;font-weight:800;padding:2px 8px;border-radius:16px;text-transform:uppercase;letter-spacing:.4px;white-space:nowrap}
.si-b.buy{background:rgba(16,185,129,.14);color:#34d399;border:1px solid rgba(16,185,129,.2)}
.si-b.sell{background:rgba(239,68,68,.14);color:#f87171;border:1px solid rgba(239,68,68,.2)}
.si-b.neu{background:rgba(148,163,184,.08);color:var(--slate);border:1px solid rgba(148,163,184,.12)}

/* SCORE BAR */
.score-wrap{margin-top:16px}
.score-lbl{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.score-track{background:rgba(255,255,255,.04);border-radius:6px;height:10px;overflow:hidden}
.score-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#ef4444,#fbbf24,#10b981);transition:width 1.2s ease}
.score-ends{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-top:3px}

/* SR LEVELS */
.sr-lvl{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;
  border-radius:7px;margin:3px 0;font-size:15px;transition:.18s}
.sr-lvl:hover{background:rgba(255,255,255,.03)}
.sr-lvl.res{border-left:3px solid rgba(239,68,68,.5)}
.sr-lvl.sup{border-left:3px solid rgba(16,185,129,.5)}
.sr-lvl.pvt{border-left:3px solid rgba(251,191,36,.65)}
.sr-lvl.cur{border-left:3px solid rgba(94,127,255,.65);background:rgba(94,127,255,.05)}
.sr-l{color:var(--slate);font-weight:600}
.sr-v{font-family:'JetBrains Mono',monospace;font-weight:800}
.sr-v.r{color:#f87171}.sr-v.s{color:#34d399}.sr-v.p{color:#fbbf24}.sr-v.c{color:#a5b8ff}

/* TABLES */
.fc-tbl,.st-tbl{width:100%;border-collapse:collapse;font-size:15px}
.fc-tbl th,.st-tbl th{padding:8px 10px;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:var(--muted);border-bottom:1px solid var(--border);text-align:center}
.fc-tbl th:first-child,.st-tbl th:first-child{text-align:left}
.fc-tbl td,.st-tbl td{padding:9px 10px;border-bottom:1px solid rgba(255,255,255,.025);text-align:center;font-family:'JetBrains Mono',monospace;font-size:14.5px;color:var(--slate)}
.fc-tbl td:first-child,.st-tbl td:first-child{text-align:left;font-family:'Inter',sans-serif;font-weight:700;color:#f1f5f9}
.fc-tbl tr.best td{background:rgba(16,185,129,.07)}
.fc-tbl tr.best td:first-child{color:var(--green)}
.fc-tbl tr:hover td,.st-tbl tr:hover td{background:rgba(255,255,255,.02)}
.best-tag{display:inline-block;font-size:11px;font-weight:800;padding:1px 6px;
  background:rgba(16,185,129,.2);color:#34d399;border-radius:8px;margin-left:6px;
  font-family:'Inter',sans-serif;text-transform:uppercase}

/* PROB BARS */
.pb-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.pb-dt{font-size:13px;color:var(--muted);width:72px;flex-shrink:0;font-family:'JetBrains Mono',monospace}
.pb-bg{flex:1;height:17px;border-radius:4px;background:rgba(255,255,255,.04);overflow:hidden}
.pb-fill{height:100%;border-radius:4px;display:flex;align-items:center;padding:0 6px;font-size:12px;font-weight:800;transition:width 1s ease}
.pb-pct{font-size:13px;font-family:'JetBrains Mono',monospace;width:36px;text-align:right;flex-shrink:0}

/* SEASON BARS */
.sb-w{display:flex;flex-direction:column;gap:8px}
.sb-row{display:flex;align-items:center;gap:9px}
.sb-lbl{width:70px;font-size:14px;font-weight:700;color:var(--slate);flex-shrink:0}
.sb-bg{flex:1;height:24px;border-radius:5px;background:rgba(255,255,255,.03);overflow:hidden}
.sb-fill{height:100%;border-radius:5px;display:flex;align-items:center;padding:0 7px;font-size:13px;font-weight:800;transition:width 1s ease}
.sb-fill.pos{background:linear-gradient(90deg,rgba(239,68,68,.42),rgba(239,68,68,.14));color:#f87171}
.sb-fill.neg{background:linear-gradient(90deg,rgba(16,185,129,.42),rgba(16,185,129,.14));color:#34d399}
.sb-val{width:55px;text-align:right;font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:800;flex-shrink:0}
.sb-val.pos{color:var(--red)}.sb-val.neg{color:var(--green)}

/* RISK ITEMS */
.ri{display:flex;align-items:center;justify-content:space-between;padding:11px 14px;
  border-radius:8px;background:rgba(255,255,255,.02);border:1px solid var(--border);margin-bottom:8px;transition:.18s}
.ri:hover{background:rgba(255,255,255,.04);border-color:var(--borderB)}
.ri-name{font-size:15px;font-weight:700}
.ri-sub{font-size:13px;color:var(--muted);margin-top:2px}
.ri-val{font-family:'JetBrains Mono',monospace;font-size:17px;font-weight:800}

/* HURST */
.hurst-track{width:100%;height:10px;border-radius:5px;
  background:linear-gradient(90deg,#10b981 0%,#fbbf24 40%,#ef4444 70%,#a855f7 100%);position:relative}
.hurst-needle{position:absolute;top:50%;transform:translate(-50%,-50%);
  width:3px;height:22px;border-radius:2px;background:#fff;box-shadow:0 0 8px rgba(255,255,255,.8);transition:left 1s ease}
.hurst-labels{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);font-weight:700;margin-top:5px}

/* DIRECTION TOGGLE */
.dir-toggle{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:10px;padding:3px;margin-left:auto}
.dir-btn{padding:5px 14px;border-radius:8px;border:none;background:transparent;color:var(--muted);font-size:14px;font-weight:700;cursor:pointer;transition:.18s;white-space:nowrap}
.dir-btn.active{background:linear-gradient(135deg,#5e7fff,#a259f7);color:#fff;box-shadow:0 2px 10px rgba(94,127,255,.3)}
.dir-btn:hover:not(.active){color:var(--slate);background:rgba(255,255,255,.05)}

/* COMPARE */
.cmp-grid{display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:19px;margin-bottom:19px}
@media(max-width:800px){.cmp-grid{grid-template-columns:1fr}}
.cmp-p{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px;transition:.22s;animation:ci .4s ease both}
.cmp-p.ep{border-top:2px solid rgba(107,143,255,.5)}
.cmp-p.up{border-top:2px solid rgba(74,222,128,.5)}
.cmp-title{font-size:16px;font-weight:900;margin-bottom:14px;display:flex;align-items:center;gap:7px}

/* EXPL BOX */
.expl{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:18px 22px;margin-bottom:16px;animation:ci .4s ease both}
.expl-title{font-size:15px;font-weight:800;margin-bottom:9px;color:var(--cyan);display:flex;align-items:center;gap:6px}
.expl-body{font-size:15px;line-height:1.8;color:var(--slate)}
.expl-body strong{color:#f1f5f9}

/* LOADING */
#ldr{position:fixed;inset:0;background:var(--bg0);z-index:9999;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;transition:opacity .5s}
.ldr-ico{font-size:47px;animation:spin 2s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.ldr-title{font-size:23px;font-weight:900;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.ldr-bar{width:260px;height:3px;border-radius:2px;background:rgba(255,255,255,.08)}
.ldr-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,var(--blue),var(--purple),var(--cyan));animation:lf 2.5s ease forwards}
@keyframes lf{from{width:0}to{width:100%}}
.ldr-msg{font-size:13px;color:var(--muted);font-family:'JetBrains Mono',monospace}

/* FOOTER */
.ftr{text-align:center;padding:28px;color:var(--muted);font-size:14px;border-top:1px solid var(--border);margin-top:28px}
.ftr strong{color:var(--slate)}

::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg1)}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--blue)}
@media(max-width:600px){.hdr,.ctrl,.tnav,.main{padding-left:14px;padding-right:14px}}
</style>
</head>
<body>

<div id="ldr">
  <div class="ldr-ico">📊</div>
  <div class="ldr-title">FX Quant Dashboard</div>
  <div class="ldr-bar"><div class="ldr-fill"></div></div>
  <div class="ldr-msg" id="ldr-msg">Initialising…</div>
</div>

<header class="hdr">
  <div style="display:flex;align-items:center;gap:12px">
    <div class="hdr-logo">₹</div>
    <div class="hdr-title">
      <h1><em>FX Quant</em> Dashboard</h1>
      <p>EUR/INR · USD/INR · ARIMA · Holt-Winters · Monte Carlo 5,000 paths · Multi-Duration</p>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <div class="hdr-rates" id="hdr-rates"></div>
    <div class="live-pip"><div class="pip-dot"></div>LIVE DATA</div>
  </div>
</header>

<!-- CONTROL BAR -->
<div class="ctrl">
  <span class="ctrl-lbl">Pair</span>
  <div class="pg">
    <button class="pl eur-a" data-pair="EURINR" onclick="setPair('EURINR',this)">🇪🇺 EUR/INR</button>
    <button class="pl" data-pair="USDINR" onclick="setPair('USDINR',this)">🇺🇸 USD/INR</button>
    <button class="pl" data-pair="GBPINR" onclick="setPair('GBPINR',this)">🇬🇧 GBP/INR</button>
    <button class="pl" data-pair="JPYINR" onclick="setPair('JPYINR',this)">🇯🇵 JPY/INR</button>
    <button class="pl" data-pair="CNYINR" onclick="setPair('CNYINR',this)">🇨🇳 CNY/INR</button>
    <button class="pl" data-pair="SGDINR" onclick="setPair('SGDINR',this)">🇸🇬 SGD/INR</button>
    <button class="pl" data-pair="HKDINR" onclick="setPair('HKDINR',this)">🇭🇰 HKD/INR</button>
    <button class="pl" data-pair="compare" onclick="setPair('compare',this)">⚖️ Compare</button>
  </div>
  <span class="ctrl-lbl" style="margin-left:10px">Forecast Window</span>
  <div class="pg">
    <button class="pl" data-dur="7"  onclick="setDur(7,this)">1 Week</button>
    <button class="pl dur-a" data-dur="14" onclick="setDur(14,this)">2 Weeks</button>
    <button class="pl" data-dur="30" onclick="setDur(30,this)">1 Month</button>
    <button class="pl" data-dur="60" onclick="setDur(60,this)">2 Months</button>
    <button class="pl" data-dur="90" onclick="setDur(90,this)">3 Months</button>
  </div>
  <div class="dir-toggle" title="Switch transfer direction">
    <button class="dir-btn active" id="dir-buy" onclick="setDirection('buy',this)">INR → FX</button>
    <button class="dir-btn" id="dir-sell" onclick="setDirection('sell',this)">FX → INR</button>
  </div>
  <span class="ctrl-ts" id="ctrl-ts"></span>
</div>

<!-- TAB NAV -->
<nav class="tnav">
  <button class="tbtn active" data-tab="overview"    onclick="showTab(this)">📈 Overview</button>
  <button class="tbtn"        data-tab="forecast"    onclick="showTab(this)">🔮 Forecast</button>
  <button class="tbtn"        data-tab="technical"   onclick="showTab(this)">⚙️ Technical</button>
  <button class="tbtn"        data-tab="statistics"  onclick="showTab(this)">📐 Statistics</button>
  <button class="tbtn"        data-tab="risk"        onclick="showTab(this)">🛡️ Risk & Transfer</button>
  <button class="tbtn"        data-tab="seasonality" onclick="showTab(this)">📅 Seasonality</button>
</nav>

<main class="main">
  <div id="sec-overview"    class="sec active"></div>
  <div id="sec-forecast"    class="sec"></div>
  <div id="sec-technical"   class="sec"></div>
  <div id="sec-statistics"  class="sec"></div>
  <div id="sec-risk"        class="sec"></div>
  <div id="sec-seasonality" class="sec"></div>
</main>

<footer class="ftr">
  <strong>FX Quant Dashboard</strong> · Data: Yahoo Finance · Models: ARIMA, Holt-Winters ETS, Monte Carlo GBM (5,000 paths) ·
  Indicators: RSI-14, MACD(12,26,9), Bollinger Bands(20,2σ), Stochastic(14,3), Williams %R, ATR-14, CCI-20, Z-Score · <span id="ftr-ts"></span><br>
  <span style="color:var(--dim);font-size:13px">⚠️ For analytical purposes only — not financial advice. Past patterns do not guarantee future results.</span>
</footer>

<script>
/* ═══════════════════════════════════════════
   EMBEDDED ANALYSIS DATA
   ═══════════════════════════════════════════ */
const ALL_DATA = DATA_PLACEHOLDER;

/* ═══════════════════════════════════════════
   STATE  — single source of truth
   ═══════════════════════════════════════════ */
const STATE = { pair:'EURINR', dur:14, tab:'overview', direction:'buy' }; // direction: 'buy'=INR→FX, 'sell'=FX→INR

const PAIR_META = {
  EURINR:{ label:'EUR/INR', flag:'🇪🇺', base:'EUR', clr:'#6b8fff', clrA:'rgba(107,143,255,', badge:'eur-a' },
  USDINR:{ label:'USD/INR', flag:'🇺🇸', base:'USD', clr:'#4ade80', clrA:'rgba(74,222,128,',  badge:'usd-a' },
  GBPINR:{ label:'GBP/INR', flag:'🇬🇧', base:'GBP', clr:'#d8b4e2', clrA:'rgba(216,180,226,', badge:'gbp-a' },
  JPYINR:{ label:'JPY/INR', flag:'🇯🇵', base:'JPY', clr:'#fca5a5', clrA:'rgba(252,165,165,', badge:'jpy-a' },
  CNYINR:{ label:'CNY/INR', flag:'🇨🇳', base:'CNY', clr:'#f87171', clrA:'rgba(248,113,113,', badge:'cny-a' },
  SGDINR:{ label:'SGD/INR', flag:'🇸🇬', base:'SGD', clr:'#fcd34d', clrA:'rgba(252,211,77,', badge:'sgd-a' },
  HKDINR:{ label:'HKD/INR', flag:'🇭🇰', base:'HKD', clr:'#a78bfa', clrA:'rgba(167,139,250,', badge:'hkd-a' },
};
const DUR_LABELS = {7:'1 Week',14:'2 Weeks',30:'1 Month',60:'2 Months',90:'3 Months'};
const SIGNAL_NAMES = {RSI:'RSI-14',MACD:'MACD(12,26,9)',BB:'Bollinger %B',ZScore:'Z-Score(20d)',Stochastic:'Stochastic(14,3)',SMA_Trend:'SMA-50 Trend'};

/* ═══════════════════════════════════════════
   UTILITIES
   ═══════════════════════════════════════════ */
const $ = id => document.getElementById(id);
const f4 = v => (v != null && !isNaN(v)) ? (+v).toFixed(4) : '—';
const f3 = v => (v != null && !isNaN(v)) ? (+v).toFixed(3) : '—';
const f2 = v => (v != null && !isNaN(v)) ? (+v).toFixed(2) : '—';

const CHARTS = {};
function killChart(id){ if(CHARTS[id]){ try{CHARTS[id].destroy();}catch(e){} delete CHARTS[id]; } }
function mkChart(id, cfg){
  killChart(id);
  const el = $('c-'+id);
  if(!el){ console.warn('Canvas not found: c-'+id); return null; }
  CHARTS[id] = new Chart(el.getContext('2d'), cfg);
  return CHARTS[id];
}

Chart.defaults.color='#475569';
Chart.defaults.font.family="'Inter',sans-serif";
Chart.defaults.font.size=14;
Chart.defaults.plugins.legend.labels.boxWidth=11;
Chart.defaults.plugins.legend.labels.padding=13;
Chart.defaults.plugins.tooltip.backgroundColor='#1a2440';
Chart.defaults.plugins.tooltip.borderColor='rgba(94,127,255,.22)';
Chart.defaults.plugins.tooltip.borderWidth=1;
Chart.defaults.plugins.tooltip.padding=10;
Chart.defaults.plugins.tooltip.cornerRadius=8;
Chart.defaults.plugins.tooltip.titleColor='#f1f5f9';
Chart.defaults.plugins.tooltip.bodyColor='#94a3b8';
Chart.defaults.elements.point.radius=0;
Chart.defaults.elements.point.hoverRadius=4;

const baseOpts = (yLbl='') => ({
  responsive:true, maintainAspectRatio:false,
  interaction:{mode:'index',intersect:false},
  plugins:{legend:{display:true}},
  scales:{
    x:{grid:{color:'rgba(255,255,255,.025)'},ticks:{maxTicksLimit:10,color:'#475569'},border:{color:'rgba(255,255,255,.04)'}},
    y:{grid:{color:'rgba(255,255,255,.03)'},ticks:{color:'#475569'},border:{color:'rgba(255,255,255,.04)'},
       title:{display:!!yLbl,text:yLbl,color:'#475569'}}
  }
});

function getData(pair, dur){
  pair = pair || STATE.pair;
  dur  = dur  || STATE.dur;
  try{ return ALL_DATA[pair][String(dur)]; } catch(e){ return null; }
}

/* ═══════════════════════════════════════════
   NAVIGATION  — all use STATE, no DOM parsing
   ═══════════════════════════════════════════ */
function showTab(btn){
  const tab = btn.dataset.tab;
  STATE.tab = tab;
  document.querySelectorAll('.tbtn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.sec').forEach(s => s.classList.remove('active'));
  btn.classList.add('active');
  $('sec-'+tab).classList.add('active');
  renderTab(tab);
}

function setPair(pair, btn){
  STATE.pair = pair;
  document.querySelectorAll('[data-pair]').forEach(b => b.classList.remove('active','eur-a','usd-a','gbp-a','jpy-a','cny-a','sgd-a','hkd-a'));
  btn.classList.add('active');
  if(pair !== 'compare') btn.classList.add(PAIR_META[pair]?.badge || 'active');
  rerender();
}

function setDur(dur, btn){
  STATE.dur = dur;
  document.querySelectorAll('[data-dur]').forEach(b => b.classList.remove('active','dur-a'));
  btn.classList.add('active','dur-a');
  rerender();
}

function setDirection(dir, btn){
  STATE.direction = dir;
  document.querySelectorAll('.dir-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  rerender();
}

/* ═══════════════════════════════════════════
   DIRECTION HELPERS
   ═══════════════════════════════════════════ */
const isSell = () => STATE.direction === 'sell';

/* Invert a single rate value for display */
function inv(v){ return (v!=null && !isNaN(v) && v!==0) ? 1/v : null; }

/* Invert an array of rate values */
function invA(arr){ return arr ? arr.map(v => (v!=null && !isNaN(v) && v!==0) ? 1/v : null) : []; }

/* Apply direction transform to a value */
function dv(v){ return isSell() ? inv(v) : v; }

/* Apply direction transform to an array */
function da(arr){ return isSell() ? invA(arr) : arr; }

/* Y-axis label */
function yLbl(base){ return isSell() ? `${base} per 1 INR` : `INR per ${base}`; }

/* Find the "best" transfer index in forecast ensemble (accounting for direction).
   INR→FX: want minimum (cheapest rate). FX→INR: want maximum (most INR back).
   When we invert the array, min(inverted) = max(original). So argmin always works
   on the display-transformed ensemble. */
function bestIdx(ensArr){
  const arr = da(ensArr);
  let best=0;
  arr.forEach((v,i)=>{ if(v!=null && v < arr[best]) best=i; });
  return best;
}

/* Probability: in INR→FX mode, prob_below_current = P(rate < today) = good.
   In FX→INR mode, P(inverted rate < today_inv) = P(orig > today) = 1 - prob_below_current */
function dirProb(p){ return isSell() ? (1 - p) : p; }

/* rerender: re-draws current tab with new STATE */
function rerender(){
  buildHeaderRates();
  if(STATE.pair === 'compare'){
    renderCompare();
  } else {
    renderTab(STATE.tab);
  }
}

/* ═══════════════════════════════════════════
   HEADER RATES
   ═══════════════════════════════════════════ */
function buildHeaderRates(){
  $('hdr-rates').innerHTML = Object.keys(PAIR_META).map(p => {
    const d = getData(p);
    if(!d) return '';
    const rate = dv(d.meta.current_rate);
    const lbl  = isSell() ? `INR/${PAIR_META[p].base}` : PAIR_META[p].label;
    return `<div class="hdr-rate-item">
      <div class="hdr-rate-label">${PAIR_META[p].flag} ${lbl}</div>
      <div class="hdr-rate-val">${f4(rate)}</div>
    </div>`;
  }).join('');
}

/* ═══════════════════════════════════════════
   TAB ROUTER
   ═══════════════════════════════════════════ */
function renderTab(tab){
  if(STATE.pair === 'compare'){ renderCompare(); return; }
  const d = getData();
  if(!d){
    $('sec-'+tab).innerHTML = '<div style="padding:60px;text-align:center;color:var(--muted)">No data for this selection.</div>';
    return;
  }
  switch(tab){
    case 'overview':    renderOverview(d);    break;
    case 'forecast':    renderForecast(d);    break;
    case 'technical':   renderTechnical(d);   break;
    case 'statistics':  renderStatistics(d);  break;
    case 'risk':        renderRisk(d);        break;
    case 'seasonality': renderSeasonality(d); break;
  }
}

/* ═══════════════════════════════════════════
   OVERVIEW
   ═══════════════════════════════════════════ */
function renderOverview(d){
  $('sec-overview').innerHTML = `
    <div id="ov-hero" class="hg"></div>
    <div id="ov-rec"  class="rec"></div>
    <div class="g2">
      <div class="cc s2">
        <div class="ch"><div><div class="ct">${d.meta.name} · Price History</div><div class="cs">Close · SMA-20 · SMA-50 · Bollinger Bands (20,2σ)</div></div><div class="cbdg" id="ov-hist-n">90D</div></div>
        <div class="cw" style="height:310px"><canvas id="c-price"></canvas></div>
      </div>
    </div>
    <div class="g2">
      <div class="cc">
        <div class="ch"><div><div class="ct">📡 Trade Signals</div><div class="cs">6 independent quant indicators</div></div><div class="cbdg" id="ov-sig-b">—</div></div>
        <div class="sgg" id="ov-sigs"></div>
        <div class="score-wrap">
          <div class="score-lbl">Composite Signal Score</div>
          <div class="score-track"><div id="ov-score-fill" class="score-fill" style="width:0%"></div></div>
          <div class="score-ends"><span>Sell</span><span>Neutral</span><span>Buy</span></div>
        </div>
      </div>
      <div class="cc">
        <div class="ch"><div><div class="ct">🏗️ Support &amp; Resistance</div><div class="cs">Pivot points · Fractal zones</div></div><div class="cbdg">PIVOTS</div></div>
        <div id="ov-sr"></div>
      </div>
    </div>`;
  buildHeroCards('ov-hero', d);
  buildRecBanner('ov-rec', d);
  mkPriceChart(d);
  buildSignals('ov-sigs','ov-sig-b','ov-score-fill', d);
  buildSR('ov-sr', d);
}

/* ═══════════════════════════════════════════
   FORECAST
   ═══════════════════════════════════════════ */
function renderForecast(d){
  const ord = d.arima.order;
  $('sec-forecast').innerHTML = `
    <div class="expl">
      <div class="expl-title">🧠 Ensemble Methodology — ${d.meta.forecast_label} Window · ${d.meta.name}</div>
      <div class="expl-body">Three models: <strong>ARIMA(${ord.join(',')}) [35%]</strong> · <strong>Holt-Winters ETS [35%]</strong> · <strong>Monte Carlo GBM [30%]</strong> with 5,000 paths. The <strong style="color:#34d399">green row</strong> = ensemble-minimum = optimal transfer window.</div>
    </div>
    <div class="g2">
      <div class="cc s2">
        <div class="ch"><div><div class="ct">${d.meta.forecast_label} Forecast — Historical + Ensemble</div><div class="cs">Gold = ensemble · Green dot = optimal date · Shaded = MC 5–95th pct</div></div><div class="cbdg go">ENSEMBLE</div></div>
        <div class="cw" style="height:330px"><canvas id="c-ens"></canvas></div>
      </div>
    </div>
    <div class="g2">
      <div class="cc">
        <div class="ch"><div><div class="ct">📅 Forecast Table · ${d.meta.forecast_label}</div><div class="cs">All models + ensemble — green = optimal window</div></div><div class="cbdg g">BEST HIGHLIGHTED</div></div>
        <div style="overflow-x:auto"><table class="fc-tbl"><thead><tr><th>Date</th><th>ARIMA</th><th>Holt-Winters</th><th>MC P50</th><th>Ensemble</th></tr></thead><tbody id="fc-tbody"></tbody></table></div>
      </div>
      <div class="cc">
        <div class="ch"><div><div class="ct">🎲 P(Rate &lt; Today) by Day</div><div class="cs">Probability rate is below current level — higher = cheaper to buy ${d.meta.base}</div></div><div class="cbdg">5,000 SIMS</div></div>
        <div id="fc-probs"></div>
      </div>
    </div>
    <div class="g2">
      <div class="cc">
        <div class="ch"><div><div class="ct">ARIMA(${ord.join(',')}) with 95% CI</div><div class="cs">Confidence interval bands</div></div><div class="cbdg">ARIMA</div></div>
        <div class="cw" style="height:250px"><canvas id="c-arima"></canvas></div>
      </div>
      <div class="cc">
        <div class="ch"><div><div class="ct">Monte Carlo Percentile Fan</div><div class="cs">P5 / P25 / P50 / P75 / P95</div></div><div class="cbdg p">GBM</div></div>
        <div class="cw" style="height:250px"><canvas id="c-mcfan"></canvas></div>
      </div>
    </div>`;
  mkEnsChart(d);
  buildFcTable('fc-tbody', d);
  buildProbBars('fc-probs', d);
  mkArimaChart(d);
  mkMCFanChart(d);
}

/* ═══════════════════════════════════════════
   TECHNICAL
   ═══════════════════════════════════════════ */
function renderTechnical(d){
  $('sec-technical').innerHTML = `
    <div class="g2">
      <div class="cc s2">
        <div class="ch"><div><div class="ct">RSI-14 — Relative Strength Index</div><div class="cs">Overbought &gt;70 · Oversold &lt;30 · Current: <span id="tc-rsi-v" style="font-family:'JetBrains Mono',monospace;color:#a5b8ff">—</span></div></div><div class="cbdg" id="tc-rsi-b">—</div></div>
        <div class="cw" style="height:185px"><canvas id="c-rsi"></canvas></div>
      </div>
    </div>
    <div class="g2">
      <div class="cc"><div class="ch"><div><div class="ct">MACD (12,26,9)</div><div class="cs">MACD · Signal · Histogram</div></div><div class="cbdg" id="tc-macd-b">—</div></div><div class="cw" style="height:220px"><canvas id="c-macd"></canvas></div></div>
      <div class="cc"><div class="ch"><div><div class="ct">Stochastic (14,3)</div><div class="cs">%K · %D · OB/OS zones</div></div><div class="cbdg" id="tc-stoch-b">—</div></div><div class="cw" style="height:220px"><canvas id="c-stoch"></canvas></div></div>
    </div>
    <div class="g2">
      <div class="cc"><div class="ch"><div><div class="ct">Bollinger %B &amp; Band Width</div><div class="cs">Squeeze · Position within bands</div></div><div class="cbdg" id="tc-bb-b">—</div></div><div class="cw" style="height:220px"><canvas id="c-bbw"></canvas></div></div>
      <div class="cc"><div class="ch"><div><div class="ct">Z-Score (20-day rolling)</div><div class="cs">Mean-reversion signal · Current: <span id="tc-z-v" style="font-family:'JetBrains Mono',monospace;color:#a5b8ff">—</span></div></div><div class="cbdg" id="tc-z-b">—</div></div><div class="cw" style="height:220px"><canvas id="c-zscore"></canvas></div></div>
    </div>
    <div class="g2">
      <div class="cc"><div class="ch"><div><div class="ct">Williams %R (14)</div><div class="cs">Momentum oscillator</div></div></div><div class="cw" style="height:200px"><canvas id="c-willr"></canvas></div></div>
      <div class="cc"><div class="ch"><div><div class="ct">ATR-14 — Average True Range</div><div class="cs">Daily volatility magnitude</div></div></div><div class="cw" style="height:200px"><canvas id="c-atr"></canvas></div></div>
    </div>
    <div class="cc"><div class="ch"><div><div class="ct">Daily Returns Distribution</div><div class="cs">Log-return histogram + fitted Normal curve</div></div><div class="cbdg" id="tc-dist-b">—</div></div><div class="cw" style="height:230px"><canvas id="c-dist"></canvas></div></div>`;
  mkRSI(d); mkMACD(d); mkStoch(d); mkBBW(d); mkZScore(d); mkWillR(d); mkATR(d); mkDist(d);
}

/* ═══════════════════════════════════════════
   STATISTICS
   ═══════════════════════════════════════════ */
function renderStatistics(d){
  $('sec-statistics').innerHTML = `
    <div class="g2">
      <div class="cc"><div class="ch"><div><div class="ct">📐 Return Distribution Stats</div><div class="cs">Properties of daily log-returns</div></div></div><table class="st-tbl" id="st-dist-tbl"></table></div>
      <div class="cc"><div class="ch"><div><div class="ct">🔬 Time-Series Tests</div><div class="cs">Stationarity · Normality · Autocorrelation</div></div></div><table class="st-tbl" id="st-ts-tbl"></table></div>
    </div>
    <div class="g2">
      <div class="cc">
        <div class="ch"><div><div class="ct">🌀 Hurst Exponent Analysis</div><div class="cs">R/S rescaled range — mean-reversion vs trending</div></div><div class="cbdg" id="st-h-b">—</div></div>
        <div style="text-align:center;padding:14px 0">
          <div style="font-size:41px;font-weight:900;font-family:'JetBrains Mono',monospace" id="st-h-val">—</div>
          <div style="font-size:15px;font-weight:800;margin:4px 0 14px" id="st-h-int">—</div>
          <div style="width:100%;max-width:400px;margin:0 auto">
            <div class="hurst-track"><div class="hurst-needle" id="st-h-ndl" style="left:50%"></div></div>
            <div class="hurst-labels"><span>Mean Rev (&lt;0.5)</span><span>Random Walk</span><span>Trending (&gt;0.5)</span></div>
          </div>
          <div style="font-size:14px;color:var(--slate);line-height:1.7;margin-top:12px;max-width:360px;margin-left:auto;margin-right:auto" id="st-h-exp"></div>
        </div>
      </div>
      <div class="cc"><div class="ch"><div><div class="ct">📈 ACF — Autocorrelation</div><div class="cs">Log-return serial correlation lags 1–10</div></div></div><div class="cw" style="height:210px"><canvas id="c-acf"></canvas></div></div>
    </div>
    <div class="cc"><div class="ch"><div><div class="ct">📊 Rolling Annualised Volatility</div><div class="cs">10d · 20d · 30d rolling bands</div></div></div><div class="cw" style="height:240px"><canvas id="c-vol"></canvas></div></div>`;
  buildStatTables(d); buildHurstViz(d); mkACF(d); mkVol(d);
}

/* ═══════════════════════════════════════════
   RISK
   ═══════════════════════════════════════════ */
function renderRisk(d){
  $('sec-risk').innerHTML = `
    <div class="expl">
      <div class="expl-title">💡 Transfer Strategy Guide</div>
      <div class="expl-body">${isSell()?`Transferring <strong>${d.meta.base} → INR</strong>: a <strong>higher ${d.meta.label} rate = better</strong> — more INR per ${d.meta.base}.`:`Transferring <strong>INR → ${d.meta.base}</strong>: a <strong>lower ${d.meta.label} rate = better</strong> — more ${d.meta.base} per Rupee.`} Ensemble models identify the <strong>optimal window</strong> across the <strong>${DUR_LABELS[STATE.dur]}</strong> horizon. Split the transfer across 3–5 days (DCA) to reduce single-point risk.</div>
    </div>
    <div id="rk-hero" class="hg"></div>
    <div class="g2">
      <div class="cc"><div class="ch"><div><div class="ct">📉 Risk Metrics</div><div class="cs">VaR, CVaR, Drawdown</div></div></div><div id="rk-items"></div></div>
      <div class="cc"><div class="ch"><div><div class="ct">💱 Transfer Scenarios (₹1 Lakh)</div><div class="cs">${d.meta.base} received under different rate assumptions</div></div></div><div id="rk-scen"></div></div>
    </div>
    <div class="cc"><div class="ch"><div><div class="ct">📉 Peak-to-Trough Drawdown</div><div class="cs">Largest rate retracements in dataset</div></div></div><div class="cw" style="height:230px"><canvas id="c-dd"></canvas></div></div>`;
  buildRiskHero('rk-hero', d);
  buildRiskItems('rk-items', d);
  buildRiskScenarios('rk-scen', d);
  mkDD(d);
}

/* ═══════════════════════════════════════════
   SEASONALITY
   ═══════════════════════════════════════════ */
function renderSeasonality(d){
  if(!d || !d.seasonality){
    $('sec-seasonality').innerHTML = '<div style="padding:60px;text-align:center;color:var(--muted)">Seasonality data unavailable for this window.</div>';
    return;
  }
  const SE = d.seasonality;
  const dowOK  = SE.dow   && Object.keys(SE.dow).length > 0;
  const monOK  = SE.monthly && Object.keys(SE.monthly).length > 0;
  const decOK  = SE.decomp_trend && SE.decomp_trend.length > 2;
  const isSell = STATE.direction === 'sell';
  const cheapDir = isSell
    ? `a <strong>positive mean return</strong> day = ${d.meta.base} is stronger — more INR when selling.`
    : `a <strong>negative mean return</strong> day = ${d.meta.base} is cheaper — ideal for INR→${d.meta.base} transfers.`;
  $('sec-seasonality').innerHTML = `
    <div class="expl">
      <div class="expl-title">📅 Seasonality in ${d.meta.name} · ${d.meta.forecast_label} forecast</div>
      <div class="expl-body">Empirical patterns by <strong>day-of-week</strong> and <strong>calendar month</strong>. ${cheapDir} Not guaranteed — treat as probabilistic edge.</div>
    </div>
    <div class="g2">
      <div class="cc">
        <div class="ch"><div><div class="ct">📆 Day-of-Week Effect</div><div class="cs">Mean daily log-return per weekday (all available history)</div></div></div>
        ${dowOK ? '<div class="sb-w" id="se-dow-bars"></div><div class="cw" style="height:190px;margin-top:16px"><canvas id="c-dow"></canvas></div>' : '<div style="padding:30px;text-align:center;color:var(--muted)">Insufficient data for this window — switch to 1 Month+</div>'}
      </div>
      <div class="cc">
        <div class="ch"><div><div class="ct">🗓️ Monthly Seasonality</div><div class="cs">Mean return by calendar month</div></div></div>
        ${monOK ? '<div class="cw" style="height:320px"><canvas id="c-month"></canvas></div>' : '<div style="padding:30px;text-align:center;color:var(--muted)">Insufficient data for this window — switch to 1 Month+</div>'}
      </div>
    </div>
    <div class="cc">
      <div class="ch"><div><div class="ct">🔁 Time-Series Decomposition</div><div class="cs">Multiplicative: Trend · Seasonal · Residual over the selected window</div></div></div>
      ${decOK ? '<div class="cw" style="height:260px"><canvas id="c-decomp"></canvas></div>' : '<div style="padding:30px;text-align:center;color:var(--muted)">Decomposition requires at least 30 data points — switch to 1 Month+</div>'}
    </div>`;
  if(dowOK){ buildDOWBars('se-dow-bars', d, isSell); mkDOW(d, isSell); }
  if(monOK){ mkMonth(d, isSell); }
  if(decOK){ mkDecomp(d); }
}

/* ═══════════════════════════════════════════
   COMPARE VIEW
   ═══════════════════════════════════════════ */
function renderCompare(){
  const tab = STATE.tab;
  const sec = $('sec-'+tab);
  
  let gridHtml = '<div class="cmp-grid">';
  Object.keys(PAIR_META).forEach(p => {
    const M = PAIR_META[p];
    gridHtml += `<div class="cmp-p" style="border-top:3px solid ${M.clr}"><div class="cmp-title">${M.flag} ${M.label}</div><div id="cmp-${p}"></div></div>`;
  });
  gridHtml += '</div>';

  sec.innerHTML = `
    <div class="expl">
      <div class="expl-title">⚖️ Side-by-Side: Multi-Currency Analysis · ${DUR_LABELS[STATE.dur]}</div>
      <div class="expl-body">All pairs analysed under identical models, same <strong>${DUR_LABELS[STATE.dur]}</strong> forecast window.</div>
    </div>
    ${gridHtml}
    <div class="g2">
      <div class="cc s2">
        <div class="ch"><div><div class="ct">Indexed Price Comparison</div><div class="cs">All pairs normalised to 100 at start of window</div></div><div class="cbdg">INDEXED</div></div>
        <div class="cw" style="height:350px"><canvas id="c-cmp"></canvas></div>
      </div>
    </div>`;

  const datasets = [];
  let labels = [];

  Object.keys(PAIR_META).forEach(p => {
    const d = getData(p);
    const el = $('cmp-' + p);
    if(!d||!el){ if(el) el.innerHTML='<p style="color:var(--muted)">No data</p>'; return; }
    
    const FC=d.forecast, ST=d.statistics, SG=d.signals, RK=d.risk, M=PAIR_META[p];
    const bi=bestIdx(FC.ensemble), bRate=dv(FC.ensemble[bi]), bDate=FC.dates[bi];
    const curD=dv(d.meta.current_rate);
    const saving = ((curD-bRate)/curD*100).toFixed(3);
    const unitLbl = isSell() ? `INR per 1 ${M.base}` : `${M.base} per ₹1L`;
    const unitVal = isSell() ? f2(d.meta.current_rate) : RK.units_per_lakh;
    el.innerHTML=`<table class="st-tbl">
      <tr><td>Current Rate</td><td style="color:${M.clr}">${f4(curD)}</td></tr>
      <tr><td>Best Transfer Date</td><td style="color:var(--green);font-weight:800">${bDate}</td></tr>
      <tr><td>Target Rate</td><td style="color:var(--green)">${f4(bRate)}</td></tr>
      <tr><td>Gain vs Now</td><td style="color:${parseFloat(saving)>0?'var(--green)':'var(--red)'}">${saving}%</td></tr>
      <tr><td>Ann. Volatility</td><td>${f2(ST.ann_vol_pct)}%</td></tr>
      <tr><td>Hurst Exp</td><td>${f3(ST.hurst_exp)}</td></tr>
      <tr><td>95% VaR (1-day)</td><td style="color:var(--red)">${f3(ST.var_95)}%</td></tr>
      <tr><td>Sharpe Ratio</td><td style="color:${ST.sharpe_ratio>0?'var(--green)':'var(--red)'}">${f3(ST.sharpe_ratio)}</td></tr>
      <tr><td>Signal</td><td style="color:${SG.composite.score>=50?'var(--green)':'var(--orange)'};font-weight:700">${SG.composite.recommendation}</td></tr>
      <tr><td>${unitLbl}</td><td style="color:${M.clr};font-weight:800">${unitVal}</td></tr>
    </table>`;

    const cRaw = d.history.close.filter(v=>v!=null);
    const c = isSell() ? cRaw.map(v=>1/v) : cRaw;
    if (c.length > 0) {
        const cn = c.map(v => +(v/c[0]*100).toFixed(4));
        datasets.push({
            label: `${M.label} (idx)`,
            data: cn,
            borderColor: M.clr,
            borderWidth: 2,
            fill: false
        });
        if (labels.length === 0) labels = d.history.dates;
    }
  });

  if (datasets.length > 0) {
    mkChart('cmp',{type:'line',data:{labels:labels,datasets:datasets},options:{...baseOpts('Indexed (base=100)'),plugins:{legend:{display:true,position:'bottom',labels:{color:'#a8b2d1',font:{size:14}}}}}});
  }
}

/* ═══════════════════════════════════════════
   BUILD FUNCTIONS
   ═══════════════════════════════════════════ */
function buildHeroCards(elId, d){
  const FC=d.forecast, ST=d.statistics, RK=d.risk;
  const bi   = bestIdx(FC.ensemble);
  const bDate= FC.dates[bi];
  const bRate= dv(FC.ensemble[bi]);
  const cur  = dv(d.meta.current_rate);
  const saving = ((cur - bRate)/cur*100).toFixed(3);
  const unitLbl = isSell() ? `INR per 1 ${d.meta.base}` : `${d.meta.base} per ₹1L`;
  const unitVal = isSell()
    ? f2(d.meta.current_rate)          // original rate = INR you receive per 1 FX
    : RK.units_per_lakh;
  const cards=[
    {l:'Current Rate',       v:f4(cur),    s:isSell()?`${d.meta.base} per INR`:d.meta.name,  c:'b'},
    {l:'Best Transfer Date', v:bDate,      s:'Rate: '+f4(bRate),                              c:'g'},
    {l:'Potential Gain',     v:saving+'%', s:'Ensemble vs current',                           c:parseFloat(saving)>0?'g':'r'},
    {l:unitLbl,              v:unitVal,    s:'At current rate',                                c:'go'},
    {l:'Ann. Volatility',    v:f2(ST.ann_vol_pct)+'%', s:'Log-return σ×√252',                c:'o'},
    {l:'Hurst Exponent',     v:f3(ST.hurst_exp),       s:ST.hurst_exp>0.6?'Trending':ST.hurst_exp<0.4?'Mean-Rev':'Random Walk', c:'p'},
    {l:'Sharpe Ratio',       v:f3(ST.sharpe_ratio),    s:'Annualised',                        c:ST.sharpe_ratio>0?'c':'r'},
    {l:'95% VaR (1-day)',    v:f3(ST.var_95)+'%',      s:'Max loss 19/20 days',               c:'r'},
  ];
  const g=$(elId); g.innerHTML='';
  cards.forEach((c,i)=>{
    const el=document.createElement('div'); el.className='mc'; el.style.animationDelay=(i*.05)+'s';
    el.innerHTML=`<div class="ml">${c.l}</div><div class="mv ${c.c}">${c.v}</div><div class="ms">${c.s}</div>`;
    g.appendChild(el);
  });
}

function buildRecBanner(elId, d){
  const SG=d.signals, FC=d.forecast, RK=d.risk, comp=SG.composite;
  const icons={'STRONG BUY NOW':'🚀','BUY (Favorable)':'✅','WAIT - May fall more':'⏳','HOLD/WAIT - Trending high':'🛑'};
  const bi2=bestIdx(FC.ensemble), bR=dv(FC.ensemble[bi2]), bD=FC.dates[bi2];
  const recLabel = isSell()
    ? (comp.score>=50?'STRONG SELL NOW':'SELL (Favorable)')
    : comp.recommendation;
  const unitV = isSell() ? f2(d.meta.current_rate)+' INR' : RK.units_per_lakh+' '+d.meta.base;
  const unitL = isSell() ? 'INR per '+d.meta.base : d.meta.base+'/₹1L';
  $(elId).innerHTML=`
    <div class="rec-icon">${icons[comp.recommendation]||'📊'}</div>
    <div class="rec-body">
      <div class="rec-tag">🏦 ${d.meta.flag} ${d.meta.name} · ${d.meta.forecast_label} · ${isSell()?'FX→INR':'INR→FX'}</div>
      <div class="rec-head">${recLabel}</div>
      <div class="rec-sub">Best window: <strong>${bD}</strong> @ <strong>${f4(bR)}</strong> · Score: <strong>${comp.score}%</strong></div>
    </div>
    <div class="rec-stats">
      <div class="rst"><div class="rst-v">${f4(bR)}</div><div class="rst-l">Target Rate</div></div>
      <div class="rst"><div class="rst-v">${bD}</div><div class="rst-l">Optimal Date</div></div>
      <div class="rst"><div class="rst-v">${unitV}</div><div class="rst-l">${unitL}</div></div>
      <div class="rst"><div class="rst-v">${f2(d.statistics.ann_vol_pct)}%</div><div class="rst-l">Ann. Vol</div></div>
    </div>`;
}

function buildSignals(sigsId,badgeId,barId, d){
  const SG=d.signals, g=$(sigsId); g.innerHTML='';
  Object.entries(SG).filter(([k])=>k!=='composite').forEach(([k,v])=>{
    const isBuy=v.signal.includes('BUY')||v.signal.includes('Bullish')||v.signal.includes('cheap');
    const isSell=v.signal.includes('SELL')||v.signal.includes('Bearish')||v.signal.includes('exp');
    const cls=isBuy?'buy':isSell?'sell':'neu';
    const el=document.createElement('div'); el.className='si';
    el.innerHTML=`<div><div class="si-name">${SIGNAL_NAMES[k]||k}</div><div class="si-val">${typeof v.value==='number'?v.value.toFixed(3):v.value}</div></div><div class="si-b ${cls}">${v.signal}</div>`;
    g.appendChild(el);
  });
  const comp=SG.composite;
  const badge=$(badgeId);
  if(badge){ badge.textContent=comp.recommendation; badge.className='cbdg '+(comp.score>=50?'g':comp.score>=33?'go':'r'); }
  setTimeout(()=>{ const b=$(barId); if(b) b.style.width=comp.score+'%'; },200);
}

function buildSR(elId, d){
  const SR=d.support_resistance;
  const cur=dv(SR.current);
  // When inverted, resistances become supports and vice versa
  const rawLevels=[
    {l:isSell()?'Support S3':'Resistance R3', v:dv(SR.R3), cls:isSell()?'sup':'res', vc:isSell()?'s':'r'},
    {l:isSell()?'Support S2':'Resistance R2', v:dv(SR.R2), cls:isSell()?'sup':'res', vc:isSell()?'s':'r'},
    {l:isSell()?'Support S1':'Resistance R1', v:dv(SR.R1), cls:isSell()?'sup':'res', vc:isSell()?'s':'r'},
    {l:'Pivot Point', v:dv(SR.pivot_pp||SR.pivot), cls:'pvt', vc:'p'},
    {l:'▶ Current',   v:cur,                        cls:'cur', vc:'c'},
    {l:isSell()?'Resistance R1':'Support S1', v:dv(SR.S1), cls:isSell()?'res':'sup', vc:isSell()?'r':'s'},
    {l:isSell()?'Resistance R2':'Support S2', v:dv(SR.S2), cls:isSell()?'res':'sup', vc:isSell()?'r':'s'},
    {l:isSell()?'Resistance R3':'Support S3', v:dv(SR.S3), cls:isSell()?'res':'sup', vc:isSell()?'r':'s'},
  ].filter(lv=>lv.v!=null).sort((a,b)=>b.v-a.v);
  const el=$(elId); el.innerHTML='';
  rawLevels.forEach(lv=>{
    const diff=((lv.v-cur)/cur*100).toFixed(2);
    const diffStr=lv.l.includes('Current')?'':` (${diff>0?'+':''}${diff}%)`;
    const d2=document.createElement('div'); d2.className=`sr-lvl ${lv.cls}`;
    d2.innerHTML=`<span class="sr-l">${lv.l}${diffStr}</span><span class="sr-v ${lv.vc}">${f4(lv.v)}</span>`;
    el.appendChild(d2);
  });
}

function buildFcTable(tbodyId, d){
  const FC=d.forecast, tb=$(tbodyId); tb.innerHTML='';
  const bi=bestIdx(FC.ensemble);
  FC.dates.forEach((dt,i)=>{
    const isBest=i===bi;
    const tr=document.createElement('tr'); if(isBest) tr.className='best';
    tr.innerHTML=`<td>${dt}${isBest?'<span class="best-tag">★ BEST</span>':''}</td>
      <td>${f4(dv(FC.arima[i]))}</td><td>${f4(dv(FC.hw[i]))}</td><td>${f4(dv(FC.mc_p50[i]))}</td>
      <td style="font-weight:800;color:${isBest?'#34d399':'#a5b8ff'}">${f4(dv(FC.ensemble[i]))}</td>`;
    tb.appendChild(tr);
  });
}

function buildProbBars(elId, d){
  const MC=d.monte_carlo, FC=d.forecast, el=$(elId); el.innerHTML='';
  const lbl = isSell() ? 'P(Rate > Today) — favourable for FX→INR' : 'P(Rate < Today) — favourable for INR→FX';
  el.innerHTML=`<div style="font-size:13px;color:var(--muted);margin-bottom:8px">${lbl}</div>`;
  FC.dates.forEach((dt,i)=>{
    const raw=(MC.prob_below_current[i]||0);
    const p=dirProb(raw)*100;
    const clr=p>55?'#10b981':p>45?'#f59e0b':'#ef4444';
    const row=document.createElement('div'); row.className='pb-row';
    row.innerHTML=`<div class="pb-dt">${dt.slice(5)}</div>
      <div class="pb-bg"><div class="pb-fill" style="width:${p.toFixed(1)}%;background:${clr}22;color:${clr}">${p>20?p.toFixed(0)+'%':''}</div></div>
      <div class="pb-pct" style="color:${clr}">${p.toFixed(1)}%</div>`;
    el.appendChild(row);
  });
}

function buildStatTables(d){
  const ST=d.statistics;
  const fillTbl=(id,rows)=>{
    const t=$(id); if(!t) return;
    t.innerHTML='<thead><tr><th>Metric</th><th>Value</th></tr></thead>';
    const tb=document.createElement('tbody');
    rows.forEach(([k,v])=>{ const tr=document.createElement('tr'); tr.innerHTML=`<td>${k}</td><td>${v}</td>`; tb.appendChild(tr); });
    t.appendChild(tb);
  };
  fillTbl('st-dist-tbl',[
    ['Daily Mean Return',(ST.mu_daily*100).toFixed(5)+'%'],
    ['Daily Std Dev (σ)',(ST.sigma_daily*100).toFixed(5)+'%'],
    ['Annualised Volatility',ST.ann_vol_pct.toFixed(3)+'%'],
    ['Skewness',ST.skewness.toFixed(4)],
    ['Excess Kurtosis',ST.excess_kurtosis.toFixed(4)],
    ['95% VaR (1-day)',ST.var_95.toFixed(4)+'%'],
    ['99% VaR (1-day)',ST.var_99.toFixed(4)+'%'],
    ['95% CVaR (Exp. Shortfall)',ST.cvar_95.toFixed(4)+'%'],
    ['Sharpe Ratio (ann.)',ST.sharpe_ratio.toFixed(4)],
  ]);
  fillTbl('st-ts-tbl',[
    ['ADF Test Statistic',ST.adf_stat.toFixed(4)],
    ['ADF p-value',ST.adf_p<0.001?'<0.001 ✓ STATIONARY':ST.adf_p.toFixed(6)],
    ['Jarque-Bera Stat',ST.jb_stat.toFixed(4)],
    ['JB p-value',ST.jb_p<0.001?'<0.001 ✗ NON-NORMAL':ST.jb_p.toFixed(6)],
    ['Hurst Exponent H',ST.hurst_exp.toFixed(4)],
    ['H Interpretation',ST.hurst_exp>0.6?'📈 Trending':ST.hurst_exp<0.4?'↩️ Mean-Reverting':'🎲 Random Walk'],
    ['ACF Lag-1',ST.acf_lags[0].toFixed(4)],
    ['ACF Lag-5',ST.acf_lags[4].toFixed(4)],
  ]);
}

function buildHurstViz(d){
  const H=d.statistics.hurst_exp;
  const el=$('st-h-val'); if(el){ el.textContent=H.toFixed(4); el.style.color=H>0.6?'#ef4444':H<0.4?'#10b981':'#fbbf24'; }
  const interp=H>0.6?'📈 Persistent Trend':H<0.4?'↩️ Mean-Reverting':'🎲 Random Walk';
  const iEl=$('st-h-int'); if(iEl){ iEl.textContent=interp; iEl.style.color=H>0.6?'#ef4444':H<0.4?'#10b981':'#fbbf24'; }
  const badge=$('st-h-b'); if(badge){ badge.textContent=interp; badge.className='cbdg '+(H>0.6?'r':H<0.4?'g':'go'); }
  const exp=$('st-h-exp'); if(exp) exp.innerHTML=H>0.6?'H&gt;0.5 → <strong>trending</strong>. Past moves persist. MACD/momentum strategies work better.':H<0.4?'H&lt;0.5 → <strong>mean-reverting</strong>. Prices snap back. Z-score/Bollinger strategies work better.':'H≈0.5 → <strong>random walk</strong>. Technical patterns have reduced predictive power.';
  setTimeout(()=>{ const n=$('st-h-ndl'); if(n) n.style.left=Math.min(95,Math.max(5,(H/1.2)*100))+'%'; },500);
}

/* buildDOWBars defined below with isSell parameter */

function buildRiskHero(elId, d){
  const RK=d.risk, FC=d.forecast;
  const bi=bestIdx(FC.ensemble), bRate=dv(FC.ensemble[bi]), bDate=FC.dates[bi];
  const curInv=dv(RK.current_rate);
  let cards;
  if(isSell()){
    cards=[
      {l:'INR per 1 '+d.meta.base+' (Now)', v:f4(RK.current_rate)+' INR', s:'Current rate', c:'g'},
      {l:'INR at Best Window',               v:f4(FC.ensemble[bi])+' INR', s:bDate,          c:'c'},
      {l:'Best 14d Move (hist.)',             v:'+'+RK.best_14d_move_pct.toFixed(2)+'%',     s:'Max gain in rolling window', c:'g'},
      {l:'Worst 14d Move (hist.)',            v:RK.worst_14d_move_pct.toFixed(2)+'%',        s:'Max loss in rolling window', c:'r'},
    ];
  } else {
    cards=[
      {l:d.meta.base+' per ₹1L (Now)', v:RK.units_per_lakh+' '+d.meta.base, s:'Current rate', c:'g'},
      {l:d.meta.base+' at Best Window', v:Math.round(100000/FC.ensemble[bi])+' '+d.meta.base,  s:bDate, c:'c'},
      {l:'Best 14d Move (hist.)',        v:'+'+RK.best_14d_move_pct.toFixed(2)+'%', s:'Max gain in rolling window', c:'g'},
      {l:'Worst 14d Move (hist.)',       v:RK.worst_14d_move_pct.toFixed(2)+'%',   s:'Max loss in rolling window', c:'r'},
    ];
  }
  const g=$(elId); g.innerHTML='';
  cards.forEach((c,i)=>{ const el=document.createElement('div'); el.className='mc'; el.style.animationDelay=(i*.06)+'s'; el.innerHTML=`<div class="ml">${c.l}</div><div class="mv ${c.c}">${c.v}</div><div class="ms">${c.s}</div>`; g.appendChild(el); });
}

function buildRiskItems(elId, d){
  const ST=d.statistics, RK=d.risk;
  const dca5lbl  = isSell() ? 'DCA Rate — 5d (inverted)' : 'DCA Rate (5-day avg)';
  const dca10lbl = isSell() ? 'DCA Rate — 10d (inverted)' : 'DCA Rate (10-day avg)';
  [
    {n:'95% VaR (1-day)',v:Math.abs(ST.var_95).toFixed(3)+'%',clr:'#ef4444',s:'Max loss 19/20 days'},
    {n:'99% VaR (1-day)',v:Math.abs(ST.var_99).toFixed(3)+'%',clr:'#ef4444',s:'Max loss 99/100 days'},
    {n:'95% CVaR / Expected Shortfall',v:Math.abs(ST.cvar_95).toFixed(3)+'%',clr:'#f97316',s:'Avg loss beyond VaR'},
    {n:'Max Drawdown (full period)',v:RK.max_drawdown_pct.toFixed(2)+'%',clr:'#ef4444',s:'Largest peak-to-trough'},
    {n:dca5lbl,  v:f4(dv(RK.dca_5d_rate)),  clr:'#10b981',s:'Cost-average over 5 days'},
    {n:dca10lbl, v:f4(dv(RK.dca_10d_rate)), clr:'#5e7fff',s:'Cost-average over 10 days'},
  ].forEach(it=>{ const el=$(elId), d2=document.createElement('div'); d2.className='ri'; d2.innerHTML=`<div><div class="ri-name">${it.n}</div><div class="ri-sub">${it.s}</div></div><div class="ri-val" style="color:${it.clr}">${it.v}</div>`; el.appendChild(d2); });
}

function buildRiskScenarios(elId, d){
  const RK=d.risk, FC=d.forecast, SR=d.support_resistance, MC=d.monte_carlo;
  const cur=RK.current_rate, amt=100000, B=d.meta.base;
  const bi=bestIdx(FC.ensemble);
  const scenarios=[
    {l:'Transfer NOW',                        rate:cur,                       clr:'#5e7fff'},
    {l:'Ensemble Best Window',                rate:FC.ensemble[bi],           clr:'#10b981'},
    {l:'DCA — 5-day avg',                     rate:RK.dca_5d_rate,            clr:'#21d0ec'},
    {l:isSell()?'At R1 (overbought)':'At S1 Support',  rate:SR.S1, clr:'#10b981'},
    {l:isSell()?'At S1 (oversold)':'At R1 (worst case)',rate:SR.R1, clr:'#ef4444'},
    {l:`MC P5 Bullish (day ${FC.dates.length})`,        rate:MC.p5[MC.p5.length-1], clr:'#fbbf24'},
  ];
  const el=$(elId); el.innerHTML='';
  scenarios.forEach(s=>{
    if(!s.rate) return;
    let units, diff, unitSym, rateLabel;
    if(isSell()){
      // FX→INR: how much INR do I get from selling 1 unit of foreign currency?
      units = s.rate.toFixed(2);          // INR received per 1 FX
      diff  = (s.rate - cur).toFixed(2);  // difference in INR
      unitSym = '₹';
      rateLabel = `${f4(dv(s.rate))} (${B}/INR display)`;
    } else {
      // INR→FX: how much FX do I get from ₹1L?
      units = (amt/s.rate).toFixed(0);
      diff  = ((amt/s.rate)-(amt/cur)).toFixed(0);
      unitSym = B[0];
      rateLabel = `Rate: ${f4(s.rate)}`;
    }
    const d2=document.createElement('div'); d2.className='ri';
    d2.innerHTML=`<div><div class="ri-name" style="color:${s.clr}">${s.l}</div><div class="ri-sub">${rateLabel}</div></div>
      <div style="text-align:right"><div class="ri-val" style="color:${s.clr}">${unitSym}${units}</div>
      <div style="font-size:13px;color:${parseFloat(diff)>=0?'#10b981':'#ef4444'};margin-top:1px">${parseFloat(diff)>=0?'+':''}${unitSym}${diff} vs now</div></div>`;
    el.appendChild(d2);
  });
}

/* ═══════════════════════════════════════════
   CHART BUILDERS
   ═══════════════════════════════════════════ */
const clr = d => PAIR_META[d.meta.pair]?.clr || '#5e7fff';

function mkPriceChart(d){
  const H=d.history, c=clr(d);
  // When inverted, BB upper becomes lower and vice versa
  const bbU = isSell() ? invA(H.bb_lower) : H.bb_upper;
  const bbL = isSell() ? invA(H.bb_upper) : H.bb_lower;
  mkChart('price',{type:'line',data:{labels:H.dates,datasets:[
    {label:'BB Upper',data:bbU,borderColor:'rgba(239,68,68,.3)',borderWidth:1,fill:false,borderDash:[4,3]},
    {label:'BB Lower',data:bbL,borderColor:'rgba(16,185,129,.3)',borderWidth:1,fill:'-1',backgroundColor:'rgba(94,127,255,.04)',borderDash:[4,3]},
    {label:'SMA-50', data:da(H.sma50), borderColor:'#f59e0b',borderWidth:1.5,fill:false},
    {label:'SMA-20', data:da(H.sma20), borderColor:'#a259f7',borderWidth:1.5,fill:false},
    {label:'EMA-21', data:da(H.ema21), borderColor:'#21d0ec',borderWidth:1.2,fill:false,borderDash:[2,2]},
    {label:d.meta.label, data:da(H.close), borderColor:c,borderWidth:2.5,fill:false},
  ]},options:{...baseOpts(yLbl(d.meta.base))}});
}

function mkEnsChart(d){
  const FC=d.forecast, H=d.history, c=clr(d);
  const n=Math.min(20,H.close.length);
  const hD=H.dates.slice(-n), hC=da(H.close.slice(-n));
  const lastC=hC[hC.length-1];
  const bi=bestIdx(FC.ensemble);
  const ensD=da([...FC.ensemble]);
  const ensJoined=[...Array(n-1).fill(null),lastC,...ensD];
  const pts=ensD.map((_,i)=>i===bi?7:0);
  // When inverted, P5 and P95 swap
  const p95data = da(isSell() ? [...FC.mc_p5]  : [...FC.mc_p95]);
  const p5data  = da(isSell() ? [...FC.mc_p95] : [...FC.mc_p5]);
  mkChart('ens',{type:'line',data:{labels:[...hD,...FC.dates],datasets:[
    {label:'MC P95',data:[...Array(n).fill(null),...p95data],borderColor:'transparent',backgroundColor:'rgba(94,127,255,.05)',fill:'+1',pointRadius:0},
    {label:'MC P5', data:[...Array(n).fill(null),...p5data], borderColor:'transparent',fill:false,pointRadius:0},
    {label:'Historical',data:[...hC,...Array(FC.dates.length).fill(null)],borderColor:c,borderWidth:2.5,fill:false},
    {label:'ARIMA',data:[...Array(n).fill(null),...da([...FC.arima])],borderColor:'#21d0ec',borderWidth:1.8,borderDash:[5,3],fill:false},
    {label:'Holt-Winters',data:[...Array(n).fill(null),...da([...FC.hw])],borderColor:'#a259f7',borderWidth:1.8,borderDash:[3,3],fill:false},
    {label:'MC P50',data:[...Array(n).fill(null),...da([...FC.mc_p50])],borderColor:'#94a3b8',borderWidth:1.3,borderDash:[2,2],fill:false},
    {label:'Ensemble',data:ensJoined,borderColor:'#fbbf24',borderWidth:3,fill:false,
     pointRadius:[...Array(n).fill(0),...pts],pointBackgroundColor:'#10b981',pointBorderColor:'#fff',pointBorderWidth:2},
  ]},options:{...baseOpts(yLbl(d.meta.base))}});
}

function mkArimaChart(d){
  const FC=d.forecast, AR=d.arima;
  // When inverted, upper CI becomes lower and vice versa
  const ciU = da(isSell() ? AR.lower_95 : AR.upper_95);
  const ciL = da(isSell() ? AR.upper_95 : AR.lower_95);
  mkChart('arima',{type:'line',data:{labels:FC.dates,datasets:[
    {label:'Upper 95%',data:ciU,borderColor:'rgba(239,68,68,.22)',backgroundColor:'rgba(239,68,68,.04)',fill:'+1',borderDash:[3,3],borderWidth:1},
    {label:'Lower 95%',data:ciL,borderColor:'rgba(16,185,129,.22)',fill:false,borderDash:[3,3],borderWidth:1},
    {label:'ARIMA',data:da([...FC.arima]),borderColor:'#21d0ec',borderWidth:2.5,fill:false,pointRadius:3,pointBackgroundColor:'#21d0ec'},
  ]},options:baseOpts(yLbl(d.meta.base))});
}

function mkMCFanChart(d){
  const FC=d.forecast, MC=d.monte_carlo;
  // Inverting flips the distribution: P5 becomes P95, P25 becomes P75
  const [dp95,dp75,dp50,dp25,dp5] = isSell()
    ? [invA(MC.p5),invA(MC.p25),invA(MC.p50),invA(MC.p75),invA(MC.p95)]
    : [MC.p95,MC.p75,MC.p50,MC.p25,MC.p5];
  mkChart('mcfan',{type:'line',data:{labels:FC.dates,datasets:[
    {label:'P95',data:dp95,borderColor:'rgba(239,68,68,.32)',backgroundColor:'rgba(239,68,68,.04)',fill:'+2',borderDash:[2,2],borderWidth:1},
    {label:'P75',data:dp75,borderColor:'rgba(251,191,36,.32)',backgroundColor:'rgba(251,191,36,.04)',fill:'+1',borderDash:[2,2],borderWidth:1},
    {label:'P50',data:dp50,borderColor:'#5e7fff',borderWidth:2.5,fill:false},
    {label:'P25',data:dp25,borderColor:'rgba(16,185,129,.32)',fill:false,borderDash:[2,2],borderWidth:1},
    {label:'P5', data:dp5, borderColor:'rgba(16,185,129,.32)',fill:false,borderDash:[2,2],borderWidth:1},
  ]},options:baseOpts(yLbl(d.meta.base))});
}

function mkRSI(d){
  const H=d.history, v=H.rsi14.filter(x=>x!=null).slice(-1)[0];
  const b=$('tc-rsi-b'), vEl=$('tc-rsi-v');
  if(vEl) vEl.textContent=v?v.toFixed(2):'—';
  if(b){ b.textContent=v>70?'OVERBOUGHT':v<30?'OVERSOLD':'NEUTRAL'; b.className='cbdg '+(v>70?'r':v<30?'g':''); }
  mkChart('rsi',{type:'line',data:{labels:H.dates,datasets:[
    {label:'RSI-14',data:H.rsi14,borderColor:'#a259f7',borderWidth:2,fill:false},
    {label:'RSI-7', data:H.rsi7, borderColor:'#21d0ec',borderWidth:1.3,borderDash:[3,3],fill:false},
  ]},options:{...baseOpts('RSI'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,min:0,max:100}}}});
}

function mkMACD(d){
  const H=d.history, lh=H.macd_hist.filter(v=>v!=null).slice(-1)[0];
  const b=$('tc-macd-b'); if(b){ b.textContent=lh>0?'BULLISH':'BEARISH'; b.className='cbdg '+(lh>0?'g':'r'); }
  mkChart('macd',{type:'bar',data:{labels:H.dates,datasets:[
    {label:'Histogram',data:H.macd_hist,backgroundColor:H.macd_hist.map(v=>v>0?'rgba(16,185,129,.48)':'rgba(239,68,68,.48)'),type:'bar'},
    {label:'MACD',  data:H.macd,    borderColor:'#5e7fff',borderWidth:2,fill:false,type:'line',pointRadius:0},
    {label:'Signal',data:H.macd_sig,borderColor:'#f59e0b',borderWidth:1.5,fill:false,type:'line',borderDash:[4,2],pointRadius:0},
  ]},options:baseOpts('MACD')});
}

function mkStoch(d){
  const H=d.history, lk=H.stoch_k.filter(v=>v!=null).slice(-1)[0];
  const b=$('tc-stoch-b'); if(b){ b.textContent=lk>80?'OVERBOUGHT':lk<20?'OVERSOLD':'NEUTRAL'; b.className='cbdg '+(lk>80?'r':lk<20?'g':''); }
  mkChart('stoch',{type:'line',data:{labels:H.dates,datasets:[
    {label:'%K',data:H.stoch_k,borderColor:'#21d0ec',borderWidth:2,fill:false},
    {label:'%D',data:H.stoch_d,borderColor:'#f59e0b',borderWidth:1.5,borderDash:[4,2],fill:false},
  ]},options:{...baseOpts('Stochastic'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,min:0,max:100}}}});
}

function mkBBW(d){
  const H=d.history;
  const bbW=H.dates.map((_,i)=>H.bb_upper[i]&&H.bb_lower[i]?((H.bb_upper[i]-H.bb_lower[i])/((H.bb_upper[i]+H.bb_lower[i])/2))*100:null);
  const lbp=H.bb_pct?H.bb_pct.filter(v=>v!=null).slice(-1)[0]:null;
  const b=$('tc-bb-b'); if(b){ b.textContent=lbp>0.9?'UPPER BAND':lbp<0.1?'LOWER BAND':'MID BAND'; b.className='cbdg '+(lbp>0.9?'r':lbp<0.1?'g':''); }
  mkChart('bbw',{type:'line',data:{labels:H.dates,datasets:[
    {label:'BB Width %',data:bbW,borderColor:'#5e7fff',borderWidth:2,fill:true,backgroundColor:'rgba(94,127,255,.06)',yAxisID:'y'},
    {label:'%B Pos',data:H.bb_pct,borderColor:'#fbbf24',borderWidth:1.5,fill:false,yAxisID:'y2',borderDash:[3,3]},
  ]},options:{...baseOpts('BB Width %'),scales:{x:baseOpts().scales.x,
    y:{...baseOpts().scales.y,position:'left'},y2:{...baseOpts().scales.y,position:'right',min:0,max:1,grid:{display:false}}}}});
}

function mkZScore(d){
  const H=d.history, lz=H.zscore.filter(v=>v!=null).slice(-1)[0];
  const zEl=$('tc-z-v'), b=$('tc-z-b');
  if(zEl) zEl.textContent=lz?lz.toFixed(3):'—';
  if(b){ b.textContent=lz<-2?'OVERSOLD':lz>2?'OVERBOUGHT':lz<-1?'CHEAP':lz>1?'EXPENSIVE':'FAIR VALUE'; b.className='cbdg '+(lz<-1?'g':lz>1?'r':''); }
  mkChart('zscore',{type:'line',data:{labels:H.dates,datasets:[{label:'Z-Score',data:H.zscore,borderColor:'#21d0ec',borderWidth:2,fill:true,
    backgroundColor:ctx=>{const g=ctx.chart.ctx.createLinearGradient(0,0,0,200);g.addColorStop(0,'rgba(239,68,68,.16)');g.addColorStop(.5,'rgba(33,208,236,.04)');g.addColorStop(1,'rgba(16,185,129,.16)');return g;}}
  ]},options:baseOpts('Z-Score')});
}

function mkWillR(d){
  const H=d.history;
  mkChart('willr',{type:'line',data:{labels:H.dates,datasets:[{label:'Williams %R',data:H.willr,borderColor:'#f59e0b',borderWidth:2,fill:false}]},
    options:{...baseOpts('%R'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,min:-100,max:0}}}});
}

function mkATR(d){
  const H=d.history;
  mkChart('atr',{type:'line',data:{labels:H.dates,datasets:[{label:'ATR-14',data:H.atr,borderColor:'#ef4444',borderWidth:2,fill:true,backgroundColor:'rgba(239,68,68,.06)'}]},
    options:baseOpts('ATR (INR)')});
}

function mkDist(d){
  const H=d.history, ST=d.statistics;
  const rets=H.returns.filter(v=>v!=null);
  const bins=40, mn=Math.min(...rets), mx=Math.max(...rets), bw=(mx-mn)/bins;
  const cnts=Array(bins).fill(0), lbs=[];
  for(let i=0;i<bins;i++) lbs.push((mn+i*bw).toFixed(2));
  rets.forEach(r=>{ const idx=Math.min(Math.floor((r-mn)/bw),bins-1); cnts[idx]++; });
  const mu=ST.mu_daily*100, sig=ST.sigma_daily*100;
  const nc=lbs.map(v=>{ const x=parseFloat(v); return (rets.length*bw)/(sig*Math.sqrt(2*Math.PI))*Math.exp(-.5*((x-mu)/sig)**2); });
  const b=$('tc-dist-b'), sk=ST.skewness;
  if(b){ b.textContent=sk>0.5?'RIGHT SKEWED':sk<-.5?'LEFT SKEWED':'NEAR NORMAL'; b.className='cbdg '+(Math.abs(sk)>0.5?'r':'g'); }
  mkChart('dist',{type:'bar',data:{labels:lbs,datasets:[
    {label:'Freq',data:cnts,backgroundColor:'rgba(94,127,255,.42)',borderColor:'rgba(94,127,255,.65)',borderWidth:1},
    {label:'Normal Fit',data:nc,type:'line',borderColor:'#fbbf24',borderWidth:2,fill:false,pointRadius:0},
  ]},options:{...baseOpts('Frequency'),plugins:{legend:{display:true}}}});
}

function mkACF(d){
  const ST=d.statistics, cb=1.96/Math.sqrt(d.meta.data_points||250);
  mkChart('acf',{type:'bar',data:{labels:Array.from({length:10},(_,i)=>`L${i+1}`),datasets:[
    {label:'ACF',data:ST.acf_lags,backgroundColor:ST.acf_lags.map(v=>Math.abs(v)>cb?'rgba(239,68,68,.5)':'rgba(94,127,255,.4)'),borderColor:ST.acf_lags.map(v=>Math.abs(v)>cb?'#ef4444':'#5e7fff'),borderWidth:1},
  ]},options:{...baseOpts('ACF'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,min:-.5,max:.5}},plugins:{legend:{display:false}}}});
}

function mkVol(d){
  const H=d.history;
  const roll=(n)=>H.dates.map((_,i)=>{ const sl=H.returns.slice(Math.max(0,i-n+1),i+1).filter(v=>v!=null); if(sl.length<3) return null; const mu=sl.reduce((a,b)=>a+b,0)/sl.length; return Math.sqrt(sl.reduce((a,b)=>a+(b-mu)**2,0)/sl.length)*Math.sqrt(252); });
  mkChart('vol',{type:'line',data:{labels:H.dates,datasets:[
    {label:'30d Vol',data:roll(30),borderColor:'#ef4444',borderWidth:1.5,fill:false,borderDash:[3,3]},
    {label:'20d Vol',data:H.vol20,borderColor:'#f59e0b',borderWidth:2,fill:false},
    {label:'10d Vol',data:roll(10),borderColor:'#21d0ec',borderWidth:2,fill:false},
  ]},options:baseOpts('Ann. Vol (%)')});
}

function mkDD(d){
  const H=d.history;
  // Use direction-adjusted close for drawdown
  const closeD = da(H.close);
  let peak=-Infinity;
  const dd=closeD.map(v=>{ if(v==null) return null; if(v>peak) peak=v; return((v-peak)/peak)*100; });
  mkChart('dd',{type:'line',data:{labels:H.dates,datasets:[{label:'Drawdown %',data:dd,borderColor:'#ef4444',borderWidth:2,fill:true,backgroundColor:'rgba(239,68,68,.07)'}]},
    options:{...baseOpts('Drawdown (%)'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,max:0}}}});
}

function buildDOWBars(elId, d, isSell){
  if(!d.seasonality||!d.seasonality.dow) return;
  const days=Object.entries(d.seasonality.dow);
  if(!days.length) return;
  const maxA=Math.max(...days.map(([,v])=>Math.abs(v.mean_return))); if(maxA===0) return;
  const el=$(elId); if(!el) return; el.innerHTML='';
  days.forEach(([day,val])=>{
    const v=val.mean_return;
    // INR->FX: lower rate (negative return) = good (green). FX->INR: higher rate (positive) = good (green).
    const isGood = isSell ? v>0 : v<0;
    const pct=(Math.abs(v)/maxA*80).toFixed(1);
    const row=document.createElement('div'); row.className='sb-row';
    row.innerHTML=`<div class="sb-lbl">${day.slice(0,3)}</div>
      <div class="sb-bg"><div class="sb-fill ${isGood?'neg':'pos'}" style="width:${pct}%"></div></div>
      <div class="sb-val ${isGood?'neg':'pos'}">${v>0?'+':''}${v.toFixed(3)}%</div>`;
    el.appendChild(row);
  });
}

function mkDOW(d, isSell){
  if(!d.seasonality||!d.seasonality.dow) return;
  const days=Object.entries(d.seasonality.dow);
  if(!days.length) return;
  mkChart('dow',{type:'bar',data:{labels:days.map(([k])=>k),datasets:[{label:'Mean Return %',data:days.map(([,v])=>v.mean_return),
    backgroundColor:days.map(([,v])=>(isSell?(v>0):(v<0))?'rgba(16,185,129,.52)':'rgba(239,68,68,.42)'),
    borderColor:days.map(([,v])=>(isSell?(v>0):(v<0))?'#10b981':'#ef4444'),borderWidth:1}]},
    options:{...baseOpts('Mean Return (%)'),plugins:{legend:{display:false}}}});
}

function mkMonth(d, isSell){
  if(!d.seasonality||!d.seasonality.monthly) return;
  const months=Object.entries(d.seasonality.monthly);
  if(!months.length) return;
  mkChart('month',{type:'bar',data:{labels:months.map(([k])=>k),datasets:[{label:'Mean Return %',data:months.map(([,v])=>v.mean_return),
    backgroundColor:months.map(([,v])=>(isSell?(v.mean_return>0):(v.mean_return<0))?'rgba(16,185,129,.52)':'rgba(239,68,68,.42)'),
    borderColor:months.map(([,v])=>(isSell?(v.mean_return>0):(v.mean_return<0))?'#10b981':'#ef4444'),borderWidth:1}]},
    options:{...baseOpts('Mean Return (%)'),plugins:{legend:{display:false}},indexAxis:'y'}});
}

function mkDecomp(d){
  const SE=d.seasonality;
  if(!SE||!SE.decomp_trend||SE.decomp_trend.length<3){ killChart('decomp'); return; }
  const N=SE.decomp_trend.length, lbs=d.history&&d.history.dates?d.history.dates.slice(-N):Array.from({length:N},(_,i)=>'D-'+(N-i));
  mkChart('decomp',{type:'line',data:{labels:lbs,datasets:[
    {label:'Trend',data:SE.decomp_trend,borderColor:'#5e7fff',borderWidth:2,fill:false},
    {label:'Seasonal',data:SE.decomp_seasonal,borderColor:'#fbbf24',borderWidth:1.5,borderDash:[3,3],fill:false},
    {label:'Residual',data:SE.decomp_residual,borderColor:'#a259f7',borderWidth:1,borderDash:[2,2],fill:false},
  ]},options:{...baseOpts('Component Value'),plugins:{legend:{display:true,position:'bottom',labels:{color:'#a8b2d1',font:{size:13}}}}}});
}

/* ═══════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded', () => {
  const msgs=['Loading EUR/INR data…','Loading USD/INR data…','Running ARIMA models…','Monte Carlo complete…','Building charts…','Ready!'];
  let mi=0; const mEl=$('ldr-msg');
  const iv=setInterval(()=>{ if(mi<msgs.length) mEl.textContent=msgs[mi++]; else clearInterval(iv); },400);
  setTimeout(()=>{
    clearInterval(iv);
    const ldr=$('ldr'); ldr.style.opacity='0';
    setTimeout(()=>{ ldr.style.display='none'; init(); }, 450);
  }, 2600);
});

function init(){
  buildHeaderRates();
  const ts = ALL_DATA?.EURINR?.['14']?.meta?.analysis_date || '';
  const tsEl=$('ctrl-ts'); if(tsEl) tsEl.textContent='Analysis: '+ts;
  const fEl=$('ftr-ts'); if(fEl) fEl.textContent=ts;
  renderTab('overview');
}
</script>
</body>
</html>"""

# Inject data
HTML = HTML.replace('DATA_PLACEHOLDER', data_json)
print(f"Final HTML size: {len(HTML)/1024:.1f} KB")

# Write the fixed standalone dashboard
with open('index.html', 'w') as f:
    f.write(HTML)

print("Written: index.html")
