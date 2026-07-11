# FX Quant Terminal

A **zero-server, 100% client-side** quantitative foreign exchange analysis platform covering seven INR currency pairs — EUR, USD, GBP, JPY, CNY, SGD, and HKD — with ensemble forecasting, technical indicators, risk analytics, and seasonality analysis.

**Live Dashboard:** [chennakeshavadasa.github.io/FOREX_QUANT](https://chennakeshavadasa.github.io/FOREX_QUANT/)

![Architecture](https://img.shields.io/badge/Architecture-100%25_Client--Side-blue)
![Python](https://img.shields.io/badge/Python-None-red)
![Build_Step](https://img.shields.io/badge/Build_Step-None-red)
![Cost](https://img.shields.io/badge/Cost-Free-green)
![Data](https://img.shields.io/badge/Data-Frankfurter_ECB-brightgreen)

---

## What Does This Dashboard Do?

> **Plain English Summary**

When you need to send money abroad or receive money from abroad, the obvious question is: *"When is the best time to do it?"*

This dashboard pulls live historical exchange rate data for seven INR currency pairs, runs three independent mathematical forecasting models simultaneously, blends them into an ensemble forecast, and surfaces the single best predicted day to execute your transfer — whether you are sending INR abroad or receiving INR from abroad. All computation happens in your browser the moment the page loads. There is no backend, no API key, no login, and nothing to install.

**What the dashboard gives you:**

| Feature | What it means |
|---|---|
| **Best Transfer Date** | The single future day the ensemble agrees the rate will be most favourable |
| **Forecast Chart** | Price history + ARIMA + Holt-Winters + Monte Carlo ensemble, plotted together |
| **MC Fan Chart** | A P5 / P50 / P95 probability cone from 5,000 simulated futures |
| **Technical Signals** | 8 indicators with a 0–100 composite score: bullish, bearish, or neutral |
| **Risk Metrics** | VaR, CVaR, Max Drawdown, DCA averages — how bad can a bad day get? |
| **Statistics** | Hurst exponent, skewness, kurtosis, rolling volatility |
| **Seasonality** | Which day of the week / month historically yields the best rate |
| **Direction Toggle** | Flip between "I'm sending INR" (want rate low) and "I'm receiving INR" (want rate high) |

---

## Architecture — v2

### Why v1 Was Broken

The original architecture used Python (`engine.py` + `build_dashboard.py`) running in GitHub Actions to download data via `yfinance`, run ARIMA/Holt-Winters/Monte Carlo, and bake results into a static JSON file that the HTML dashboard read. This broke within days of deployment — consistently — because:

- Yahoo Finance rate-limits GitHub Actions runner IPs aggressively
- `yfinance`, `statsmodels`, and `scipy` version conflicts appear silently between runs
- A failed CI job leaves stale data in `multi_data.json` with no indication anything is wrong
- The dashboard shows data from days ago as if it were current

### How v2 Works

```
Your Browser
    │
    ├─── 1. Fetch live FX data
    │         │
    │         ├── PRIMARY: Frankfurter API (ECB reference rates)
    │         │     • Native CORS — works from file://, localhost, GitHub Pages
    │         │     • No API key, no proxy, no rate limits
    │         │     • 3 years of daily history for all 7 pairs
    │         │     │
    │         └── FALLBACK: Yahoo Finance v8 API
    │               • Tried via 4 CORS proxies in parallel (Promise.any, 9s timeout)
    │               • corsproxy.io / allorigins.win / codetabs.com / thingproxy.io
    │               • If all fail → DATA UNAVAILABLE banner + Retry button
    │
    └─── 2. Run all quant math in browser JavaScript
              │
              ├── ARIMA(2,1,0)         — Yule-Walker AR fit on differenced log prices
              ├── Holt-Winters          — Triple exponential smoothing (additive)
              ├── Monte Carlo GBM       — 5,000 paths, P5 / P50 / P95
              ├── Ensemble              — 35% ARIMA + 35% H-W + 30% MC median
              ├── 8 Technical Indicators
              ├── Risk Metrics (VaR, CVaR, MaxDD, DCA, Ann. Vol)
              ├── Statistics (Hurst, Skewness, Kurtosis, Rolling Vol)
              └── Seasonality (day-of-week, monthly average log-return)
```

**Key properties of v2:**
- No Python anywhere
- No build step, no npm, no bundler
- No cron job, no CI data-fetch pipeline
- No stale data — every page load fetches live rates
- Single `index.html` file — the entire application
- GitHub Actions only deploys the static file to Pages (no computation)

---

## Data Sources

### Primary: Frankfurter API (ECB Reference Rates)

[api.frankfurter.app](https://api.frankfurter.app/) publishes the European Central Bank's official daily reference exchange rates. It is open, CORS-enabled, requires no API key, and has no meaningful rate limits for individual users.

**Endpoint used:**
```
GET https://api.frankfurter.app/2022-07-11..?from=EUR&to=INR
```
The `..` suffix means "from start date to today" — an open-ended range. This returns a JSON object where every key is a date string and every value is the closing rate:

```json
{
  "amount": 1.0,
  "base": "EUR",
  "start_date": "2022-07-11",
  "end_date": "2026-07-11",
  "rates": {
    "2022-07-11": { "INR": 82.9012 },
    "2022-07-12": { "INR": 83.1450 },
    ...
  }
}
```

All 7 pairs are fetched directly (`from=EUR`, `from=USD`, `from=GBP`, etc.) since Frankfurter supports INR as a target for all of them, including CNY, SGD, and HKD. No synthetic cross-rate calculation is needed.

**Coverage:** ~780 daily data points over 3 years. Data is published on European business days; Indian holidays within that window are forward-filled by the browser before passing to the models.

### Fallback: Yahoo Finance v8 via CORS Cascade

If Frankfurter fails (network issue, API down), the browser immediately retries using Yahoo Finance's chart API:
```
GET https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=3y
```
Yahoo Finance enforces CORS restrictions, so the request is routed through 4 public CORS proxy services simultaneously using `Promise.any()`. Whichever responds first and successfully within a 9-second timeout is used. If all four fail, a `DATA UNAVAILABLE` message is shown with a retry button.

| Yahoo Ticker | Pair |
|---|---|
| `EURINR=X` | EUR/INR |
| `INR=X` | USD/INR |
| `GBPINR=X` | GBP/INR |
| `JPYINR=X` | JPY/INR |
| `SGDINR=X` | SGD/INR |
| `HKDINR=X` | HKD/INR |
| Synthetic | CNY/INR = USD/INR ÷ USD/CNY |

---

## Forecasting Models

### Forecast Horizons

| Label | Trading Days Forecasted | History Displayed |
|---|---|---|
| 1W | 5 | 10 days |
| 2W | 10 | 20 days |
| 1M | 22 | 44 days |
| 2M | 44 | 88 days |
| 3M | 66 | 132 days |

The display window scales 1:1 with the forecast horizon — a 1W forecast shows 10 days of history and 5 days of future. The statistical models always use the full 3-year dataset behind the scenes for robust parameter estimation.

---

### Model 1: ARIMA(2,1,0)

> **Plain English:** ARIMA looks at the sequence of past rates and fits a linear equation that captures how each day's rate depends on the two previous days. The "integrated" step removes the trend so the model works on the stationary (mean-stable) series of daily returns instead of raw prices.

**Full name:** AutoRegressive Integrated Moving Average

The model is fitted on first-differenced log prices (i.e., daily log-returns), making it equivalent to a stationary AR(2) process:

$$\Delta \ln S_t = \phi_1 \Delta \ln S_{t-1} + \phi_2 \Delta \ln S_{t-2} + \varepsilon_t$$

**Parameter estimation — Yule-Walker equations:**

The AR coefficients $\phi_1, \phi_2$ are estimated from the empirical autocorrelations of the return series at lags 0, 1, and 2:

$$\begin{bmatrix} r_0 & r_1 \\ r_1 & r_0 \end{bmatrix} \begin{bmatrix} \phi_1 \\ \phi_2 \end{bmatrix} = \begin{bmatrix} r_1 \\ r_2 \end{bmatrix}$$

Solving the 2×2 system:

$$\phi_1 = \frac{r_0 r_1 - r_1 r_2}{r_0^2 - r_1^2}, \quad \phi_2 = \frac{r_0 r_2 - r_1^2}{r_0^2 - r_1^2}$$

A stationarity constraint clips $|\phi_1| + |\phi_2| < 0.97$ to prevent explosive forecasts.

**Forecasting:** $h$-step forecast is computed by iterating the AR recursion forward, cumulative-summing the predicted differences, and exponentiating back to price space:

$$\ln \hat{S}_{t+h} = \ln S_t + \sum_{k=1}^{h} \hat{\Delta}_k$$

**Weight in ensemble: 35%**

---

### Model 2: Holt-Winters Additive Triple Exponential Smoothing

> **Plain English:** Holt-Winters separately tracks three things: where the rate is right now (level), whether it is rising or falling (trend), and recurring weekly or monthly patterns (seasonality). It gives exponentially more weight to recent data than old data.

**Equations:**

Level (where the rate currently sits, corrected for seasonality):

$$L_t = \alpha(y_t - S_{t-m}) + (1-\alpha)(L_{t-1} + T_{t-1})$$

Trend (direction and speed of movement):

$$T_t = \beta(L_t - L_{t-1}) + (1-\beta)T_{t-1}$$

Seasonality (additive recurring component):

$$S_t = \gamma(y_t - L_t) + (1-\gamma)S_{t-m}$$

Forecast $h$ steps ahead:

$$\hat{y}_{t+h} = L_t + h \cdot T_t + S_{(t+h-1) \bmod m}$$

**Parameters:** $\alpha = 0.35$, $\beta = 0.08$, $\gamma = 0.12$. The seasonal period $m$ is set to 5 trading days for 1W/2W horizons (capturing within-week patterns) and 22 trading days for 1M+ horizons (capturing monthly cycles).

**Why this complements ARIMA:** ARIMA captures linear autocorrelation in the differenced series. Holt-Winters explicitly separates trend from seasonality and applies time-decaying weights. They are structurally independent, so blending them reduces single-model error.

**Weight in ensemble: 35%**

---

### Model 3: Monte Carlo Geometric Brownian Motion

> **Plain English:** Monte Carlo runs 5,000 independent possible "futures" simultaneously. Each path evolves differently because currency markets have a random component. The result is a fan of possibilities — showing not just the most likely outcome, but the full spread of plausible outcomes.

**The stochastic differential equation:**

$$dS_t = \mu S_t \, dt + \sigma S_t \, dW_t$$

**Discrete solution (Euler-Maruyama):**

$$S_{t+1} = S_t \exp\!\left[\left(\mu - \frac{\sigma^2}{2}\right)\Delta t + \sigma\sqrt{\Delta t} \cdot Z\right], \quad Z \sim \mathcal{N}(0,1)$$

**Parameter estimation from historical returns** $r_t = \ln(S_t / S_{t-1})$:

$$\hat{\mu} = \bar{r}, \quad \hat{\sigma} = \text{std}(r_t)$$

Normal draws $Z$ are generated using the **Box-Muller transform** for efficiency:

$$Z = \sqrt{-2\ln U_1} \cdot \cos(2\pi U_2), \quad U_1, U_2 \sim \text{Uniform}(0,1)$$

**Output:** After running all 5,000 paths for $h$ days, the price distribution at each future day is summarised as:
- **P5 (Bear case):** Rate below this on only 5% of paths
- **P50 (Base case):** Median across all paths
- **P95 (Bull case):** Rate above this on only 5% of paths

**Weight in ensemble: 30%** (lower than the deterministic models because GBM assumes a pure random walk with no mean-reversion, which tends to underperform for managed INR crosses)

---

### Ensemble Forecast

The three model outputs are combined at each forecast step by a fixed weighted average:

$$\hat{S}_{t+h}^{\text{ens}} = 0.35 \cdot \hat{S}_{t+h}^{\text{ARIMA}} + 0.35 \cdot \hat{S}_{t+h}^{\text{H-W}} + 0.30 \cdot \hat{S}_{t+h}^{\text{MC}_{P50}}$$

**Selecting the Best Transfer Date:**

For **INR → FX** (sending Rupees abroad — lower rate is better):

$$h^* = \underset{h \in \{1,\ldots,T\}}{\arg\min} \; \hat{S}_{t+h}^{\text{ens}}$$

For **FX → INR** (receiving Rupees — higher rate is better):

$$h^* = \underset{h \in \{1,\ldots,T\}}{\arg\max} \; \hat{S}_{t+h}^{\text{ens}}$$

**Potential gain** displayed in the banner:

$$\text{Gain\%} = \frac{|\hat{S}_{t+h^*}^{\text{ens}} - S_t|}{S_t} \times 100$$

---

## Technical Indicators

> **Plain English:** Technical indicators are mathematical summaries of the price history that classify whether the current rate is cheap, expensive, gaining momentum, or losing it. The dashboard computes 8 of them and combines them into a single 0–100 composite score.

All indicators run on the **full 3-year dataset** (not just the display window) for statistical stability.

| Indicator | Formula | Signal interpretation |
|---|---|---|
| **RSI-14** | $100 - \frac{100}{1 + \text{AvgGain}_{14} / \text{AvgLoss}_{14}}$ | <30 oversold (cheap); >70 overbought (expensive) |
| **MACD(12,26,9)** | $\text{EMA}_{12} - \text{EMA}_{26}$; histogram = MACD − signal | Positive histogram = bullish momentum |
| **Bollinger %B** | $\frac{S_t - \text{Lower}}{Upper - \text{Lower}}$, bands at $\mu \pm 2\sigma$ over 20 days | <0.2 at lower band (cheap); >0.8 at upper band |
| **Stochastic-14** | $\frac{S_t - \min_{14}}{\max_{14} - \min_{14}} \times 100$ | <20 oversold; >80 overbought |
| **Williams %R** | $\frac{\max_{14} - S_t}{\max_{14} - \min_{14}} \times (-100)$ | <−80 oversold; >−20 overbought |
| **ATR-14** | Mean of $\max(H-L, |H-C_{t-1}|, |L-C_{t-1}|)$ over 14 days | Higher = more volatile regime |
| **CCI-20** | $\frac{TP_t - \bar{TP}_{20}}{0.015 \cdot \text{MAD}_{20}}$ | <−100 unusually cheap; >+100 unusually expensive |
| **Z-Score-20** | $\frac{S_t - \mu_{20}}{\sigma_{20}}$ | <−1.5 statistically cheap; >+1.5 statistically expensive |

**Composite Score (0–100):**

A weighted aggregation of normalised indicator values, where each indicator's bullish/bearish reading is mapped to a 0–100 scale and summed:

$$\text{Score} = 0.20 \cdot \text{RSI} + 0.15 \cdot \text{MACD} + 0.12 \cdot \text{BB} + 0.12 \cdot \text{Stoch} + 0.10 \cdot \text{W\%R} + 0.10 \cdot \text{CCI} + 0.10 \cdot \text{Z} + 0.11 \cdot \text{ROC}$$

| Score | Classification |
|---|---|
| ≥ 70 | Strong signal (green) |
| 40 – 69 | Neutral |
| < 40 | Weak / deteriorating (red) |

The direction toggle **inverts the composite score** — what is bearish for INR→FX (rate rising) is bullish for FX→INR (you receive more INR).

---

## Risk Metrics

> **Plain English:** These numbers answer "how bad can a bad day be?" and provide context for how much rate risk you carry by waiting.

**Value at Risk (VaR):**

$$\text{VaR}_{95} = -Q_{0.05}(r), \quad \text{VaR}_{99} = -Q_{0.01}(r)$$

where $Q_\alpha$ is the $\alpha$-quantile of the empirical daily return distribution. VaR₉₅ = 0.4% means the rate will not move more than 0.4% against you on 95% of days.

**Conditional VaR / Expected Shortfall:**

$$\text{CVaR}_{95} = -\mathbb{E}[r \mid r < Q_{0.05}(r)]$$

The average loss on the worst 5% of days — more informative than VaR because it describes the severity of tail events, not just their threshold.

**Maximum Drawdown:**

$$\text{MDD} = \max_{t} \frac{\text{Peak}_t - S_t}{\text{Peak}_t}, \quad \text{Peak}_t = \max_{s \leq t} S_s$$

The largest peak-to-trough decline observed in the full historical window.

**Dollar-Cost Averaging (DCA):**

$$\text{DCA}_n = \frac{1}{n} \sum_{i=0}^{n-1} S_{t-i}$$

The average rate you would have obtained by splitting your transfer equally across the last 5 or 10 trading days — a benchmark for how much timing precision is worth.

**Annualised Volatility:**

$$\sigma_\text{ann} = \sigma_\text{daily} \times \sqrt{252}$$

Computed on a rolling 20-day window of daily log-returns.

---

## Statistical Analysis

> **Plain English:** These tests characterise the statistical *nature* of the exchange rate series — does it trend, mean-revert, or wander randomly? Are big moves more common than a normal distribution would predict?

**Hurst Exponent:**

$$H = \frac{\ln(R/S)}{\ln(n)}$$

where $R$ is the range of the cumulative deviation series and $S$ is the standard deviation of the return series. Interpretation:

| $H$ | Regime | Implication |
|---|---|---|
| $H < 0.45$ | Mean-reverting | Rate bounces back — buy dips, sell rallies |
| $H \approx 0.5$ | Random walk | No exploitable serial pattern |
| $H > 0.55$ | Trending | Moves persist — follow the direction |

**Skewness:**

$$\gamma_1 = \frac{\mathbb{E}[(r-\mu)^3]}{\sigma^3}$$

Negative skew means occasional large drops are more common than large gains — relevant for tail-risk assessment.

**Excess Kurtosis:**

$$\gamma_2 = \frac{\mathbb{E}[(r-\mu)^4]}{\sigma^4} - 3$$

Values above 0 indicate fat tails — extreme rate movements occur more often than a Gaussian model predicts. This is almost always positive for FX returns, which is why VaR and CVaR use the empirical distribution rather than a normal approximation.

**Rolling Annualised Volatility:**

Computed for 10-day, 20-day, and 30-day windows to show how the volatility regime has evolved over time. Compression (all three converging downward) often precedes a large directional move.

---

## Seasonality Analysis

> **Plain English:** Are Tuesdays historically cheaper than Fridays for a given pair? Is November typically better than March? This section analyses the full 3-year return history to surface these patterns.

**Day-of-Week Effect:**

For each trading day $d \in \{\text{Mon}, \text{Tue}, \text{Wed}, \text{Thu}, \text{Fri}\}$:

$$\bar{r}_d = \frac{1}{|T_d|} \sum_{t \in T_d} r_t$$

where $T_d$ is the set of all historical dates falling on weekday $d$.

**Monthly Seasonality:**

$$\bar{r}_m = \frac{1}{|T_m|} \sum_{t \in T_m} r_t, \quad m \in \{1, \ldots, 12\}$$

Green bars indicate days/months where the FX rate historically **fell** (good for INR→FX — you spend fewer Rupees). Red bars indicate days/months where the rate rose.

> These are historical averages over the full dataset, not guarantees. A month being historically green does not mean it will be green next year.

---

## Direction Toggle

**INR → FX (default):** You are sending Rupees abroad. You want the exchange rate as *low* as possible — fewer Rupees needed to buy one unit of foreign currency.

**FX → INR:** You are receiving foreign money in India. You want the exchange rate as *high* as possible — more Rupees per unit of foreign currency received.

When you toggle to FX → INR, the entire dashboard inverts:

$$\tilde{S}_t = \frac{1}{S_t}$$

The "best date" switches from $\arg\min$ to $\arg\max$, the composite score inverts (what was bearish becomes bullish), and the Monte Carlo fan swaps its P5 and P95 bands from the INR-receiver's perspective.

---

## Deployment

### Option 1 — GitHub Pages (recommended)

This repo is configured to deploy automatically via GitHub Actions on every push to `main`.

1. Fork or clone the repository
2. Go to **Settings → Pages → Source** and select `main` branch, root `/`
3. Push any change to `main` — GitHub Actions runs `deploy.yml` and the live site updates in ~2 minutes

No secrets, no environment variables, no API keys needed.

### Option 2 — Local Testing

```bash
# Frankfurter API works even from file://, so you can just open the file
open index.html

# Or serve it properly
python3 -m http.server 8000
# → http://localhost:8000
```

---

## Repo Structure

```
FOREX_QUANT/
├── index.html                   ← Entire application (HTML + CSS + JS)
├── .nojekyll                    ← Disables Jekyll processing on GitHub Pages
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml           ← Pushes index.html to GitHub Pages (no Python, no data fetch)
```

The entire application is one file. There is no `package.json`, no build config, no `requirements.txt`, no data files.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application structure | Single `index.html` — zero build step, zero npm, zero dependencies to install |
| Styling | Vanilla CSS with CSS custom properties, dark terminal theme |
| Typography | [Outfit](https://fonts.google.com/specimen/Outfit) (UI) + [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) (all numeric data) |
| Charts | [Chart.js 4.4](https://www.chartjs.org/) loaded from cdnjs CDN |
| Quantitative math | Pure JavaScript — ARIMA, Holt-Winters, Monte Carlo GBM, all 8 indicators, all risk metrics, Hurst exponent, seasonality — all implemented from scratch |
| Primary data | [Frankfurter API](https://www.frankfurter.app/) (ECB reference rates, native CORS) |
| Fallback data | Yahoo Finance v8 via 4 parallel CORS proxies (`Promise.any`, 9s timeout) |
| Hosting | GitHub Pages — free, zero infrastructure, deploys on push |

---

## Disclaimer

This tool is for analytical and educational purposes only. It does not constitute financial advice. All forecasts are probabilistic estimates derived from historical data and mathematical models. Past exchange rate patterns do not guarantee future movements. Currency markets are affected by macroeconomic, geopolitical, and regulatory factors that no model can fully capture. Consult a licensed financial advisor before making foreign exchange decisions.
