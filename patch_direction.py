#!/usr/bin/env python3
"""
Comprehensive patch: makes INR→FX / FX→INR toggle actually transform
all data displayed — rates, charts, forecasts, risk scenarios, probability bars.
"""

with open('build_dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. Replace direction helper block with full inv() / invA() utilities
# ─────────────────────────────────────────────────────────────────────────────
OLD_DIR_HELPERS = """/* Helper: get display rate adjusted for direction */
function displayRate(rawRate){
  if(!rawRate || isNaN(rawRate)) return null;
  return STATE.direction === 'sell' ? +(1/rawRate).toFixed(6) : +rawRate;
}
function dirLabel(base){ return STATE.direction === 'sell' ? `INR/${base}` : `${base}/INR`; }
function dirDesc(base){
  return STATE.direction === 'sell'
    ? `Receiving INR from ${base} — a <strong>higher rate</strong> = more INR per ${base} = better.`
    : `Sending INR to buy ${base} — a <strong>lower rate</strong> = more ${base} per Rupee = better.`;
}"""

NEW_DIR_HELPERS = """/* ═══════════════════════════════════════════
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
function dirProb(p){ return isSell() ? (1 - p) : p; }"""

code = code.replace(OLD_DIR_HELPERS, NEW_DIR_HELPERS)

# ─────────────────────────────────────────────────────────────────────────────
# 2. buildHeaderRates — invert displayed rate
# ─────────────────────────────────────────────────────────────────────────────
OLD_HDR = """function buildHeaderRates(){
  $('hdr-rates').innerHTML = Object.keys(PAIR_META).map(p => {
    const d = getData(p);
    if(!d) return '';
    const cls = p === 'EURINR' ? 'eur-c' : 'usd-c';
    return `<div class="hdr-rate-item">
      <div class="hdr-rate-label">${PAIR_META[p].flag} ${PAIR_META[p].label}</div>
      <div class="hdr-rate-val ${cls}">${f4(d.meta.current_rate)}</div>
    </div>`;
  }).join('');
}"""

NEW_HDR = """function buildHeaderRates(){
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
}"""

code = code.replace(OLD_HDR, NEW_HDR)

# ─────────────────────────────────────────────────────────────────────────────
# 3. buildHeroCards — invert rates, recompute best date
# ─────────────────────────────────────────────────────────────────────────────
OLD_HERO = """function buildHeroCards(elId, d){
  const FC=d.forecast, ST=d.statistics, RK=d.risk;
  const saving = ((d.meta.current_rate-FC.best_transfer_rate)/d.meta.current_rate*100).toFixed(3);
  const cards=[
    {l:'Current Rate',           v:f4(d.meta.current_rate),         s:d.meta.name,            c:'b'},
    {l:'Best Transfer Date',     v:FC.best_transfer_date,           s:'Rate: '+f4(FC.best_transfer_rate), c:'g'},
    {l:'Potential Saving',       v:saving+'%',                      s:'Ensemble vs current',  c:parseFloat(saving)>0?'g':'r'},
    {l:d.meta.base+' per ₹1L',  v:RK.units_per_lakh,               s:'At current rate',      c:'go'},
    {l:'Ann. Volatility',        v:f2(ST.ann_vol_pct)+'%',          s:'Log-return σ×√252',    c:'o'},
    {l:'Hurst Exponent',         v:f3(ST.hurst_exp),                s:ST.hurst_exp>0.6?'Trending':ST.hurst_exp<0.4?'Mean-Rev':'Random Walk', c:'p'},
    {l:'Sharpe Ratio',           v:f3(ST.sharpe_ratio),             s:'Annualised',            c:ST.sharpe_ratio>0?'c':'r'},
    {l:'95% VaR (1-day)',        v:f3(ST.var_95)+'%',               s:'Max loss 19/20 days',  c:'r'},
  ];
  const g=$(elId); g.innerHTML='';
  cards.forEach((c,i)=>{
    const el=document.createElement('div'); el.className='mc'; el.style.animationDelay=(i*.05)+'s';
    el.innerHTML=`<div class="ml">${c.l}</div><div class="mv ${c.c}">${c.v}</div><div class="ms">${c.s}</div>`;
    g.appendChild(el);
  });
}"""

NEW_HERO = """function buildHeroCards(elId, d){
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
}"""

code = code.replace(OLD_HERO, NEW_HERO)

# ─────────────────────────────────────────────────────────────────────────────
# 4. buildRecBanner — invert rate in banner
# ─────────────────────────────────────────────────────────────────────────────
OLD_REC = """  $(elId).innerHTML=`
    <div class="rec-icon">${icons[comp.recommendation]||'📊'}</div>
    <div class="rec-body">
      <div class="rec-tag">🏦 ${d.meta.flag} ${d.meta.name} · ${d.meta.forecast_label}</div>
      <div class="rec-head">${comp.recommendation}</div>
      <div class="rec-sub">Best window: <strong>${FC.best_transfer_date}</strong> @ <strong>${f4(FC.best_transfer_rate)}</strong> · Score: <strong>${comp.score}%</strong></div>
    </div>
    <div class="rec-stats">
      <div class="rst"><div class="rst-v">${f4(FC.best_transfer_rate)}</div><div class="rst-l">Target Rate</div></div>
      <div class="rst"><div class="rst-v">${FC.best_transfer_date}</div><div class="rst-l">Optimal Date</div></div>
      <div class="rst"><div class="rst-v">${RK.units_per_lakh}</div><div class="rst-l">${d.meta.base}/₹1L</div></div>
      <div class="rst"><div class="rst-v">${f2(d.statistics.ann_vol_pct)}%</div><div class="rst-l">Ann. Vol</div></div>
    </div>`;"""

NEW_REC = """  const bi2=bestIdx(FC.ensemble), bR=dv(FC.ensemble[bi2]), bD=FC.dates[bi2];
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
    </div>`;"""

code = code.replace(OLD_REC, NEW_REC)

# ─────────────────────────────────────────────────────────────────────────────
# 5. buildSR — invert support/resistance levels
# ─────────────────────────────────────────────────────────────────────────────
OLD_SR = """function buildSR(elId, d){
  const SR=d.support_resistance, cur=SR.current;
  const levels=[
    {l:'Resistance R3',v:SR.R3,cls:'res',vc:'r'},{l:'Resistance R2',v:SR.R2,cls:'res',vc:'r'},{l:'Resistance R1',v:SR.R1,cls:'res',vc:'r'},
    {l:'Pivot Point',v:SR.pivot_pp||SR.pivot,cls:'pvt',vc:'p'},
    {l:'▶ Current',v:cur,cls:'cur',vc:'c'},
    {l:'Support S1',v:SR.S1,cls:'sup',vc:'s'},{l:'Support S2',v:SR.S2,cls:'sup',vc:'s'},{l:'Support S3',v:SR.S3,cls:'sup',vc:'s'},
  ].sort((a,b)=>b.v-a.v);
  const el=$(elId); el.innerHTML='';
  levels.forEach(lv=>{
    const diff=((lv.v-cur)/cur*100).toFixed(2);
    const diffStr=lv.l.includes('Current')?'':` (${diff>0?'+':''}${diff}%)`;
    const d2=document.createElement('div'); d2.className=`sr-lvl ${lv.cls}`;
    d2.innerHTML=`<span class="sr-l">${lv.l}${diffStr}</span><span class="sr-v ${lv.vc}">${f4(lv.v)}</span>`;
    el.appendChild(d2);
  });
}"""

NEW_SR = """function buildSR(elId, d){
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
}"""

code = code.replace(OLD_SR, NEW_SR)

# ─────────────────────────────────────────────────────────────────────────────
# 6. buildFcTable — invert all model values, re-highlight best
# ─────────────────────────────────────────────────────────────────────────────
OLD_FC = """function buildFcTable(tbodyId, d){
  const FC=d.forecast, tb=$(tbodyId); tb.innerHTML='';
  FC.dates.forEach((dt,i)=>{
    const isBest=i===FC.best_transfer_day_idx;
    const tr=document.createElement('tr'); if(isBest) tr.className='best';
    tr.innerHTML=`<td>${dt}${isBest?'<span class="best-tag">★ BEST</span>':''}</td>
      <td>${f4(FC.arima[i])}</td><td>${f4(FC.hw[i])}</td><td>${f4(FC.mc_p50[i])}</td>
      <td style="font-weight:800;color:${isBest?'#34d399':'#a5b8ff'}">${f4(FC.ensemble[i])}</td>`;
    tb.appendChild(tr);
  });
}"""

NEW_FC = """function buildFcTable(tbodyId, d){
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
}"""

code = code.replace(OLD_FC, NEW_FC)

# ─────────────────────────────────────────────────────────────────────────────
# 7. buildProbBars — flip probability in sell mode
# ─────────────────────────────────────────────────────────────────────────────
OLD_PROB = """function buildProbBars(elId, d){
  const MC=d.monte_carlo, FC=d.forecast, el=$(elId); el.innerHTML='';
  FC.dates.forEach((dt,i)=>{
    const p=(MC.prob_below_current[i]||0)*100;
    const clr=p>55?'#10b981':p>45?'#f59e0b':'#ef4444';
    const row=document.createElement('div'); row.className='pb-row';
    row.innerHTML=`<div class="pb-dt">${dt.slice(5)}</div>
      <div class="pb-bg"><div class="pb-fill" style="width:${p.toFixed(1)}%;background:${clr}22;color:${clr}">${p>20?p.toFixed(0)+'%':''}</div></div>
      <div class="pb-pct" style="color:${clr}">${p.toFixed(1)}%</div>`;
    el.appendChild(row);
  });
}"""

NEW_PROB = """function buildProbBars(elId, d){
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
}"""

code = code.replace(OLD_PROB, NEW_PROB)

# ─────────────────────────────────────────────────────────────────────────────
# 8. buildRiskHero — invert rates and recompute
# ─────────────────────────────────────────────────────────────────────────────
OLD_RK_HERO = """function buildRiskHero(elId, d){
  const RK=d.risk, FC=d.forecast;
  const cards=[
    {l:d.meta.base+' per ₹1L (Now)', v:RK.units_per_lakh+' '+d.meta.base, s:'Current rate', c:'g'},
    {l:d.meta.base+' at Best Window', v:Math.round(100000/FC.best_transfer_rate)+' '+d.meta.base, s:FC.best_transfer_date, c:'c'},
    {l:'Best 14d Move (historical)', v:'+'+RK.best_14d_move_pct.toFixed(2)+'%', s:'Max gain in rolling window', c:'g'},
    {l:'Worst 14d Move (historical)', v:RK.worst_14d_move_pct.toFixed(2)+'%', s:'Max loss in rolling window', c:'r'},
  ];
  const g=$(elId); g.innerHTML='';
  cards.forEach((c,i)=>{ const el=document.createElement('div'); el.className='mc'; el.style.animationDelay=(i*.06)+'s'; el.innerHTML=`<div class="ml">${c.l}</div><div class="mv ${c.c}">${c.v}</div><div class="ms">${c.s}</div>`; g.appendChild(el); });
}"""

NEW_RK_HERO = """function buildRiskHero(elId, d){
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
}"""

code = code.replace(OLD_RK_HERO, NEW_RK_HERO)

# ─────────────────────────────────────────────────────────────────────────────
# 9. buildRiskItems — invert DCA rates
# ─────────────────────────────────────────────────────────────────────────────
OLD_RK_ITEMS = """  [
    {n:'95% VaR (1-day)',v:Math.abs(ST.var_95).toFixed(3)+'%',clr:'#ef4444',s:'Max loss 19/20 days'},
    {n:'99% VaR (1-day)',v:Math.abs(ST.var_99).toFixed(3)+'%',clr:'#ef4444',s:'Max loss 99/100 days'},
    {n:'95% CVaR / Expected Shortfall',v:Math.abs(ST.cvar_95).toFixed(3)+'%',clr:'#f97316',s:'Avg loss beyond VaR'},
    {n:'Max Drawdown (full period)',v:RK.max_drawdown_pct.toFixed(2)+'%',clr:'#ef4444',s:'Largest peak-to-trough'},
    {n:'DCA Rate (5-day avg)',v:f4(RK.dca_5d_rate),clr:'#10b981',s:'Cost-average over 5 days'},
    {n:'DCA Rate (10-day avg)',v:f4(RK.dca_10d_rate),clr:'#5e7fff',s:'Cost-average over 10 days'},
  ].forEach(it=>{ const el=$(elId), d2=document.createElement('div'); d2.className='ri'; d2.innerHTML=`<div><div class="ri-name">${it.n}</div><div class="ri-sub">${it.s}</div></div><div class="ri-val" style="color:${it.clr}">${it.v}</div>`; el.appendChild(d2); });"""

NEW_RK_ITEMS = """  const dca5lbl  = isSell() ? 'DCA Rate — 5d (inverted)' : 'DCA Rate (5-day avg)';
  const dca10lbl = isSell() ? 'DCA Rate — 10d (inverted)' : 'DCA Rate (10-day avg)';
  [
    {n:'95% VaR (1-day)',v:Math.abs(ST.var_95).toFixed(3)+'%',clr:'#ef4444',s:'Max loss 19/20 days'},
    {n:'99% VaR (1-day)',v:Math.abs(ST.var_99).toFixed(3)+'%',clr:'#ef4444',s:'Max loss 99/100 days'},
    {n:'95% CVaR / Expected Shortfall',v:Math.abs(ST.cvar_95).toFixed(3)+'%',clr:'#f97316',s:'Avg loss beyond VaR'},
    {n:'Max Drawdown (full period)',v:RK.max_drawdown_pct.toFixed(2)+'%',clr:'#ef4444',s:'Largest peak-to-trough'},
    {n:dca5lbl,  v:f4(dv(RK.dca_5d_rate)),  clr:'#10b981',s:'Cost-average over 5 days'},
    {n:dca10lbl, v:f4(dv(RK.dca_10d_rate)), clr:'#5e7fff',s:'Cost-average over 10 days'},
  ].forEach(it=>{ const el=$(elId), d2=document.createElement('div'); d2.className='ri'; d2.innerHTML=`<div><div class="ri-name">${it.n}</div><div class="ri-sub">${it.s}</div></div><div class="ri-val" style="color:${it.clr}">${it.v}</div>`; el.appendChild(d2); });"""

code = code.replace(OLD_RK_ITEMS, NEW_RK_ITEMS)

# ─────────────────────────────────────────────────────────────────────────────
# 10. buildRiskScenarios — invert rates and flip units calculation
# ─────────────────────────────────────────────────────────────────────────────
OLD_RK_SCEN = """function buildRiskScenarios(elId, d){
  const RK=d.risk, FC=d.forecast, SR=d.support_resistance, MC=d.monte_carlo;
  const cur=RK.current_rate, amt=100000, B=d.meta.base;
  [
    {l:'Transfer NOW',rate:cur,clr:'#5e7fff'},
    {l:'Ensemble Best Window',rate:FC.best_transfer_rate,clr:'#10b981'},
    {l:'DCA — 5-day avg',rate:RK.dca_5d_rate,clr:'#21d0ec'},
    {l:'At S1 Support',rate:SR.S1,clr:'#10b981'},
    {l:'At R1 (worst case)',rate:SR.R1,clr:'#ef4444'},
    {l:`MC P5 Bullish (day ${FC.dates.length})`,rate:MC.p5[MC.p5.length-1],clr:'#fbbf24'},
  ].forEach(s=>{
    const units=(amt/s.rate).toFixed(0), diff=(amt/s.rate-amt/cur).toFixed(0);
    const el=$(elId), d2=document.createElement('div'); d2.className='ri';
    d2.innerHTML=`<div><div class="ri-name" style="color:${s.clr}">${s.l}</div><div class="ri-sub">Rate: ${f4(s.rate)}</div></div>
      <div style="text-align:right"><div class="ri-val" style="color:${s.clr}">${B[0]}${units}</div>
      <div style="font-size:13px;color:${parseFloat(diff)>=0?'#10b981':'#ef4444'};margin-top:1px">${parseFloat(diff)>=0?'+':''}${B[0]}${diff} vs now</div></div>`;
    el.appendChild(d2);
  });
}"""

NEW_RK_SCEN = """function buildRiskScenarios(elId, d){
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
}"""

code = code.replace(OLD_RK_SCEN, NEW_RK_SCEN)

# ─────────────────────────────────────────────────────────────────────────────
# 11. mkPriceChart — invert all price series
# ─────────────────────────────────────────────────────────────────────────────
OLD_PRICE = """function mkPriceChart(d){
  const H=d.history, c=clr(d);
  mkChart('price',{type:'line',data:{labels:H.dates,datasets:[
    {label:'BB Upper',data:H.bb_upper,borderColor:'rgba(239,68,68,.3)',borderWidth:1,fill:false,borderDash:[4,3]},
    {label:'BB Lower',data:H.bb_lower,borderColor:'rgba(16,185,129,.3)',borderWidth:1,fill:'-1',backgroundColor:'rgba(94,127,255,.04)',borderDash:[4,3]},
    {label:'SMA-50', data:H.sma50, borderColor:'#f59e0b',borderWidth:1.5,fill:false},
    {label:'SMA-20', data:H.sma20, borderColor:'#a259f7',borderWidth:1.5,fill:false},
    {label:'EMA-21', data:H.ema21, borderColor:'#21d0ec',borderWidth:1.2,fill:false,borderDash:[2,2]},
    {label:d.meta.label,data:H.close,borderColor:c,borderWidth:2.5,fill:false},
  ]},options:{...baseOpts('INR per '+d.meta.base)}});
}"""

NEW_PRICE = """function mkPriceChart(d){
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
}"""

code = code.replace(OLD_PRICE, NEW_PRICE)

# ─────────────────────────────────────────────────────────────────────────────
# 12. mkEnsChart — invert history and all forecast bands
# ─────────────────────────────────────────────────────────────────────────────
OLD_ENS = """function mkEnsChart(d){
  const FC=d.forecast, H=d.history, c=clr(d);
  const n=Math.min(20,H.close.length);
  const hD=H.dates.slice(-n), hC=H.close.slice(-n);
  const lastC=hC[hC.length-1];
  const ensJoined=[...Array(n-1).fill(null),lastC,...FC.ensemble];
  const pts=FC.ensemble.map((_,i)=>i===FC.best_transfer_day_idx?7:0);
  mkChart('ens',{type:'line',data:{labels:[...hD,...FC.dates],datasets:[
    {label:'MC P95',data:[...Array(n).fill(null),...FC.mc_p95],borderColor:'transparent',backgroundColor:'rgba(94,127,255,.05)',fill:'+1',pointRadius:0},
    {label:'MC P5', data:[...Array(n).fill(null),...FC.mc_p5], borderColor:'transparent',fill:false,pointRadius:0},
    {label:'Historical',data:[...hC,...Array(FC.dates.length).fill(null)],borderColor:c,borderWidth:2.5,fill:false},
    {label:'ARIMA',data:[...Array(n).fill(null),...FC.arima],borderColor:'#21d0ec',borderWidth:1.8,borderDash:[5,3],fill:false},
    {label:'Holt-Winters',data:[...Array(n).fill(null),...FC.hw],borderColor:'#a259f7',borderWidth:1.8,borderDash:[3,3],fill:false},
    {label:'MC P50',data:[...Array(n).fill(null),...FC.mc_p50],borderColor:'#94a3b8',borderWidth:1.3,borderDash:[2,2],fill:false},
    {label:'Ensemble',data:ensJoined,borderColor:'#fbbf24',borderWidth:3,fill:false,
     pointRadius:[...Array(n).fill(0),...pts],pointBackgroundColor:'#10b981',pointBorderColor:'#fff',pointBorderWidth:2},
  ]},options:{...baseOpts('INR per '+d.meta.base)}});
}"""

NEW_ENS = """function mkEnsChart(d){
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
}"""

code = code.replace(OLD_ENS, NEW_ENS)

# ─────────────────────────────────────────────────────────────────────────────
# 13. mkArimaChart — invert forecast + CI bands (upper/lower swap)
# ─────────────────────────────────────────────────────────────────────────────
OLD_ARIMA = """function mkArimaChart(d){
  const FC=d.forecast, AR=d.arima;
  mkChart('arima',{type:'line',data:{labels:FC.dates,datasets:[
    {label:'Upper 95%',data:AR.upper_95,borderColor:'rgba(239,68,68,.22)',backgroundColor:'rgba(239,68,68,.04)',fill:'+1',borderDash:[3,3],borderWidth:1},
    {label:'Lower 95%',data:AR.lower_95,borderColor:'rgba(16,185,129,.22)',fill:false,borderDash:[3,3],borderWidth:1},
    {label:'ARIMA',data:FC.arima,borderColor:'#21d0ec',borderWidth:2.5,fill:false,pointRadius:3,pointBackgroundColor:'#21d0ec'},
  ]},options:baseOpts('INR per '+d.meta.base)});
}"""

NEW_ARIMA = """function mkArimaChart(d){
  const FC=d.forecast, AR=d.arima;
  // When inverted, upper CI becomes lower and vice versa
  const ciU = da(isSell() ? AR.lower_95 : AR.upper_95);
  const ciL = da(isSell() ? AR.upper_95 : AR.lower_95);
  mkChart('arima',{type:'line',data:{labels:FC.dates,datasets:[
    {label:'Upper 95%',data:ciU,borderColor:'rgba(239,68,68,.22)',backgroundColor:'rgba(239,68,68,.04)',fill:'+1',borderDash:[3,3],borderWidth:1},
    {label:'Lower 95%',data:ciL,borderColor:'rgba(16,185,129,.22)',fill:false,borderDash:[3,3],borderWidth:1},
    {label:'ARIMA',data:da([...FC.arima]),borderColor:'#21d0ec',borderWidth:2.5,fill:false,pointRadius:3,pointBackgroundColor:'#21d0ec'},
  ]},options:baseOpts(yLbl(d.meta.base))});
}"""

code = code.replace(OLD_ARIMA, NEW_ARIMA)

# ─────────────────────────────────────────────────────────────────────────────
# 14. mkMCFanChart — invert all percentile bands (P5↔P95, P25↔P75)
# ─────────────────────────────────────────────────────────────────────────────
OLD_MC = """function mkMCFanChart(d){
  const FC=d.forecast, MC=d.monte_carlo;
  mkChart('mcfan',{type:'line',data:{labels:FC.dates,datasets:[
    {label:'P95',data:MC.p95,borderColor:'rgba(239,68,68,.32)',backgroundColor:'rgba(239,68,68,.04)',fill:'+2',borderDash:[2,2],borderWidth:1},
    {label:'P75',data:MC.p75,borderColor:'rgba(251,191,36,.32)',backgroundColor:'rgba(251,191,36,.04)',fill:'+1',borderDash:[2,2],borderWidth:1},
    {label:'P50',data:MC.p50,borderColor:'#5e7fff',borderWidth:2.5,fill:false},
    {label:'P25',data:MC.p25,borderColor:'rgba(16,185,129,.32)',fill:false,borderDash:[2,2],borderWidth:1},
    {label:'P5', data:MC.p5, borderColor:'rgba(16,185,129,.32)',fill:false,borderDash:[2,2],borderWidth:1},
  ]},options:baseOpts('INR per '+d.meta.base)});
}"""

NEW_MC = """function mkMCFanChart(d){
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
}"""

code = code.replace(OLD_MC, NEW_MC)

# ─────────────────────────────────────────────────────────────────────────────
# 15. mkDD — invert history for drawdown chart
# ─────────────────────────────────────────────────────────────────────────────
OLD_DD = """function mkDD(d){
  const H=d.history; let peak=-Infinity;
  const dd=H.close.map(v=>{ if(v==null) return null; if(v>peak) peak=v; return((v-peak)/peak)*100; });
  mkChart('dd',{type:'line',data:{labels:H.dates,datasets:[{label:'Drawdown %',data:dd,borderColor:'#ef4444',borderWidth:2,fill:true,backgroundColor:'rgba(239,68,68,.07)'}]},
    options:{...baseOpts('Drawdown (%)'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,max:0}}}});
}"""

NEW_DD = """function mkDD(d){
  const H=d.history;
  // Use direction-adjusted close for drawdown
  const closeD = da(H.close);
  let peak=-Infinity;
  const dd=closeD.map(v=>{ if(v==null) return null; if(v>peak) peak=v; return((v-peak)/peak)*100; });
  mkChart('dd',{type:'line',data:{labels:H.dates,datasets:[{label:'Drawdown %',data:dd,borderColor:'#ef4444',borderWidth:2,fill:true,backgroundColor:'rgba(239,68,68,.07)'}]},
    options:{...baseOpts('Drawdown (%)'),scales:{...baseOpts().scales,y:{...baseOpts().scales.y,max:0}}}});
}"""

code = code.replace(OLD_DD, NEW_DD)

# ─────────────────────────────────────────────────────────────────────────────
# 16. renderCompare — invert rates in the compare grid
# ─────────────────────────────────────────────────────────────────────────────
OLD_CMP_ROW = """    const FC=d.forecast, ST=d.statistics, SG=d.signals, RK=d.risk, M=PAIR_META[p];
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
    </table>`;"""

NEW_CMP_ROW = """    const FC=d.forecast, ST=d.statistics, SG=d.signals, RK=d.risk, M=PAIR_META[p];
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
    </table>`;"""

code = code.replace(OLD_CMP_ROW, NEW_CMP_ROW)

# Also update the indexed comparison chart to use inverted data
OLD_CMP_IDX = """    const c = d.history.close.filter(v=>v!=null);
    if (c.length > 0) {
        const cn = c.map(v => +(v/c[0]*100).toFixed(4));"""

NEW_CMP_IDX = """    const cRaw = d.history.close.filter(v=>v!=null);
    const c = isSell() ? cRaw.map(v=>1/v) : cRaw;
    if (c.length > 0) {
        const cn = c.map(v => +(v/c[0]*100).toFixed(4));"""

code = code.replace(OLD_CMP_IDX, NEW_CMP_IDX)

# ─────────────────────────────────────────────────────────────────────────────
# 17. renderRisk description text
# ─────────────────────────────────────────────────────────────────────────────
OLD_RISK_DESC = """      <div class="expl-body">Transferring <strong>INR → ${d.meta.base}</strong>: a <strong>lower ${d.meta.label} rate = better</strong> — more ${d.meta.base} per Rupee. Ensemble models identify the <strong>optimal window</strong> across the <strong>${DUR_LABELS[STATE.dur]}</strong> horizon. Split the transfer across 3–5 days (DCA) to reduce single-point risk.</div>"""

NEW_RISK_DESC = """      <div class="expl-body">${isSell()?`Transferring <strong>${d.meta.base} → INR</strong>: a <strong>higher ${d.meta.label} rate = better</strong> — more INR per ${d.meta.base}.`:`Transferring <strong>INR → ${d.meta.base}</strong>: a <strong>lower ${d.meta.label} rate = better</strong> — more ${d.meta.base} per Rupee.`} Ensemble models identify the <strong>optimal window</strong> across the <strong>${DUR_LABELS[STATE.dur]}</strong> horizon. Split the transfer across 3–5 days (DCA) to reduce single-point risk.</div>"""

code = code.replace(OLD_RISK_DESC, NEW_RISK_DESC)

# ─────────────────────────────────────────────────────────────────────────────
# Write output
# ─────────────────────────────────────────────────────────────────────────────
with open('build_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch applied successfully.")
