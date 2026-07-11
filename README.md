# FX Quant Terminal

A **zero-server, 100% client-side** quantitative foreign exchange analysis platform covering seven INR currency pairs — EUR, USD, GBP, JPY, CNY, SGD, and HKD — with ensemble forecasting, technical indicators, risk analytics, and seasonality analysis.

**Live Dashboard:** [chennakeshavadasa.github.io/FOREX_QUANT](https://chennakeshavadasa.github.io/FOREX_QUANT/)

[![Live](https://img.shields.io/badge/Status-Live-brightgreen)](https://chennakeshavadasa.github.io/FOREX_QUANT/)
[![Architecture](https://img.shields.io/badge/Architecture-100%25_Client--Side-blue)](#architecture)
[![Data](https://img.shields.io/badge/Data-Frankfurter_ECB-informational)](#data-sources)
[![Cost](https://img.shields.io/badge/Cost-Free-success)](#deployment)

---

## Table of Contents

1. [What Does This Dashboard Do?](#what-does-this-dashboard-do)
2. [Architecture](#architecture)
3. [Data Sources](#data-sources)
4. [Forecasting Models](#forecasting-models)
   - [ARIMA(2,1,0)](#model-1-arima210)
   - [Holt-Winters](#model-2-holt-winters-additive)
   - [Monte Carlo GBM](#model-3-monte-carlo-gbm)
   - [Ensemble](#ensemble-forecast)
5. [Technical Indicators](#technical-indicators)
6. [Risk Metrics](#risk-metrics)
7. [Statistical Analysis](#statistical-analysis)
8. [Seasonality Analysis](#seasonality-analysis)
9. [Direction Toggle](#direction-toggle)
10. [Deployment](#deployment)
11. [Tech Stack](#tech-stack)
12. [Disclaimer](#disclaimer)

---

## What Does This Dashboard Do?

When you need to send money abroad or receive a foreign payment in India, the obvious question is: *"When is the best time to do the transfer this week or month?"*

This dashboard pulls live historical exchange rate data for seven INR currency pairs, runs three independent mathematical forecasting models simultaneously, blends them into a weighted ensemble, and surfaces the single best predicted day to execute your transfer — whether you are sending INR abroad or receiving INR from a foreign source. All computation runs in the browser the moment the page loads. There is no backend, no API key, no login, and nothing to install.

| Feature | What it means for you |
|---|---|
| **Best Transfer Date** | The one future day when the ensemble forecast peaks at the most favourable rate |
| **Forecast Chart** | Price history + ARIMA + Holt-Winters + Monte Carlo plotted together with a confidence band |
| **MC Fan Chart** | P5 / P50 / P95 probability cone from 5,000 independently simulated futures |
| **8 Technical Signals** | RSI, MACD, Bollinger, Stochastic, Williams %R, ATR, CCI, Z-Score — combined into a 0–100 composite |
| **Risk Metrics** | VaR, CVaR, Max Drawdown, DCA averages — quantifying how bad a bad day can get |
| **Statistical Profile** | Hurst exponent, skewness, kurtosis, rolling volatility — characterising the rate's behaviour |
| **Seasonality** | Which day of the week and which calendar month historically yields the best rate |
| **Direction Toggle** | Flip between INR→FX (you are sending, want rate low) and FX→INR (you are receiving, want rate high) |

---

## Architecture

### Why the Old Version Broke

The previous architecture used a Python pipeline (`engine.py` → `build_dashboard.py`) running inside GitHub Actions on a daily cron schedule. It downloaded data via `yfinance`, ran the forecasting models, and saved results to `multi_data.json`, which the HTML dashboard read statically.

This failed within days of every deployment for three compounding reasons:

1. **Yahoo Finance rate-limits GitHub Actions runner IPs.** CI runners share public IP pools that Yahoo Finance identifies and throttles aggressively. `yfinance` calls return empty DataFrames silently.
2. **Stale data with no indication of failure.** A failed CI run leaves the previous `multi_data.json` in place. The dashboard loads it and shows data that is days old as if it were current, with no error shown to the user.
3. **Python dependency drift.** `yfinance`, `statsmodels`, and `scipy` minor version conflicts surface unpredictably in the GitHub Actions environment.

### The New Architecture

Everything runs in the browser. GitHub Actions only deploys the static `index.html` file — it performs no computation and touches no external APIs.

```
Your Browser
    │
    ├── Step 1: Fetch live FX data
    │       │
    │       ├── PRIMARY ──► Frankfurter API (ECB reference rates)
    │       │                 • Native CORS — no proxy needed
    │       │                 • Works from file://, localhost, and GitHub Pages
    │       │                 • No API key · No rate limits · 3 years of daily history
    │       │
    │       └── FALLBACK ──► Yahoo Finance v8 API
    │                         • 4 CORS proxies tried in parallel (Promise.any, 9s timeout)
    │                         • If all four fail → DATA UNAVAILABLE + Retry button
    │                         • No synthetic fallback data is ever displayed
    │
    └── Step 2: Run all quant math in JavaScript
            │
            ├── ARIMA(2,1,0)           Yule-Walker AR fit on differenced log prices
            ├── Holt-Winters            Triple exponential smoothing, additive seasonal
            ├── Monte Carlo GBM         5,000 paths · P5 / P50 / P95 at each horizon step
            ├── Ensemble                35% ARIMA + 35% H-W + 30% MC median
            ├── 8 Technical Indicators  RSI, MACD, Bollinger, Stochastic, Williams, ATR, CCI, Z-Score
            ├── Risk Metrics            VaR95/99, CVaR95, Max Drawdown, DCA 5/10-day, Ann. Vol
            ├── Statistical Analysis    Hurst exponent, Skewness, Kurtosis, Rolling Vol (10/20/30d)
            └── Seasonality             Day-of-week + monthly average log-return
```

---

## Data Sources

### Primary — Frankfurter API

[api.frankfurter.app](https://api.frankfurter.app/) publishes the European Central Bank's official daily reference exchange rates. It is open-source, CORS-enabled by default, requires no API key, and has no meaningful rate limit for individual users. This is the reason it was chosen over Yahoo Finance as primary: it simply works reliably, every time, from any origin.

**Request format:**
```
GET https://api.frankfurter.app/2022-07-11..?from=EUR&to=INR
```

The `..` suffix means "from start date through today" — open-ended. The response is compact JSON:

```json
{
  "base": "EUR",
  "start_date": "2022-07-11",
  "end_date": "2026-07-11",
  "rates": {
    "2022-07-11": { "INR": 82.9012 },
    "2022-07-12": { "INR": 83.1450 }
  }
}
```

All 7 pairs are fetched by changing the `from` parameter (EUR, USD, GBP, JPY, CNY, SGD, HKD). The Frankfurter API supports INR as a target for all of them, including CNY, SGD, and HKD — no synthetic cross-rate calculation is needed. Approximately 780 daily data points covering 3 years are returned per pair.

### Fallback — Yahoo Finance v8 via CORS Cascade

If Frankfurter is unavailable, the browser immediately retries against Yahoo Finance's chart API:

```
GET https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=3y
```

Because Yahoo Finance blocks direct browser requests with CORS headers, the request is routed through four public CORS proxy services **simultaneously** using `Promise.any()`. Whichever proxy responds first and successfully within 9 seconds is used.

| Yahoo Finance Ticker | Pair |
|---|---|
| `EURINR=X` | EUR / INR |
| `INR=X` | USD / INR |
| `GBPINR=X` | GBP / INR |
| `JPYINR=X` | JPY / INR |
| `SGDINR=X` | SGD / INR |
| `HKDINR=X` | HKD / INR |
| Synthetic: `INR=X` ÷ `CNY=X` | CNY / INR |

---

## Forecasting Models

### Forecast Horizons

The visual chart scales 1:1 with the chosen forecast horizon — a 1W selection shows 10 trading days of history and 5 trading days of forecast. The statistical models always use the full 3-year dataset for parameter estimation, regardless of the display horizon.

| Horizon | Trading Days Forecast | History Displayed |
|---|---|---|
| 1W | 5 | 10 days |
| 2W | 10 | 20 days |
| 1M | 22 | 44 days |
| 2M | 44 | 88 days |
| 3M | 66 | 132 days |

---

### Model 1: ARIMA(2,1,0)

> **Plain English:** ARIMA identifies how much today's exchange rate movement depends on the previous two days' movements, removes the price trend by differencing, and uses those learned patterns to project forward.

ARIMA(2,1,0) operates on first-differenced log prices — i.e., the daily log-return series $\Delta \ln S_t = \ln S_t - \ln S_{t-1}$ — making the model equivalent to a stationary AR(2) process:

$$\Delta \ln S_t = \mu + \phi_1 \Delta \ln S_{t-1} + \phi_2 \Delta \ln S_{t-2} + \varepsilon_t$$

**Parameter estimation via Yule-Walker equations:**

The autoregressive coefficients $\phi_1, \phi_2$ are solved from the autocorrelation structure of the return series. For a lag-$k$ autocorrelation $r_k$, the AR(2) Yule-Walker system is:

$$\begin{bmatrix} r_0 & r_1 \\ r_1 & r_0 \end{bmatrix} \begin{bmatrix} \phi_1 \\ \phi_2 \end{bmatrix} = \begin{bmatrix} r_1 \\ r_2 \end{bmatrix}$$

Closed-form solution:

$$\phi_1 = \frac{r_0 r_1 - r_1 r_2}{r_0^2 - r_1^2}, \qquad \phi_2 = \frac{r_0 r_2 - r_1^2}{r_0^2 - r_1^2}$$

A stationarity constraint clips $|\phi_1| + |\phi_2| < 0.97$ to prevent explosive forecasts.

**Forecasting $h$ steps ahead:** The AR recursion is iterated forward from the last known return, differences are cumulatively summed, and the result is exponentiated back to price space:

$$\ln \hat{S}_{t+h} = \ln S_t + \sum_{k=1}^{h} \hat{\Delta}_k$$

**Weight in ensemble: 35%**

---

### Model 2: Holt-Winters Additive

> **Plain English:** Holt-Winters separately tracks the current level of the rate, whether it is trending up or down, and recurring weekly or monthly seasonal patterns. It weights recent data more heavily than old data through exponential smoothing.

The additive form decomposes the series into three components updated at each time step:

**Level** — the current baseline, corrected for seasonality:
$$L_t = \alpha(y_t - S_{t-m}) + (1-\alpha)(L_{t-1} + T_{t-1})$$

**Trend** — the direction and speed of movement:
$$T_t = \beta(L_t - L_{t-1}) + (1-\beta)T_{t-1}$$

**Seasonal index** — the additive recurring component:
$$S_t = \gamma(y_t - L_t) + (1-\gamma)S_{t-m}$$

**Forecast** $h$ steps ahead:
$$\hat{y}_{t+h} = L_t + h \cdot T_t + S_{(t+h-1) \bmod m}$$

Parameters used: $\alpha = 0.35$, $\beta = 0.08$, $\gamma = 0.12$. The seasonal period $m$ is set to 5 trading days for 1W/2W horizons and 22 trading days for 1M+ horizons.

**Why it complements ARIMA:** ARIMA captures linear autocorrelation in the differenced series. Holt-Winters explicitly separates trend from seasonality and applies exponentially decaying weights to historical observations. The two models are structurally independent; combining them reduces single-model forecast error.

**Weight in ensemble: 35%**

---

### Model 3: Monte Carlo GBM

> **Plain English:** Monte Carlo runs 5,000 independent simulated futures simultaneously. Each path is different because it includes a random shock at every step calibrated to the historical volatility of the pair. The output is a fan of plausible futures, not a single line.

Exchange rate dynamics are modelled as Geometric Brownian Motion (GBM):

$$dS_t = \mu S_t \, dt + \sigma S_t \, dW_t$$

The exact discrete-time solution used in the simulation:

$$S_{t+1} = S_t \exp\!\left[\left(\mu - \frac{\sigma^2}{2}\right)\Delta t + \sigma\sqrt{\Delta t} \cdot Z\right], \quad Z \sim \mathcal{N}(0,1)$$

Parameters are estimated from the historical log-return series $r_t = \ln(S_t / S_{t-1})$:

$$\hat{\mu} = \bar{r}, \qquad \hat{\sigma} = \text{std}(r_t)$$

Normal random variates $Z$ are generated using the Box-Muller transform, which converts two uniform draws into a standard normal without rejection sampling:

$$Z = \sqrt{-2 \ln U_1} \cdot \cos(2\pi U_2), \qquad U_1, U_2 \sim \text{Uniform}(0,1)$$

After running all 5,000 paths for $h$ steps, the price distribution at each future day is summarised as:

- **P5 (Bear case):** 95% of paths end above this level
- **P50 (Base case):** Median across all 5,000 paths  
- **P95 (Bull case):** 95% of paths end below this level

Monte Carlo receives a slightly lower ensemble weight (30%) than the deterministic models because GBM assumes a pure random walk with no mean-reversion — a property that tends to overstate uncertainty for tightly managed INR cross-rates.

**Weight in ensemble: 30%**

---

### Ensemble Forecast

The three model outputs are combined at every forecast step by a fixed weighted average:

$$\hat{S}_{t+h}^{\text{ens}} = 0.35 \cdot \hat{S}_{t+h}^{\text{ARIMA}} + 0.35 \cdot \hat{S}_{t+h}^{\text{H-W}} + 0.30 \cdot \hat{S}_{t+h}^{\text{MC}_{P50}}$$

**Best Transfer Date selection:**

For **INR → FX** (sending Rupees — a lower rate means more foreign currency per Rupee):

$$h^* = \underset{h \in \{1,\ldots,T\}}{\arg\min}\; \hat{S}_{t+h}^{\text{ens}}$$

For **FX → INR** (receiving Rupees — a higher rate means more Rupees per unit of foreign currency):

$$h^* = \underset{h \in \{1,\ldots,T\}}{\arg\max}\; \hat{S}_{t+h}^{\text{ens}}$$

**Potential gain displayed in the banner:**

$$\text{Gain\%} = \frac{|\hat{S}_{t+h^*}^{\text{ens}} - S_t|}{S_t} \times 100$$

> This is a probabilistic estimate, not a guarantee. The Monte Carlo fan chart shows the full distribution of outcomes so the range of uncertainty is always visible.

---

## Technical Indicators

> **Plain English:** Technical indicators are mathematical summaries of price history that classify whether the current rate is cheap, expensive, gaining momentum, or losing it. The dashboard computes 8 of them and fuses them into a single 0–100 composite score.

All indicators are computed on the full 3-year dataset for statistical stability, not just the display window.

| Indicator | Core Formula | Signal |
|---|---|---|
| **RSI-14** | $100 - \frac{100}{1 + \text{AvgGain}_{14}/\text{AvgLoss}_{14}}$ | <30 oversold · >70 overbought |
| **MACD(12,26,9)** | $\text{EMA}_{12} - \text{EMA}_{26}$; histogram vs 9-day signal | Positive histogram = bullish momentum |
| **Bollinger %B** | $\frac{S_t - (μ - 2σ)}{4σ}$ on 20-day window | <0.2 at lower band · >0.8 at upper band |
| **Stochastic-14** | $\frac{S_t - \min_{14}}{\max_{14} - \min_{14}} \times 100$ | <20 oversold · >80 overbought |
| **Williams %R** | $\frac{\max_{14} - S_t}{\max_{14} - \min_{14}} \times (-100)$ | <−80 oversold · >−20 overbought |
| **ATR-14** | Mean of true range over 14 days | Higher = more volatile regime |
| **CCI-20** | $\frac{TP_t - \overline{TP}_{20}}{0.015 \cdot \text{MAD}_{20}}$ | <−100 statistically cheap · >+100 expensive |
| **Z-Score-20** | $\frac{S_t - \mu_{20}}{\sigma_{20}}$ | <−1.5 cheap · >+1.5 expensive |

**Composite Score (0–100):**

Each indicator is normalised to a 0–100 bullish scale, then combined with fixed weights:

$$\text{Score} = 0.20 \cdot \text{RSI} + 0.15 \cdot \text{MACD} + 0.12 \cdot \text{BB} + 0.12 \cdot \text{Stoch} + 0.10 \cdot \text{W\%R} + 0.10 \cdot \text{CCI} + 0.10 \cdot Z + 0.11 \cdot \text{ROC}$$

| Score | Classification |
|---|---|
| ≥ 70 | Strong signal — highlighted green |
| 40 – 69 | Neutral |
| < 40 | Weak / deteriorating — highlighted red |

The direction toggle inverts the composite: what is bearish for INR→FX (rate rising) is bullish for FX→INR (you receive more Rupees per unit).

---

## Risk Metrics

**Value at Risk (VaR)** — the maximum daily loss you would expect at a given confidence level:

$$\text{VaR}_{95} = -Q_{0.05}(r), \qquad \text{VaR}_{99} = -Q_{0.01}(r)$$

where $Q_\alpha$ is the $\alpha$-quantile of the empirical daily return distribution. A VaR₉₅ of 0.4% means the rate will not move more than 0.4% against you on 19 out of 20 days.

**Conditional VaR / Expected Shortfall** — the average loss on the days that *do* breach the VaR threshold:

$$\text{CVaR}_{95} = -\mathbb{E}[r \mid r < Q_{0.05}(r)]$$

CVaR is more informative than VaR because it describes the severity of tail events, not just their frequency threshold.

**Maximum Drawdown** — the largest peak-to-trough decline observed in the full history:

$$\text{MDD} = \max_t \frac{\text{Peak}_t - S_t}{\text{Peak}_t}, \qquad \text{Peak}_t = \max_{s \leq t} S_s$$

**Dollar-Cost Averaging (DCA)** — the average rate you would obtain by splitting your transfer equally across the last 5 or 10 trading days:

$$\text{DCA}_n = \frac{1}{n}\sum_{i=0}^{n-1} S_{t-i}$$

DCA is shown as a benchmark: if the best transfer date's predicted rate is only marginally better than the DCA rate, spreading the transfer is lower-risk than trying to time the market.

**Annualised Volatility** — computed on a rolling 20-day window of daily log-returns and scaled to annual:

$$\sigma_\text{ann} = \sigma_\text{daily} \times \sqrt{252}$$

---

## Statistical Analysis

**Hurst Exponent** — characterises whether the rate series trends, mean-reverts, or behaves as a random walk:

$$H = \frac{\ln(R/S)}{\ln(n)}$$

where $R$ is the range of the cumulative deviation series and $S$ is the standard deviation of returns.

| $H$ | Regime | Trading implication |
|---|---|---|
| $H < 0.45$ | Mean-reverting | Rate bounces back — buy dips, sell rallies |
| $H \approx 0.5$ | Random walk | No exploitable serial structure |
| $H > 0.55$ | Trending | Moves persist — follow the direction |

**Skewness** — asymmetry of the return distribution:

$$\gamma_1 = \frac{\mathbb{E}[(r-\mu)^3]}{\sigma^3}$$

Negative skew indicates occasional large drops are more common than large gains — the distribution has a heavier left tail than a symmetric model would suggest.

**Excess Kurtosis** — how fat the tails are relative to a normal distribution:

$$\gamma_2 = \frac{\mathbb{E}[(r-\mu)^4]}{\sigma^4} - 3$$

Values above 0 indicate fat tails — extreme rate moves happen more often than a Gaussian model predicts. FX return distributions almost universally exhibit positive excess kurtosis, which is why VaR and CVaR are computed from the empirical distribution rather than a normal approximation.

**Rolling Annualised Volatility** — computed over 10, 20, and 30-day windows simultaneously to show how the volatility regime has evolved. Compression of all three lines toward a common low often precedes a large directional breakout.

---

## Seasonality Analysis

**Day-of-Week Effect** — for each trading weekday $d$, the average of all historical daily log-returns falling on that weekday:

$$\bar{r}_d = \frac{1}{|T_d|} \sum_{t \in T_d} r_t, \qquad d \in \{\text{Mon, Tue, Wed, Thu, Fri}\}$$

**Monthly Seasonality** — same calculation grouped by calendar month:

$$\bar{r}_m = \frac{1}{|T_m|} \sum_{t \in T_m} r_t, \qquad m \in \{1, \ldots, 12\}$$

Green bars indicate the rate historically *fell* on that day or month — good for INR→FX transfers (fewer Rupees needed). Red bars indicate the rate historically *rose*.

> These are historical averages across the full 3-year dataset, not predictions. A month being historically green does not guarantee it will be green this year.

---

## Direction Toggle

**INR → FX (default):** You are sending Rupees abroad and purchasing foreign currency. You want the exchange rate as *low* as possible — fewer Rupees per unit of EUR/USD/GBP etc.

**FX → INR:** You are receiving a foreign payment in India. You want the exchange rate as *high* as possible — more Rupees per unit of foreign currency received.

When you switch direction, every displayed rate is mathematically inverted:

$$\tilde{S}_t = \frac{1}{S_t}$$

The following all flip simultaneously: the forecast chart Y-axis, the best-date objective (argmin ↔ argmax), the composite indicator score, the MC fan bands (P5 becomes P95 and vice versa), and the "potential gain" calculation.

---

## Deployment

### GitHub Pages

The repository is configured to deploy automatically via GitHub Actions on every push to `main`. The workflow (`deploy.yml`) only uploads `index.html` to GitHub Pages — it performs no computation, no data fetching, and contacts no external services.

```bash
# Fork or clone the repo, make your changes, then push
git push origin main
# GitHub Actions deploys automatically — live in ~2 minutes
```

No API keys, no secrets, no environment variables required.

### Local Testing

```bash
# Option A: Open directly — Frankfurter API works from file://
open index.html

# Option B: Serve locally
python3 -m http.server 8000
# → http://localhost:8000
```

---

## Repo Structure

```
FOREX_QUANT/
├── index.html                ← Complete application (HTML + CSS + JS, single file)
├── .nojekyll                 ← Disables Jekyll on GitHub Pages
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml        ← Deploys index.html to GitHub Pages on push
```

The entire application is one file. There is no `package.json`, no build configuration, no `requirements.txt`, and no data files to keep updated.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Single `index.html` — zero build step, zero npm, zero dependencies to install |
| Styling | Vanilla CSS with custom properties, dark terminal theme |
| Typography | [Outfit](https://fonts.google.com/specimen/Outfit) (UI) + [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) (numeric data) |
| Charts | [Chart.js 4.4](https://www.chartjs.org/) via cdnjs CDN |
| Quant math | Pure JavaScript — all models, all indicators, all risk metrics implemented from scratch |
| Primary data | [Frankfurter API](https://www.frankfurter.app/) — ECB reference rates, native CORS |
| Fallback data | Yahoo Finance v8 API via 4 parallel CORS proxies (`Promise.any`, 9s timeout) |
| Hosting | GitHub Pages — free, zero infrastructure, auto-deploys on push |

---

## Disclaimer

This tool is for analytical and educational purposes only. It does not constitute financial advice. All forecasts are probabilistic estimates derived from historical data and mathematical models. Past exchange rate patterns do not guarantee future movements. Currency markets are affected by macroeconomic, geopolitical, and regulatory factors that no model can fully capture. Consult a licensed financial advisor before making foreign exchange decisions.
