import sys

with open('build_dashboard.py', 'r') as f:
    code = f.read()

# 1. Update PAIR_META
meta_old = """const PAIR_META = {
  EURINR:{ label:'EUR/INR', flag:'🇪🇺', base:'EUR', clr:'#6b8fff', clrA:'rgba(107,143,255,', badge:'eur-a' },
  USDINR:{ label:'USD/INR', flag:'🇺🇸', base:'USD', clr:'#4ade80', clrA:'rgba(74,222,128,',  badge:'usd-a' },
};"""
meta_new = """const PAIR_META = {
  EURINR:{ label:'EUR/INR', flag:'🇪🇺', base:'EUR', clr:'#6b8fff', clrA:'rgba(107,143,255,', badge:'eur-a' },
  USDINR:{ label:'USD/INR', flag:'🇺🇸', base:'USD', clr:'#4ade80', clrA:'rgba(74,222,128,',  badge:'usd-a' },
  GBPINR:{ label:'GBP/INR', flag:'🇬🇧', base:'GBP', clr:'#d8b4e2', clrA:'rgba(216,180,226,', badge:'gbp-a' },
  JPYINR:{ label:'JPY/INR', flag:'🇯🇵', base:'JPY', clr:'#fca5a5', clrA:'rgba(252,165,165,', badge:'jpy-a' },
  CNYINR:{ label:'CNY/INR', flag:'🇨🇳', base:'CNY', clr:'#f87171', clrA:'rgba(248,113,113,', badge:'cny-a' },
  SGDINR:{ label:'SGD/INR', flag:'🇸🇬', base:'SGD', clr:'#fcd34d', clrA:'rgba(252,211,77,', badge:'sgd-a' },
  HKDINR:{ label:'HKD/INR', flag:'🇭🇰', base:'HKD', clr:'#a78bfa', clrA:'rgba(167,139,250,', badge:'hkd-a' },
};"""
code = code.replace(meta_old, meta_new)

# 2. Update CSS styles for badges
css_old = ".pl.usd-a{background:rgba(74,222,128,.14);color:#4ade80;border:1px solid rgba(74,222,128,.28)}"
css_new = """.pl.usd-a{background:rgba(74,222,128,.14);color:#4ade80;border:1px solid rgba(74,222,128,.28)}
.pl.gbp-a{background:rgba(216,180,226,.14);color:#d8b4e2;border:1px solid rgba(216,180,226,.28)}
.pl.jpy-a{background:rgba(252,165,165,.14);color:#fca5a5;border:1px solid rgba(252,165,165,.28)}
.pl.cny-a{background:rgba(248,113,113,.14);color:#f87171;border:1px solid rgba(248,113,113,.28)}
.pl.sgd-a{background:rgba(252,211,77,.14);color:#fcd34d;border:1px solid rgba(252,211,77,.28)}
.pl.hkd-a{background:rgba(167,139,250,.14);color:#a78bfa;border:1px solid rgba(167,139,250,.28)}"""
code = code.replace(css_old, css_new)

# 3. Update grid CSS
grid_old = ".cmp-grid{display:grid;grid-template-columns:1fr 1fr;gap:19px;margin-bottom:19px}"
grid_new = ".cmp-grid{display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:19px;margin-bottom:19px}"
code = code.replace(grid_old, grid_new)

# fallback for old grid without px modifications
grid_old_alt = ".cmp-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}"
code = code.replace(grid_old_alt, grid_new)

# 4. Update the Buttons
btn_old = """    <button class="pl eur-a" data-pair="EURINR" onclick="setPair('EURINR',this)">🇪🇺 EUR/INR</button>
    <button class="pl" data-pair="USDINR" onclick="setPair('USDINR',this)">🇺🇸 USD/INR</button>"""
btn_new = """    <button class="pl eur-a" data-pair="EURINR" onclick="setPair('EURINR',this)">🇪🇺 EUR/INR</button>
    <button class="pl" data-pair="USDINR" onclick="setPair('USDINR',this)">🇺🇸 USD/INR</button>
    <button class="pl" data-pair="GBPINR" onclick="setPair('GBPINR',this)">🇬🇧 GBP/INR</button>
    <button class="pl" data-pair="JPYINR" onclick="setPair('JPYINR',this)">🇯🇵 JPY/INR</button>
    <button class="pl" data-pair="CNYINR" onclick="setPair('CNYINR',this)">🇨🇳 CNY/INR</button>
    <button class="pl" data-pair="SGDINR" onclick="setPair('SGDINR',this)">🇸🇬 SGD/INR</button>
    <button class="pl" data-pair="HKDINR" onclick="setPair('HKDINR',this)">🇭🇰 HKD/INR</button>"""
code = code.replace(btn_old, btn_new)

# 5. Header rates
hr_old = "$('hdr-rates').innerHTML = ['EURINR','USDINR'].map(p => {"
hr_new = "$('hdr-rates').innerHTML = Object.keys(PAIR_META).map(p => {"
code = code.replace(hr_old, hr_new)

# 6. classList remove all pairs
cr_old = "document.querySelectorAll('[data-pair]').forEach(b => b.classList.remove('active','eur-a','usd-a'));"
cr_new = "document.querySelectorAll('[data-pair]').forEach(b => b.classList.remove('active','eur-a','usd-a','gbp-a','jpy-a','cny-a','sgd-a','hkd-a'));"
code = code.replace(cr_old, cr_new)

# 7. Render compare tab
rc_old = """function renderCompare(){
  const tab = STATE.tab;
  const sec = $('sec-'+tab);
  sec.innerHTML = `
    <div class="expl">
      <div class="expl-title">⚖️ Side-by-Side: EUR/INR vs USD/INR · ${DUR_LABELS[STATE.dur]}</div>
      <div class="expl-body">Both pairs analysed under identical models, same <strong>${DUR_LABELS[STATE.dur]}</strong> forecast window. Use this to decide which currency to prioritise for your international transfer.</div>
    </div>
    <div class="cmp-grid">
      <div class="cmp-p ep"><div class="cmp-title">🇪🇺 EUR/INR</div><div id="cmp-eur"></div></div>
      <div class="cmp-p up"><div class="cmp-title">🇺🇸 USD/INR</div><div id="cmp-usd"></div></div>
    </div>
    <div class="g2">
      <div class="cc s2">
        <div class="ch"><div><div class="ct">Indexed Price Comparison — Last 90 Days</div><div class="cs">Both pairs normalised to 100 at start of window</div></div><div class="cbdg">INDEXED</div></div>
        <div class="cw" style="height:293px"><canvas id="c-cmp"></canvas></div>
      </div>
    </div>`;
  ['EURINR','USDINR'].forEach(p => {
    const d = getData(p);
    const el = $(p === 'EURINR' ? 'cmp-eur' : 'cmp-usd');
    if(!d||!el){ if(el) el.innerHTML='<p style="color:var(--muted)">No data</p>'; return; }
    const FC=d.forecast, ST=d.statistics, SG=d.signals, RK=d.risk, M=PAIR_META[p];
    const saving = ((d.meta.current_rate-FC.best_transfer_rate)/d.meta.current_rate*100).toFixed(3);
    el.innerHTML=`<table class="st-tbl">
      <tr><td>Current Rate</td><td style="color:${M.clr}">${f4(d.meta.current_rate)}</td></tr>
      <tr><td>Best Transfer Date</td><td style="color:var(--green);font-weight:800">${FC.best_transfer_date}</td></tr>
      <tr><td>Target Rate (Ensemble)</td><td style="color:var(--green)">${f4(FC.best_transfer_rate)}</td></tr>
      <tr><td>Saving vs Now</td><td style="color:${parseFloat(saving)>0?'var(--green)':'var(--red)'}">${saving}%</td></tr>
      <tr><td>Ann. Volatility</td><td>${f2(ST.ann_vol_pct)}%</td></tr>
      <tr><td>Hurst Exponent</td><td>${f3(ST.hurst_exp)} (${ST.hurst_exp>0.6?'Trending':ST.hurst_exp<0.4?'Mean-Rev':'Random Walk'})</td></tr>
      <tr><td>95% VaR (1-day)</td><td style="color:var(--red)">${f3(ST.var_95)}%</td></tr>
      <tr><td>Sharpe Ratio</td><td style="color:${ST.sharpe_ratio>0?'var(--green)':'var(--red)'}">${f3(ST.sharpe_ratio)}</td></tr>
      <tr><td>Signal</td><td style="color:${SG.composite.score>=50?'var(--green)':'var(--orange)'};font-weight:700">${SG.composite.recommendation}</td></tr>
      <tr><td>${M.base} per ₹1 Lakh</td><td style="color:${M.clr};font-weight:800">${RK.units_per_lakh}</td></tr>
    </table>`;
  });
  // Indexed price chart
  const eur=getData('EURINR'), usd=getData('USDINR');
  if(eur && usd){
    const ec=eur.history.close.filter(v=>v!=null), uc=usd.history.close.filter(v=>v!=null);
    const en=ec.map(v=>+(v/ec[0]*100).toFixed(4)), un=uc.map(v=>+(v/uc[0]*100).toFixed(4));
    const lbs=eur.history.dates;
    mkChart('cmp',{type:'line',data:{labels:lbs,datasets:[
      {label:'EUR/INR (indexed)',data:en,borderColor:'#6b8fff',borderWidth:2.5,fill:false},
      {label:'USD/INR (indexed)',data:un,borderColor:'#4ade80',borderWidth:2.5,fill:false},
    ]},options:{...baseOpts('Indexed (base=100)'),plugins:{legend:{display:true}}}});
  }
}"""
rc_new = """function renderCompare(){
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
    const saving = ((d.meta.current_rate-FC.best_transfer_rate)/d.meta.current_rate*100).toFixed(3);
    el.innerHTML=`<table class="st-tbl">
      <tr><td>Current Rate</td><td style="color:${M.clr}">${f4(d.meta.current_rate)}</td></tr>
      <tr><td>Best Transfer Date</td><td style="color:var(--green);font-weight:800">${FC.best_transfer_date}</td></tr>
      <tr><td>Target Rate</td><td style="color:var(--green)">${f4(FC.best_transfer_rate)}</td></tr>
      <tr><td>Saving vs Now</td><td style="color:${parseFloat(saving)>0?'var(--green)':'var(--red)'}">${saving}%</td></tr>
      <tr><td>Ann. Volatility</td><td>${f2(ST.ann_vol_pct)}%</td></tr>
      <tr><td>Hurst Exp</td><td>${f3(ST.hurst_exp)}</td></tr>
      <tr><td>95% VaR (1-day)</td><td style="color:var(--red)">${f3(ST.var_95)}%</td></tr>
      <tr><td>Sharpe Ratio</td><td style="color:${ST.sharpe_ratio>0?'var(--green)':'var(--red)'}">${f3(ST.sharpe_ratio)}</td></tr>
      <tr><td>Signal</td><td style="color:${SG.composite.score>=50?'var(--green)':'var(--orange)'};font-weight:700">${SG.composite.recommendation}</td></tr>
      <tr><td>${M.base} per ₹1L</td><td style="color:${M.clr};font-weight:800">${RK.units_per_lakh}</td></tr>
    </table>`;

    const c = d.history.close.filter(v=>v!=null);
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
}"""
code = code.replace(rc_old, rc_new)

with open('build_dashboard.py', 'w') as f:
    f.write(code)
