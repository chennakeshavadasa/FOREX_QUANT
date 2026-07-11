# FX Quant Terminal

A **zero-server, 100% client-side** quantitative foreign exchange analysis platform covering seven INR currency pairs.

**Live:** [chennakeshavadasa.github.io/FOREX_QUANT](https://chennakeshavadasa.github.io/FOREX_QUANT/)

![Architecture](https://img.shields.io/badge/Architecture-100%25_Client--Side-blue)
![Python](https://img.shields.io/badge/Python-None-red)
![Build_Step](https://img.shields.io/badge/Build_Step-None-red)
![Cost](https://img.shields.io/badge/Cost-Free-green)

---

## Architecture — v2 (Complete Rewrite)

The Python-based architecture (`engine.py` → `multi_data.json` → HTML) was removed entirely. It relied on `yfinance` in GitHub Actions which fails within days — Yahoo Finance rate-limits CI runners, causing stale data and blank dashboards.

**New architecture:**

```
Browser → Frankfurter API (ECB rates, native CORS, no key, works from file://)
               │
               └── if fail → Yahoo Finance v8 via 4 CORS proxies (Promise.any)
                                    │
                                    └── if all fail → DATA UNAVAILABLE + Retry button
```

All quant computation runs in the browser. No Python, no build step, no cron job, no JSON files.

---

## Data Sources

| Source | Role | CORS | API Key |
|--------|------|------|---------|
| [Frankfurter API](https://www.frankfurter.app/) | **Primary** — ECB reference rates, 3yr history | Native ✓ | None ✓ |
| Yahoo Finance v8 | Fallback | Via 4 CORS proxies | None ✓ |

**Why Frankfurter?** It serves European Central Bank reference rates via a stable, CORS-enabled, rate-limit-free API. Works from `file://` URLs, `localhost`, and GitHub Pages without any proxy.

---

## Features

| Feature | Detail |
|---------|--------|
| **7 Pairs** | EUR, USD, GBP, JPY, CNY, SGD, HKD vs INR |
| **5 Horizons** | 1W · 2W · 1M · 2M · 3M |
| **Direction Toggle** | INR→FX (sending) / FX→INR (receiving) |
| **3 Forecast Models** | ARIMA(2,1,0) · Holt-Winters additive · Monte Carlo GBM |
| **Ensemble** | 35% ARIMA + 35% H-W + 30% MC median |
| **Best Transfer Date** | argmin/argmax of ensemble over horizon |
| **MC Fan Chart** | P5 / P50 / P95 probability cone (5000 paths) |
| **8 Tech Indicators** | RSI-14, MACD, Bollinger %B, Stochastic-14, Williams %R, ATR-14, CCI-20, Z-Score-20 |
| **Composite Score** | Weighted 0–100 signal (≥70 strong, <40 weak) |
| **Risk Metrics** | VaR95/99, CVaR95, Max Drawdown, DCA 5/10-day, Ann. Vol |
| **Statistics** | Hurst exponent, Skewness, Excess Kurtosis, 10/20/30d Rolling Vol |
| **Seasonality** | Day-of-week + monthly average log-return charts |

---

## Deployment

### Option 1 — GitHub Pages (recommended)
1. Push these files to `main` branch
2. Settings → Pages → Source: `main` branch, root `/`
3. Live at `https://chennakeshavadasa.github.io/FOREX_QUANT/`

### Option 2 — Local Testing
```bash
# Open directly — Frankfurter API works from file://
open index.html

# OR serve locally
python3 -m http.server 8000
# → http://localhost:8000
```

---

## Files (Complete List)

```
FOREX_QUANT/
├── index.html                   ← Entire application
├── .nojekyll                    ← Disables Jekyll on GitHub Pages
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml           ← Deploy index.html to Pages (no Python)
```

**Delete from repo if still present:** `engine.py`, `build_dashboard.py`, `multi_data.json`, `patch.py`, `patch_direction.py`, `requirements.txt`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Structure | Single `index.html` — zero build, zero npm |
| Styling | Vanilla CSS, CSS custom properties, dark terminal theme |
| Fonts | [Outfit](https://fonts.google.com/specimen/Outfit) + [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) |
| Charts | [Chart.js 4.4](https://www.chartjs.org/) via cdnjs CDN |
| Math | Pure JavaScript — all models from scratch |
| Data | Frankfurter API (primary) + Yahoo Finance CORS cascade (fallback) |
| Hosting | GitHub Pages — free, zero infrastructure |

---

## Disclaimer

Educational and analytical purposes only. Not financial advice. All forecasts are probabilistic estimates from historical data. Currency markets are affected by macroeconomic, geopolitical, and regulatory factors that no model can fully capture.
