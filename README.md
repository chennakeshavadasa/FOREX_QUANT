# 📊 FX Quant Dashboard — EUR/INR & USD/INR

> Institutional-grade quantitative analysis for EUR/INR and USD/INR exchange rates.  
> Helps you decide **when to transfer INR to EUR or USD** using math — not guesswork.

🔗 **Live Dashboard** → [https://your-username.github.io/fx-quant-dashboard](https://your-username.github.io/fx-quant-dashboard)

---

## Features

| Category | Techniques |
|----------|-----------|
| **Forecasting** | ARIMA (auto-order), Holt-Winters ETS, Monte Carlo GBM (5,000 paths) |
| **Technical** | RSI-14, MACD(12,26,9), Bollinger Bands(20,2σ), Stochastic(14,3), Williams %R, ATR-14, CCI-20, Z-Score |
| **Statistics** | VaR (95/99%), CVaR, Hurst Exponent, ADF Test, Jarque-Bera, Sharpe Ratio, Skewness, Kurtosis, ACF |
| **Risk** | Max Drawdown, Peak-to-trough, DCA scenarios, Transfer scenario matrix |
| **Seasonality** | Day-of-week effect, Monthly patterns, Multiplicative decomposition |

## Currency Pairs
- 🇪🇺 **EUR/INR** — Euro vs Indian Rupee
- 🇺🇸 **USD/INR** — US Dollar vs Indian Rupee
- ⚖️ **Compare** — Side-by-side view

## Forecast Windows
- 1 Week · 2 Weeks · 1 Month · 2 Months · 3 Months

---

## Deploy to GitHub Pages

```bash
git clone https://github.com/your-username/fx-quant-dashboard.git
cd fx-quant-dashboard
# Open index.html in your browser OR push to GitHub Pages
```

### GitHub Pages Setup
1. Push this repo to GitHub
2. Go to repo **Settings → Pages**
3. Set source to **Deploy from branch → main → / (root)**
4. Done — live in ~60 seconds at `https://your-username.github.io/fx-quant-dashboard`

---

## Refresh Data

```bash
# Run from the EU_VS_INR directory
python3 engine.py          # Fetches fresh data + runs all models
python3 build_dashboard.py # Rebuilds index.html with new data
```

## Tech Stack
- **Frontend**: Pure HTML5 + Vanilla CSS + Chart.js 4.4
- **Analysis Engine**: Python 3 — yfinance, statsmodels, scipy, ta
- **Models**: ARIMA, Holt-Winters ETS, Monte Carlo GBM
- **Deployment**: GitHub Pages (static, zero backend)

---

> ⚠️ For educational/analytical purposes only. Not financial advice.
