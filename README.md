# FX Quant Dashboard

A quantitative foreign exchange analysis platform covering seven currency pairs against the Indian Rupee — EUR, USD, GBP, JPY, CNY, SGD, and HKD — with ensemble forecasting, technical indicators, risk analytics, and seasonality analysis.

**Live Dashboard:** [chennakeshavadasa.github.io/FOREX_QUANT](https://chennakeshavadasa.github.io/FOREX_QUANT/)

---

## Table of Contents

1. [What Does This Dashboard Do?](#what-does-this-dashboard-do)
2. [Architecture Overview](#architecture-overview)
3. [Data Acquisition](#data-acquisition)
4. [How the Best Transfer Date is Predicted](#how-the-best-transfer-date-is-predicted)
   - [Model 1: ARIMA](#model-1-arima)
   - [Model 2: Holt-Winters](#model-2-holt-winters)
   - [Model 3: Monte Carlo Simulation](#model-3-monte-carlo-simulation)
   - [Combining the Models](#combining-the-models)
   - [Picking the Optimal Date](#picking-the-optimal-date)
5. [Technical Indicators](#technical-indicators)
6. [Statistical Analysis](#statistical-analysis)
7. [Risk Metrics](#risk-metrics)
8. [Seasonality Analysis](#seasonality-analysis)
9. [Adaptive Window Scaling](#adaptive-window-scaling)
10. [Direction Toggle — INR to FX vs FX to INR](#direction-toggle)
11. [CNY/INR Synthetic Cross Rate](#cnyinr-synthetic-cross-rate)
12. [Disclaimer](#disclaimer)

---

## What Does This Dashboard Do?

> **Plain English Summary**

Imagine you need to send money abroad, or receive money from abroad, and you want to know: *"When is the best time to do it this week / month?"*

This dashboard analyses historical exchange rate data, runs three mathematical forecasting models simultaneously, and predicts the most favourable future date to execute your currency transfer. It covers seven major currency pairs against the Indian Rupee.

**Key things the dashboard gives you:**

| Feature | What it means for you |
|---|---|
| Best Transfer Date | The single future day when the models agree the rate will be most favourable |
| Forecast Chart | A chart showing where the exchange rate is likely to head over your chosen horizon |
| Technical Signals | 8 indicators that summarise whether the current rate is cheap or expensive |
| Risk Metrics | How much the rate can move against you on a bad day |
| Seasonality | Which day of the week or month historically has the best rates |
| Direction Toggle | Switch between "I'm sending INR abroad" and "I'm receiving money in INR" |

---

## Architecture Overview

```
engine.py          —  Downloads data, runs all models, saves results to JSON
build_dashboard.py —  Reads JSON and bakes it into a single HTML file
index.html         —  The dashboard, served via GitHub Pages (no server needed)
multi_data.json    —  Pre-computed analysis for all 7 pairs × 5 time windows = 35 datasets
```

The engine pre-computes all 35 analysis contexts (7 currencies × 5 forecast durations) and embeds them into one HTML file. The browser switches between them instantly with zero network calls.

---

## Data Acquisition

Historical daily OHLCV (Open, High, Low, Close, Volume) data is downloaded from Yahoo Finance using the `yfinance` Python library.

**Lookback windows used for each forecast horizon:**

| Forecast Horizon | Data Window Used for Models |
|---|---|
| 1 Week (7 days) | 180 days |
| 2 Weeks (14 days) | 365 days |
| 1 Month (30 days) | 365 days |
| 2 Months (60 days) | 730 days |
| 3 Months (90 days) | 730 days |

> **Why use more data than the forecast length?**
> Statistical models need enough historical data to learn patterns reliably. You wouldn't predict next week's weather by looking at only the last 7 days — you'd look at historical patterns over months. The same principle applies here.

Missing data (weekends, public holidays) is forward-filled — the last known rate is carried forward.

The **visual charts** only display data matching your selected forecast window (e.g., 7 days of history for a 7-day forecast), keeping the view tight and contextually relevant. The **statistical models** use the full lookback window behind the scenes for numerical stability.

---

## How the Best Transfer Date is Predicted

> **Plain English:** Three independent mathematical models each make a forecast of where the exchange rate will be on every future day in your window. Their predictions are averaged together (with different weights), and the day with the best predicted rate is highlighted as the optimal transfer date.

The dashboard uses **three independent forecasting models**, each with a different structural assumption about how exchange rates behave. Their outputs are combined into a single **ensemble forecast**.

---

### Model 1: ARIMA

> **Plain English:** ARIMA looks at the history of the exchange rate and finds patterns — like "whenever the rate goes up 3 days in a row, it tends to come back down." It then uses those patterns to project forward.

**Full name:** AutoRegressive Integrated Moving Average

**Core idea:** The rate today can be predicted from:
- Its own past values (AutoRegressive part)
- The past prediction errors (Moving Average part)
- One round of differencing to remove the trend (Integrated part)

**Equation:**

$$\phi(B)(1-B)^d \ln S_t = \theta(B)\varepsilon_t$$

Where:
- $S_t$ = exchange rate on day $t$
- $B$ = backshift operator ($B \ln S_t = \ln S_{t-1}$)
- $\phi(B)$ = autoregressive polynomial of order $p$
- $\theta(B)$ = moving-average polynomial of order $q$
- $d$ = number of differencing steps (typically 1 for FX rates)
- $\varepsilon_t$ = random noise term

**Choosing the best order (p, d, q):**

The model tests all combinations of $p, q \in \{0, 1, 2, 3\}$ and selects the one with the lowest **AIC (Akaike Information Criterion)**:

$$\text{AIC} = 2k - 2\ln(\hat{L})$$

where $k$ is the number of parameters and $\hat{L}$ is how well the model fits the data. Lower AIC = better balance of accuracy and simplicity.

**Confidence bands:** As you forecast further into the future, uncertainty grows. The 95% confidence interval widens as:

$$\text{Var}(\hat{S}_{t+h}) = \sigma^2 \sum_{j=0}^{h-1} \psi_j^2$$

**Weight in the final ensemble: 35%**

---

### Model 2: Holt-Winters

> **Plain English:** Holt-Winters is like a weather forecasting model — it separately tracks the "baseline level" of the rate, whether it's rising or falling (the trend), and repeating patterns within a week or month (seasonality). It gives more weight to recent data than old data.

**Full name:** Holt-Winters Exponential Smoothing (ETS — Error, Trend, Seasonality)

**Core idea:** Instead of treating all historical data equally, this model puts exponentially more weight on recent observations. It learns three things simultaneously: the current level, the direction of movement, and seasonal cycles.

**Equations (multiplicative form):**

Level — where the rate is right now, adjusted for seasonality:

$$\ell_t = \alpha \frac{y_t}{s_{t-m}} + (1-\alpha)(\ell_{t-1} + b_{t-1})$$

Trend — whether the rate is rising or falling:

$$b_t = \beta(\ell_t - \ell_{t-1}) + (1-\beta)b_{t-1}$$

Seasonality — recurring weekly/monthly patterns:

$$s_t = \gamma \frac{y_t}{\ell_t} + (1-\gamma)s_{t-m}$$

Forecast $h$ steps ahead:

$$\hat{y}_{t+h} = (\ell_t + h \cdot b_t) \cdot s_{t+h-m}$$

Where $\alpha, \beta, \gamma \in [0,1]$ are smoothing parameters (fitted automatically by minimising one-step forecast errors). $m$ is the seasonal period — set to 5 for weekly cycles and 22 for monthly cycles.

**Why this complements ARIMA:** ARIMA focuses on linear autocorrelation in the differenced series. Holt-Winters explicitly captures multiplicative seasonal cycles. They are structurally independent, so combining them reduces error.

**Weight in the final ensemble: 35%**

---

### Model 3: Monte Carlo Simulation

> **Plain English:** Monte Carlo runs 5,000 possible "futures" of the exchange rate simultaneously. Each simulated future is slightly different (because currency markets are partly random). The result is a fan of possibilities — showing not just the most likely outcome, but also the optimistic case (P95) and the pessimistic case (P5).

**Full name:** Monte Carlo Geometric Brownian Motion (GBM) Simulation

**Core idea:** Exchange rate returns are treated as random, following a normal distribution with a historical mean and standard deviation. The simulation rolls the dice 5,000 times per day per simulation path.

**The stochastic equation:**

$$dS_t = \mu S_t \, dt + \sigma S_t \, dW_t$$

Where $\mu$ is the drift (average daily return) and $\sigma$ is the volatility. The exact discrete solution for each day is:

$$S_{t+1}^{(i)} = S_t \exp\!\left[\left(\mu - \frac{\sigma^2}{2}\right) \frac{1}{252} + \sigma \sqrt{\frac{1}{252}} \cdot Z\right]$$

where $Z$ is a random draw from a standard normal distribution.

**Estimating parameters from history:**

$$\mu = \bar{r} + \frac{\sigma^2}{2}, \quad \sigma = \text{std}(r_t) \times \sqrt{252}$$

where $r_t = \ln(S_t / S_{t-1})$ are the daily log-returns.

**What you see on the chart:**
- **P50 (median):** The middle path — half the simulations end above this, half below
- **P5 / P95:** The extreme pessimistic and optimistic scenarios
- **Probability bar chart:** For each future day, the fraction of the 5,000 simulations where the rate is cheaper than today

**Weight in the final ensemble: 30%**

---

### Combining the Models

> **Plain English:** The three model predictions are blended together like a committee vote — each model has a say, weighted by its reliability for this type of data.

The final forecast on each future day is a weighted average:

$$\hat{S}_{t+h}^{\text{ensemble}} = 0.35 \times \hat{S}_{t+h}^{\text{ARIMA}} + 0.35 \times \hat{S}_{t+h}^{\text{HW}} + 0.30 \times \hat{S}_{t+h}^{\text{MC median}}$$

**Why these weights?**
- ARIMA and Holt-Winters each get 35% — they are deterministic models that capture different structural properties and are equally reliable at short-to-medium horizons.
- Monte Carlo gets 30% — it captures uncertainty correctly but assumes a pure random walk (no mean-reversion), which tends to underperform for managed currency pairs like INR crosses.

---

### Picking the Optimal Date

> **Plain English:** After combining the three models' predictions into one forecast line, the dashboard simply looks for the day with the best predicted rate within your chosen window and marks it with a green dot.

**For INR → FX transfers** (you are spending Rupees to buy foreign currency):
A *lower* rate is better — you get more foreign currency per Rupee.

$$h^* = \underset{h \in \{1,\ldots,T\}}{\arg\min} \; \hat{S}_{t+h}^{\text{ensemble}}$$

**For FX → INR transfers** (you are receiving Rupees from foreign currency):
A *higher* rate is better — you get more Rupees per unit of foreign currency.

$$h^* = \underset{h \in \{1,\ldots,T\}}{\arg\max} \; \hat{S}_{t+h}^{\text{ensemble}}$$

**Potential gain:**

$$\text{Gain \%} = \frac{|S_{\text{today}} - \hat{S}_{t+h^*}^{\text{ensemble}}|}{S_{\text{today}}} \times 100$$

> **Important:** This is a probabilistic estimate, not a guarantee. Currency markets are inherently unpredictable. The optimal date represents the model's best guess — the Monte Carlo fan chart shows the full range of uncertainty.

---

## Technical Indicators

> **Plain English:** Technical indicators are mathematical formulas applied to the price history that summarise whether the currency is currently "cheap", "expensive", "rising", or "falling." This dashboard computes 8 of them and combines them into a single composite score from 0 (strong sell) to 100 (strong buy).

All indicators are computed on the chart window that matches your selected forecast duration.

| Indicator | What it measures | Simple signal |
|---|---|---|
| **RSI-14** | Momentum — how fast price has risen vs fallen over 14 days | Below 30: cheap (buy); Above 70: expensive (wait) |
| **MACD(12,26,9)** | Trend direction — difference between fast and slow moving averages | Line crosses above signal: upward momentum |
| **Bollinger %B** | Where the current rate sits within its normal range | Near 0: at the low end (cheap); Near 1: at the high end |
| **Stochastic(14,3)** | Where today's price sits vs recent highs and lows | Below 20: oversold; Above 80: overbought |
| **Williams %R** | Similar to Stochastic, different calculation | Below -80: cheap; Above -20: expensive |
| **ATR-14** | How much the rate moves on an average day | Higher = more volatile = more risk per day |
| **CCI-20** | How far the rate is from its 20-day average (in standard units) | Below -100: unusually cheap; Above +100: unusually expensive |
| **Z-Score(20d)** | Standard deviations above/below the 20-day mean | Below -2: statistically cheap; Above +2: statistically expensive |

**Mathematical formulas:**

RSI:

$$\text{RSI} = 100 - \frac{100}{1 + \frac{\text{Avg Gain (14d)}}{\text{Avg Loss (14d)}}}$$

Bollinger %B (where is today's rate within the Bollinger Bands?):

$$\%B = \frac{S_t - \text{Lower Band}}{\text{Upper Band} - \text{Lower Band}}$$

Z-Score (how many standard deviations from the mean?):

$$Z = \frac{S_t - \mu_{20}}{\sigma_{20}}$$

---

## Statistical Analysis

> **Plain English:** Beyond the forecast, the dashboard runs a set of statistical tests on the historical data to characterise how the exchange rate behaves — does it tend to come back to average? Does it follow trends? Are big moves more common than a normal distribution would predict?

### Hurst Exponent

**What it tells you:** Whether the exchange rate tends to **trend** (keep moving in the same direction), **mean-revert** (bounce back), or move **randomly**.

**Formula:**

$$H = \frac{\ln(R/S)}{\ln(n)}$$

where $R/S$ is the rescaled range of the return series.

| Value of H | Meaning | Trading implication |
|---|---|---|
| H < 0.5 | Mean-reverting | Rate bounces back — buy dips, sell rallies |
| H ≈ 0.5 | Random walk | No exploitable pattern |
| H > 0.5 | Trending | Moves persist — follow the trend |

### Return Distribution Tests

**Skewness** — is the distribution of daily returns lopsided?

$$\gamma_1 = \frac{E[(r - \mu)^3]}{\sigma^3}$$

Positive skew: more frequent small losses, occasional large gains. Negative: more frequent small gains, occasional large crashes.

**Excess Kurtosis** — are extreme moves more common than a normal distribution predicts?

$$\gamma_2 = \frac{E[(r - \mu)^4]}{\sigma^4} - 3$$

Values above 0 indicate "fat tails" — large rate movements happen more often than a simple bell curve would suggest.

**Augmented Dickey-Fuller (ADF) Test:** Tests whether the return series is stationary (suitable for ARIMA). A p-value below 0.05 confirms stationarity.

**Jarque-Bera Test:** Tests whether returns follow a normal distribution. A very low p-value confirms non-normality (fat tails), which is almost always the case for FX returns.

### Annualised Volatility

$$\sigma_{\text{annual}}^{(n)} = \sigma_{\text{daily}}^{(n)} \times \sqrt{252}$$

Computed for rolling windows of $n \in \{10, 20, 30\}$ trading days, where $\sigma_{\text{daily}}^{(n)}$ is the standard deviation of daily log-returns over those $n$ days.

---

## Risk Metrics

> **Plain English:** These metrics answer: "How much can I lose / gain if I wait?" and "What's the worst that could realistically happen?"

### Value at Risk (VaR)

**What it means:** The maximum loss you'd expect on a given day, 95% or 99% of the time.

> Example: If 95% VaR = 0.4%, it means on 19 out of 20 days, the rate will not move more than 0.4% against you.

$$\text{VaR}_{95} = -Q_{0.05}(r)$$

$$\text{VaR}_{99} = -Q_{0.01}(r)$$

where $Q_\alpha$ is the $\alpha$-th quantile of the historical daily returns.

### Conditional VaR / Expected Shortfall (CVaR)

**What it means:** On the worst 5% of days — the days that *do* breach the VaR threshold — what is the average loss?

$$\text{CVaR}_{95} = -E[r \mid r < Q_{0.05}(r)]$$

CVaR is considered more informative than VaR because it describes the severity of tail events, not just their threshold.

### Maximum Drawdown

**What it means:** The largest drop the exchange rate has experienced from a peak to a subsequent trough in the historical window.

$$\text{MDD} = \max_{t \in [0,T]} \frac{\text{Peak}_t - S_t}{\text{Peak}_t}$$

where $\text{Peak}_t = \max_{s \leq t} S_s$.

### Dollar-Cost Averaging (DCA)

**What it means:** Instead of transferring all your money on one day, you split it across 5 or 10 days. The DCA rate is the average rate you'd get.

$$\text{DCA}_n = \frac{1}{n} \sum_{i=0}^{n-1} S_{t-i}$$

DCA reduces the risk of timing the market badly — you automatically buy at both high and low rates, averaging out.

---

## Seasonality Analysis

> **Plain English:** Are there patterns in which day of the week or month the exchange rate tends to be cheapest? This section analyses historical data to find those patterns.

### Day-of-Week Effect

For each weekday, the average daily log-return is computed across all historical data:

$$\bar{r}_d = \frac{1}{|T_d|} \sum_{t \in T_d} r_t$$

**Green bars** = days when the foreign currency tends to be cheaper on average (good for INR→FX transfers). **Red bars** = days when it tends to be more expensive.

> Note: These are historical averages — not guarantees. A Tuesday being historically "green" doesn't mean next Tuesday will definitely be cheap.

### Monthly Seasonality

Same idea, grouped by calendar month:

$$\bar{r}_m = \frac{1}{|T_m|} \sum_{t \in T_m} r_t$$

### Time-Series Decomposition

The full rate series is decomposed into three components:

$$S_t = T_t \times C_t \times R_t$$

| Component | What it is |
|---|---|
| $T_t$ — Trend | The long-run direction (e.g., Rupee gradually weakening) |
| $C_t$ — Seasonal | Recurring cyclical patterns within the window |
| $R_t$ — Residual | What's left over — the "noise" that isn't explained by trend or seasonality |

---

## Adaptive Window Scaling

> **Plain English:** When you select "1 Week" forecast, the charts show you the last 7 days of data and forecast the next 7 days. When you select "3 Months," the charts show the last 3 months and forecast the next 3 months. The analysis adapts to your chosen horizon — it doesn't show you the same view regardless of what you select.

The charts scale **1:1 with the forecast window** — the historical view always matches the forward view in length. This is intentional: comparing 7 days of history against a 7-day forecast is contextually meaningful; comparing 2 years of history against a 7-day forecast would make the forecast invisible.

Behind the scenes, statistical models still use the full lookback window (up to 2 years) for robust parameter estimation, but the display adapts to your selection.

---

## Direction Toggle

> **Plain English:**
> - **INR → FX (default):** You are sending Rupees abroad. You want the exchange rate to be *as low as possible* — fewer Rupees needed to buy 1 Euro/Dollar/Pound.
> - **FX → INR:** You are receiving foreign money in India. You want the exchange rate to be *as high as possible* — more Rupees received per Euro/Dollar/Pound.
>
> Clicking the toggle flips the entire dashboard: the charts invert, the "best date" changes, and all forecasts are recalculated from your perspective.

**What mathematically changes when you switch to FX → INR:**

All displayed rates are inverted:

$$\tilde{S}_t = \frac{1}{S_t}$$

For example, if EUR/INR = 90.5, then in FX→INR mode it shows INR/EUR = 0.01105 (how many Euros per 1 Rupee you'd receive back).

The optimal date switches from minimising to maximising the ensemble:

$$h^* = \underset{h}{\arg\min} \; \tilde{S}_{t+h} \equiv \underset{h}{\arg\max} \; S_{t+h}$$

The Monte Carlo fan chart also flips — what was the P5 (pessimistic) band becomes P95 (optimistic) when viewed from the INR-receiver's perspective, and vice versa.

---

## CNY/INR Synthetic Cross Rate

> **Plain English:** Yahoo Finance does not directly provide historical CNY/INR data. Instead, the dashboard constructs it using two rates that *are* available: USD/INR and USD/CNY. Since everything is priced against the US Dollar, you can calculate CNY/INR by dividing one by the other.

**Formula:**

$$S_t^{\text{CNY/INR}} = \frac{S_t^{\text{USD/INR}}}{S_t^{\text{USD/CNY}}}$$

**Sources:**
- `INR=X` on Yahoo Finance: USD/INR rate (how many INR per 1 USD)
- `CNY=X` on Yahoo Finance: USD/CNY rate (how many CNY per 1 USD)

Both series are aligned to their common trading dates before division. This gives a complete daily OHLCV series for CNY/INR.

**The triangular arbitrage identity** guarantees this is mathematically exact in liquid markets:

$$\frac{\text{USD}}{\text{INR}} \div \frac{\text{USD}}{\text{CNY}} = \frac{\text{CNY}}{\text{INR}}$$

All downstream models (ARIMA, Holt-Winters, Monte Carlo) run identically on this synthetic series as on any directly quoted pair.

---

## Disclaimer

This tool is for analytical and educational purposes only. It does not constitute financial advice. All forecasts are probabilistic estimates derived from historical data and mathematical models. Past patterns do not guarantee future exchange rate movements. Currency markets are affected by macroeconomic, geopolitical, and regulatory factors that no model can fully capture. Consult a licensed financial advisor before making foreign exchange decisions.
