import json
import os
from datetime import datetime

def sparkline_svg(prices, color, width=220, height=80):
    prices = [p for p in prices if p is not None]
    if len(prices) < 2:
        return ""
    mn, mx = min(prices), max(prices)
    rng    = mx - mn or 1
    xs     = [i / (len(prices)-1) * width for i in range(len(prices))]
    ys     = [height - (p - mn) / rng * height for p in prices]
    pts    = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    fill   = f"0,{height} " + pts + f" {width},{height}"
    uid    = color.replace('#','')
    return f"""<svg viewBox="0 0 {width} {height}"
    xmlns="http://www.w3.org/2000/svg" style="width:100%;height:{height}px">
  <defs>
    <linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="{color}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
  <polygon points="{fill}" fill="url(#g{uid})"/>
  <polyline points="{pts}" fill="none" stroke="{color}"
            stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
</svg>"""


def seasonality_mini_svg(dow_data, direction='inr_to_fx', width=160, height=32):
    days   = ['Monday','Tuesday','Wednesday','Thursday','Friday']
    values = []
    for d in days:
        v = dow_data.get(d, {}).get('mean_return', 0.0) or 0.0
        values.append(-v if direction == 'fx_to_inr' else v)

    mx  = max([abs(v) for v in values] + [1e-9])
    bw  = width / len(days) - 3
    mid = height / 2
    bars = []
    for i, v in enumerate(values):
        x      = i * (bw + 3)
        bar_h  = abs(v) / mx * (height / 2 - 2)
        y      = mid - bar_h if v >= 0 else mid
        color  = "#00D084" if v >= 0 else "#FF4757"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
            f'height="{bar_h:.1f}" rx="2" fill="{color}" opacity="0.85"/>'
        )
    day_labels = "MTWTF"
    labels = ''.join(
        f'<text x="{{i*(bw+3)+bw/2:.1f}}" y="{{height+9:.1f}}" '
        f'text-anchor="middle" font-size="8" fill="#4A5568">{{day_labels[i]}}</text>'
    ).replace("{i*(bw+3)+bw/2:.1f}", "{x}").replace("{height+9:.1f}", "{y}").replace("{day_labels[i]}", "{label}")
    # Fix the string formatting since list comprehension inside f-string is tricky in old python.
    labels = ''
    for i in range(5):
        xl = i*(bw+3)+bw/2
        yl = height+9
        labels += f'<text x="{xl:.1f}" y="{yl:.1f}" text-anchor="middle" font-size="8" fill="#4A5568">{day_labels[i]}</text>'
    
    return (
        f'<svg viewBox="0 0 {width} {height+12}" '
        f'xmlns="http://www.w3.org/2000/svg" style="width:{width}px;height:{height+12}px">'
        f'<line x1="0" y1="{mid:.1f}" x2="{width}" y2="{mid:.1f}" '
        f'stroke="rgba(255,255,255,0.08)" stroke-width="1"/>'
        f'{"".join(bars)}{labels}</svg>'
    )


def get_color(pair):
    c = {"EUR": "#4A9EFF", "USD": "#00D084", "GBP": "#A78BFA", "JPY": "#FF6B35", 
         "CNY": "#FF4757", "SGD": "#F5A623", "HKD": "#26C6DA"}
    return c.get(pair[:3], "#4A9EFF")


def get_flag(pair):
    f = {"EUR": "🇪🇺", "USD": "🇺🇸", "GBP": "🇬🇧", "JPY": "🇯🇵", 
         "CNY": "🇨🇳", "SGD": "🇸🇬", "HKD": "🇭🇰"}
    return f.get(pair[:3], "🏳️")


def main():
    try:
        with open('multi_data.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    meta = data.get('_meta', {})
    gen_at = meta.get('generated_at', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    pairs = [p for p in ["EURINR", "USDINR", "GBPINR", "JPYINR", "CNYINR", "SGDINR", "HKDINR"] if p in data and data[p]]
    durations = [7, 14, 30, 60, 90]
    
    html = []
    html.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FOREX_QUANT Terminal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
:root {{
  --bg-primary:    #090C18;
  --bg-secondary:  #0E1525;
  --bg-card:       rgba(255, 255, 255, 0.04);
  --bg-card-hover: rgba(255, 255, 255, 0.07);
  --border:        rgba(255, 255, 255, 0.07);
  --border-bright: rgba(255, 255, 255, 0.15);
  --text-primary:  #DDE5F0;
  --text-secondary:#7B8899;
  --text-muted:    #3D4A5C;
  --eur: #4A9EFF;   --usd: #00D084;   --gbp: #A78BFA;
  --jpy: #FF6B35;   --cny: #FF4757;   --sgd: #F5A623;   --hkd: #26C6DA;
  --positive: #00D084;
  --negative: #FF4757;
  --neutral:  #7B8899;
  --radius:   12px;
  --radius-sm: 8px;
  --transition: 180ms ease;
  --shadow:   0 8px 32px rgba(0, 0, 0, 0.5);
}}
body {{
  margin: 0; padding: 0;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', system-ui, sans-serif;
}}
.num {{ font-family: 'JetBrains Mono', monospace; }}
.app-header {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  height: 64px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
  background: linear-gradient(135deg, #0C1829 0%, #090C18 100%);
  border-bottom: 1px solid var(--border);
}}
.header-logo {{
  font-size: 18px; font-weight: 700; letter-spacing: -0.3px;
  background: linear-gradient(135deg, #4A9EFF, #00D084);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.header-sub  {{ font-size: 11px; color: var(--text-secondary); margin-top: 1px; }}
.header-meta {{ text-align: right; }}
.header-ts   {{ font-size: 11px; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; }}
.header-countdown {{ font-size: 12px; color: var(--positive); font-family: 'JetBrains Mono', monospace; margin-top: 2px; }}

.control-bar {{
  position: sticky; top: 64px; z-index: 90;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  padding: 10px 24px;
  background: rgba(9, 12, 24, 0.94);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(10px);
}}
.control-group       {{ display: flex; align-items: center; gap: 6px; }}
.control-label       {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.6px; margin-right: 4px; }}
.ctrl-btn {{
  padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 500;
  border: 1px solid var(--border); background: transparent;
  color: var(--text-secondary); cursor: pointer; transition: var(--transition);
}}
.ctrl-btn:hover, .ctrl-btn.active {{
  border-color: #4A9EFF; color: #4A9EFF; background: rgba(74,158,255,0.10);
}}
.direction-pill {{
  display: flex; border: 1px solid var(--border); border-radius: 8px; overflow: hidden;
}}
.direction-pill .ctrl-btn {{
  border-radius: 0; border: none; border-right: 1px solid var(--border);
}}
.direction-pill .ctrl-btn:last-child {{ border-right: none; }}
.direction-pill .ctrl-btn.active {{
  background: rgba(0,208,132,0.15); color: var(--positive);
  border-color: transparent;
}}
.direction-hint {{
  text-align: center; font-size: 12px; color: var(--text-muted);
  padding: 8px 24px; background: rgba(255,255,255,0.02);
  border-bottom: 1px solid var(--border);
}}

.content {{ padding: 24px; max-width: 1400px; margin: 80px auto 0; }}

.pair-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 18px 20px 14px; cursor: pointer; position: relative; overflow: hidden; margin-bottom: 12px;
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
}}
.pair-card::before {{
  content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: var(--pair-color);
}}
.pair-card:hover {{
  transform: translateY(-1px); box-shadow: var(--shadow); border-color: var(--border-bright); background: var(--bg-card-hover);
}}
.pair-card-inner {{
  display: grid; grid-template-columns: 220px 1fr 260px; gap: 20px; align-items: start;
}}
@media (max-width: 900px) {{
  .pair-card-inner {{ grid-template-columns: 1fr; }}
}}

.transfer-callout {{
  background: rgba(0, 208, 132, 0.06); border: 1px solid rgba(0, 208, 132, 0.2); border-radius: var(--radius-sm);
  padding: 12px 14px; text-align: center;
}}
.transfer-callout.inr-to-fx {{ border-color: rgba(0,208,132,0.2); }}
.transfer-callout.fx-to-inr {{ border-color: rgba(74,158,255,0.2); background: rgba(74,158,255,0.06); }}
.transfer-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); }}
.transfer-date  {{ font-size: 20px; font-weight: 600; color: var(--positive); font-family: 'JetBrains Mono', monospace; margin: 4px 0; }}
.transfer-rate  {{ font-size: 13px; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; }}
.transfer-gain  {{ font-size: 11px; color: var(--positive); margin-top: 3px; }}

.view-analysis-btn {{
  display: inline-block; padding: 6px 12px; background: rgba(255,255,255,0.05); border: 1px solid var(--border);
  border-radius: 6px; font-size: 11px; color: var(--text-secondary); cursor: pointer; margin-top: 10px;
}}
.chart-panel {{
  display: none; padding-top: 16px; margin-top: 16px; border-top: 1px solid var(--border);
}}
.chart-panel.open {{ display: block; }}
.chart-container {{ height: 300px; margin-bottom: 20px; }}

.summary-table {{ width: 100%; border-collapse: collapse; margin-top: 30px; font-size: 13px; }}
.summary-table th {{ text-align: left; padding: 10px; border-bottom: 1px solid var(--border); color: var(--text-muted); font-weight: 500; }}
.summary-table td {{ padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: 'JetBrains Mono', monospace; }}
.summary-table-wrapper {{ overflow-x: auto; }}
.app-footer {{
  text-align: center; padding: 30px; font-size: 11px; color: var(--text-muted);
  border-top: 1px solid var(--border); margin-top: 40px;
}}
</style>
</head>
<body>
<div id="stale-banner" style="display:none; background:#FF4757; color:#fff; text-align:center; padding:8px; font-size:12px; z-index:200; position:relative; margin-top: 64px;">
  ⚠️ WARNING: Data is more than 25 hours old.
</div>
<header class="app-header">
  <div>
    <div class="header-logo">FOREX_QUANT</div>
    <div class="header-sub">7 pairs · Multi-model ensemble</div>
  </div>
  <div class="header-meta">
    <div class="header-ts">Last updated: {gen_at}</div>
    <div class="header-countdown" id="countdown">Calculating...</div>
  </div>
</header>

<div class="control-bar">
  <div class="control-group">
    <span class="control-label">Duration</span>
    <button class="ctrl-btn" data-dur-btn="7" onclick="applyDuration('7')">1W</button>
    <button class="ctrl-btn" data-dur-btn="14" onclick="applyDuration('14')">2W</button>
    <button class="ctrl-btn active" data-dur-btn="30" onclick="applyDuration('30')">1M</button>
    <button class="ctrl-btn" data-dur-btn="60" onclick="applyDuration('60')">2M</button>
    <button class="ctrl-btn" data-dur-btn="90" onclick="applyDuration('90')">3M</button>
  </div>
  <div class="control-group" style="margin-left:auto;">
    <span class="control-label">Direction</span>
    <div class="direction-pill">
      <button class="ctrl-btn active" data-dir-btn="inr_to_fx" onclick="applyDirection('inr_to_fx')">INR → FX</button>
      <button class="ctrl-btn" data-dir-btn="fx_to_inr" onclick="applyDirection('fx_to_inr')">FX → INR</button>
    </div>
  </div>
  <div class="control-group" style="margin-left:auto;">
    <span class="control-label">Filter</span>
    <button class="ctrl-btn active" data-ccy-btn="all">ALL</button>
""")
    for p in pairs:
        ccy = p[:3]
        html.append(f'<button class="ctrl-btn" data-ccy-btn="{ccy}">{ccy}</button>')

    html.append(f"""
  </div>
</div>
<div class="direction-hint" id="dir-hint">Showing cheapest rate to buy foreign currency with Rupees — lower rates are better</div>

<div class="content">
""")

    charts_js = {}

    for pair in pairs:
        color = get_color(pair)
        flag = get_flag(pair)
        pair_data_30 = data[pair].get("30") or data[pair].get(list(data[pair].keys())[0])
        if not pair_data_30: continue
        
        c = pair_data_30['history']['close']
        c_rate = c[-1] if c and c[-1] else 0
        score = pair_data_30['signals']['composite']['score']
        vol = pair_data_30['statistics']['ann_vol_pct']
        rsi = pair_data_30['history']['rsi14'][-1] if pair_data_30['history']['rsi14'] else 0
        
        html.append(f'<div class="pair-card" data-pair="{pair}" data-score="{score:.1f}" data-vol="{vol:.1f}" data-rsi="{rsi:.1f}" style="--pair-color: {color};">')
        html.append(f'<div class="pair-card-inner">')
        
        html.append(f"""
          <div>
            <div style="font-size:16px; font-weight:600;">{flag}  {pair[:3]} / {pair[3:]} <span style="font-size:11px; color:var(--text-muted); margin-left:6px;">[{pair[:3]}]</span></div>
            <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">{pair_data_30['meta']['name']}</div>
            <div style="margin-top:12px; font-size:18px; font-family:'JetBrains Mono';">{c_rate:.4f}</div>
            <div style="margin-top:12px; font-size:12px;">[BUY] Composite: {score:.0f}/100</div>
          </div>
        """)
        
        html.append('<div>')
        for dur in durations:
            ds = str(dur)
            d = data[pair].get(ds)
            if not d: continue
            
            var95 = d['statistics']['var_95']
            sharpe = d['statistics']['sharpe_ratio']
            hurst = d['statistics']['hurst_exp']
            
            display = 'block' if ds == '30' else 'none'
            html.append(f'<div data-dur-section="{ds}" style="display:{display};">')
            
            spark = sparkline_svg(d['history']['close'][-30:], color, width=240, height=80)
            html.append(f'<div style="margin-bottom:12px;">{spark}</div>')
            
            html.append(f"""
              <div style="display:flex; gap:12px; font-size:11px; color:var(--text-secondary); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:8px 0; justify-content:space-between;">
                <span>RSI <span class="num">{rsi:.1f}</span></span> │
                <span>VaR95 <span class="num">{var95:.1f}%</span></span> │
                <span>Ann.Vol <span class="num">{vol:.1f}%</span></span> │
                <span>Sharpe <span class="num">{sharpe:.2f}</span></span> │
                <span>H <span class="num">{hurst:.2f}</span></span>
              </div>
            """)
            
            seas = d['seasonality'].get('dow', {})
            s_inr = seasonality_mini_svg(seas, 'inr_to_fx', 140, 24)
            s_fx = seasonality_mini_svg(seas, 'fx_to_inr', 140, 24)
            html.append(f"""
              <div style="display:flex; align-items:center; justify-content:space-between; margin-top:8px;">
                <div class="direction-inr-to-fx">{s_inr}</div>
                <div class="direction-fx-to-inr" style="display:none;">{s_fx}</div>
                <button class="view-analysis-btn">View Analysis ▼</button>
              </div>
            """)
            
            html.append('</div>')
        html.append('</div>')
        
        html.append('<div>')
        for dur in durations:
            ds = str(dur)
            d = data[pair].get(ds)
            if not d: continue
            
            ens = d['forecast']['ensemble']
            dates = d['forecast']['dates']
            min_idx = d['forecast']['best_transfer_day_idx']
            max_idx = int(ens.index(max(ens)))
            
            display = 'block' if ds == '30' else 'none'
            html.append(f'<div data-dur-section="{ds}" style="display:{display};">')
            
            html.append(f"""
              <div class="transfer-callout inr-to-fx direction-inr-to-fx">
                <div class="transfer-label">Best Transfer Date</div>
                <div class="transfer-date">● {dates[min_idx]}</div>
                <div class="transfer-rate">Ensemble Rate: {ens[min_idx]:.4f}</div>
                <div class="transfer-gain">INR→FX mode (Cheapest)</div>
              </div>
              <div class="transfer-callout fx-to-inr direction-fx-to-inr" style="display:none;">
                <div class="transfer-label">Best Transfer Date</div>
                <div class="transfer-date" style="color:#4A9EFF;">● {dates[max_idx]}</div>
                <div class="transfer-rate">Ensemble Rate: {ens[max_idx]:.4f}</div>
                <div class="transfer-gain" style="color:#4A9EFF;">FX→INR mode (Highest)</div>
              </div>
            """)
            html.append('</div>')
            
            hist_d = d['history']['dates']
            hist_c = d['history']['close']
            fc_d = d['forecast']['dates']
            
            c_key = f"{pair}_{ds}"
            charts_js[c_key] = {
                'traces_fc': [
                    {'x': hist_d, 'y': hist_c, 'name': 'History', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#7B8899'}},
                    {'x': fc_d, 'y': d['forecast']['arima'], 'name': 'ARIMA', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#4A9EFF'}},
                    {'x': fc_d, 'y': d['forecast']['hw'], 'name': 'Holt-Winters', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#A78BFA'}},
                    {'x': fc_d, 'y': d['forecast']['mc_p50'], 'name': 'MC Median', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#FF6B35'}},
                    {'x': fc_d, 'y': d['forecast']['ensemble'], 'name': 'Ensemble', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#FFFFFF', 'width': 2.5}},
                ],
                'layout_fc': {
                    'title': 'Forecast Ensemble', 'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                    'font': {'color': '#7B8899', 'family': 'Inter'}, 'margin': {'t': 30, 'r': 10, 'l': 40, 'b': 30},
                    'xaxis': {'gridcolor': 'rgba(255,255,255,0.05)'}, 'yaxis': {'gridcolor': 'rgba(255,255,255,0.05)'},
                    'showlegend': True, 'legend': {'orientation': 'h', 'y': -0.2}
                },
                'traces_mc': [
                    {'x': fc_d, 'y': d['forecast']['mc_p95'], 'name': 'P95', 'type': 'scatter', 'mode': 'lines', 'line': {'color': 'rgba(255,107,53,0.1)'}},
                    {'x': fc_d, 'y': d['forecast']['mc_p75'], 'name': 'P75', 'type': 'scatter', 'mode': 'lines', 'fill': 'tonexty', 'fillcolor': 'rgba(255,107,53,0.1)', 'line': {'color': 'rgba(255,107,53,0.2)'}},
                    {'x': fc_d, 'y': d['forecast']['mc_p50'], 'name': 'P50', 'type': 'scatter', 'mode': 'lines', 'fill': 'tonexty', 'fillcolor': 'rgba(255,107,53,0.2)', 'line': {'color': '#FF6B35'}},
                    {'x': fc_d, 'y': d['forecast']['mc_p25'], 'name': 'P25', 'type': 'scatter', 'mode': 'lines', 'fill': 'tonexty', 'fillcolor': 'rgba(255,107,53,0.2)', 'line': {'color': 'rgba(255,107,53,0.2)'}},
                    {'x': fc_d, 'y': d['forecast']['mc_p5'], 'name': 'P5', 'type': 'scatter', 'mode': 'lines', 'fill': 'tonexty', 'fillcolor': 'rgba(255,107,53,0.1)', 'line': {'color': 'rgba(255,107,53,0.1)'}},
                ],
                'layout_mc': {
                    'title': 'Monte Carlo Fan', 'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                    'font': {'color': '#7B8899', 'family': 'Inter'}, 'margin': {'t': 30, 'r': 10, 'l': 40, 'b': 30},
                    'xaxis': {'gridcolor': 'rgba(255,255,255,0.05)'}, 'yaxis': {'gridcolor': 'rgba(255,255,255,0.05)'},
                    'showlegend': False
                },
                'traces_rsi': [
                    {'x': hist_d, 'y': d['history']['rsi14'], 'name': 'RSI', 'type': 'scatter', 'mode': 'lines', 'line': {'color': color}},
                    {'x': [hist_d[0], hist_d[-1]], 'y': [70, 70], 'name': 'OB', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#FF4757', 'dash': 'dot'}},
                    {'x': [hist_d[0], hist_d[-1]], 'y': [30, 30], 'name': 'OS', 'type': 'scatter', 'mode': 'lines', 'line': {'color': '#00D084', 'dash': 'dot'}},
                ],
                'layout_rsi': {
                    'title': 'RSI (14)', 'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                    'font': {'color': '#7B8899', 'family': 'Inter'}, 'margin': {'t': 30, 'r': 10, 'l': 40, 'b': 30},
                    'xaxis': {'gridcolor': 'rgba(255,255,255,0.05)'}, 'yaxis': {'gridcolor': 'rgba(255,255,255,0.05)'},
                    'showlegend': False
                }
            }

        html.append('</div>')
        html.append('</div>')
        
        html.append(f"""
        <div class="chart-panel">
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div id="chart_forecast_{pair}" class="chart-container"></div>
            <div id="chart_mc_{pair}" class="chart-container"></div>
          </div>
          <div id="chart_rsi_{pair}" class="chart-container" style="height:200px;"></div>
        </div>
        """)
        
        html.append('</div>')

    html.append("""
<div class="summary-table-wrapper">
  <table class="summary-table">
    <thead>
      <tr>
        <th>Pair</th>
        <th>Rate</th>
        <th>7d Change</th>
        <th>Ensemble Target</th>
        <th>Signal</th>
        <th>Vol</th>
        <th>Sharpe</th>
      </tr>
    </thead>
    <tbody id="summary-tbody">
""")
    for pair in pairs:
        d = data[pair].get("30") or data[pair].get(list(data[pair].keys())[0])
        if not d: continue
        c = d['history']['close']
        rate = c[-1]
        c7 = c[-7] if len(c) >= 7 else c[0]
        pct = (rate - c7)/c7 * 100
        ens = d['forecast']['ensemble'][0]
        sig = d['signals']['composite']['recommendation']
        vol = d['statistics']['ann_vol_pct']
        sharpe = d['statistics']['sharpe_ratio']
        
        html.append(f"""
        <tr data-summary-pair="{pair}">
          <td style="color:{get_color(pair)}">{pair[:3]}/{pair[3:]}</td>
          <td>{rate:.4f}</td>
          <td style="color:{'#00D084' if pct>0 else '#FF4757'}">{pct:+.2f}%</td>
          <td class="target-ens">{ens:.4f}</td>
          <td>{sig}</td>
          <td>{vol:.1f}%</td>
          <td>{sharpe:.2f}</td>
        </tr>
        """)
    
    html.append("""
    </tbody>
  </table>
</div>
</div>
<footer class="app-footer">
  FOREX_QUANT · FX analysis for INR cross rates · Data via Yahoo Finance ·
  Not financial advice · For educational use only
</footer>
<script>
const CHARTS = """)
    html.append(json.dumps(charts_js))
    html.append(";\n")
    
    html.append("""
let currentDirection = 'inr_to_fx';
let currentDuration  = '30';

function applyDirection(dir) {
  currentDirection = dir;
  document.querySelectorAll('.direction-inr-to-fx').forEach(el => {
    el.style.display = dir === 'inr_to_fx' ? '' : 'none';
  });
  document.querySelectorAll('.direction-fx-to-inr').forEach(el => {
    el.style.display = dir === 'fx_to_inr' ? '' : 'none';
  });
  document.querySelectorAll('[data-dir-btn]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.dirBtn === dir);
  });
  const hint = document.getElementById('dir-hint');
  if (hint) {
    hint.textContent = dir === 'inr_to_fx' ? 
      "Showing cheapest rate to buy foreign currency with Rupees — lower rates are better" : 
      "Showing highest rate to receive Rupees — higher rates are better";
  }
}

function applyDuration(dur) {
  currentDuration = dur;
  document.querySelectorAll('[data-dur-section]').forEach(el => {
    el.style.display = el.dataset.durSection === dur ? '' : 'none';
  });
  document.querySelectorAll('[data-dur-btn]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.durBtn === dur);
  });
  document.querySelectorAll('.chart-panel.open').forEach(p => p.classList.remove('open'));
  document.querySelectorAll('.view-analysis-btn').forEach(btn => btn.textContent = 'View Analysis ▼');
}

document.querySelectorAll('[data-ccy-btn]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-ccy-btn]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const ccy = btn.dataset.ccyBtn;
    document.querySelectorAll('.pair-card').forEach(card => {
      card.style.display = (ccy === 'all' || card.dataset.pair.startsWith(ccy)) ? '' : 'none';
    });
    document.querySelectorAll('#summary-tbody tr').forEach(row => {
      row.style.display = (ccy === 'all' || row.dataset.summaryPair.startsWith(ccy)) ? '' : 'none';
    });
  });
});

document.querySelectorAll('.view-analysis-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const panel  = btn.closest('.pair-card').querySelector('.chart-panel');
    const isOpen = panel.classList.toggle('open');
    btn.textContent = isOpen ? 'View Analysis ▲' : 'View Analysis ▼';
    if (isOpen) {
      const pair = btn.closest('.pair-card').dataset.pair;
      const dur  = currentDuration;
      const key  = pair + '_' + dur;
      if (!window._chartsRendered) window._chartsRendered = {};
      if (!window._chartsRendered[key]) {
        const c = CHARTS[key];
        if (c) {
          Plotly.newPlot('chart_forecast_' + pair, c.traces_fc, c.layout_fc, {responsive:true, displayModeBar:false});
          Plotly.newPlot('chart_mc_' + pair,       c.traces_mc, c.layout_mc, {responsive:true, displayModeBar:false});
          Plotly.newPlot('chart_rsi_' + pair,      c.traces_rsi, c.layout_rsi, {responsive:true, displayModeBar:false});
        }
        window._chartsRendered[key] = true;
      }
    }
  });
});

(function() {
  const genAtStr = '""")
    
    gen_time_str = meta.get('generated_at', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")).replace(' UTC', '').replace(' ', 'T')
    html.append(gen_time_str)
    
    html.append("""Z';
  const genAt = new Date(genAtStr);
  const updateH = 6;
  function tick() {
    const nextUp = new Date(genAt.getTime() + updateH * 3600 * 1000);
    const diff   = nextUp - Date.now();
    if (diff <= 0) {
      document.getElementById('countdown').textContent = 'Update overdue';
      return;
    }
    const hh = Math.floor(diff / 3600000);
    const mm = Math.floor((diff % 3600000) / 60000);
    const ss = Math.floor((diff % 60000) / 1000);
    document.getElementById('countdown').textContent =
      `Next update in ${hh}h ${String(mm).padStart(2,'0')}m ${String(ss).padStart(2,'0')}s`;
  }
  tick(); setInterval(tick, 1000);
  
  if ((Date.now() - genAt) / 3.6e6 > 25) {
    const sb = document.getElementById('stale-banner');
    if(sb) sb.style.display = 'block';
  }
})();
</script>
</body>
</html>
""")

    with open('index.html', 'w') as f:
        f.write("".join(html))
    print("✅ Dashboard built: index.html")

if __name__ == "__main__":
    main()
