# FX Quant Dashboard

A quantitative foreign exchange analysis platform covering seven INR currency pairs — EUR/INR, USD/INR, GBP/INR, JPY/INR, CNY/INR, SGD/INR, and HKD/INR — with ensemble forecasting, technical indicators, and risk analytics.

**Live Dashboard:** [chennakeshavadasa.github.io/FOREX_QUANT](https://chennakeshavadasa.github.io/FOREX_QUANT/)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Acquisition and Preprocessing](#data-acquisition-and-preprocessing)
3. [Mathematical Basis for Optimal Transfer Date Prediction](#mathematical-basis-for-optimal-transfer-date-prediction)
   - [Model 1: ARIMA](#model-1-arima-autoregressive-integrated-moving-average)
   - [Model 2: Holt-Winters ETS](#model-2-holt-winters-ets-exponential-smoothing)
   - [Model 3: Monte Carlo GBM](#model-3-monte-carlo-gbm-geometric-brownian-motion)
   - [Ensemble Aggregation](#ensemble-aggregation)
   - [Optimal Date Selection](#optimal-date-selection)
4. [Technical Indicators](#technical-indicators)
5. [Statistical Analysis](#statistical-analysis)
6. [Risk Metrics](#risk-metrics)
7. [Seasonality Analysis](#seasonality-analysis)
8. [Adaptive Window Scaling](#adaptive-window-scaling)
9. [Direction Toggle: INR to FX vs FX to INR](#direction-toggle)
10. [CNY/INR Synthetic Cross Rate](#cnyinr-synthetic-cross-rate)

---

## Architecture Overview

```
engine.py          —  Data fetching, quantitative models, JSON output
build_dashboard.py —  Embeds JSON into standalone index.html
index.html         —  Single-file dashboard served via GitHub Pages
multi_data.json    —  Pre-computed analysis for all pairs and durations
```

The engine runs all five forecast windows (7d, 14d, 30d, 60d, 90d) for each of the seven currency pairs — 35 distinct analysis contexts — and embeds them into a single HTML file. The client-side JavaScript switches between pre-computed datasets on user interaction with zero network calls.

---

## Data Acquisition and Preprocessing

Historical OHLCV data is fetched from Yahoo Finance using the `yfinance` library. Each pair uses an adaptive lookback window proportional to the selected forecast horizon:

| Forecast Horizon | Lookback Window |
|-----------------|-----------------|
| 7 days          | 180 days        |
| 14 days         | 365 days        |
| 30 days         | 365 days        |
| 60 days         | 730 days        |
| 90 days         | 730 days        |

Forward-filling is applied to handle weekend and holiday gaps. The visual chart renders only the last N days matching the forecast horizon, keeping the display contextually tight, while statistical models operate on the full lookback window for numerical stability.

---

## Mathematical Basis for Optimal Transfer Date Prediction

This is the core quantitative question: **on which future date should you execute a foreign exchange transfer to get the best rate?**

The dashboard does not make a single deterministic prediction. Instead, it constructs a probability-weighted ensemble of three independent time-series models, each with a different structural assumption about how exchange rates evolve. The date with the minimum ensemble-predicted rate (for INR-to-FX transfers) across the forecast horizon is marked as the **optimal transfer window**.

### Model 1: ARIMA (AutoRegressive Integrated Moving Average)

**Structural assumption:** Past values and past forecast errors linearly predict future values. The series is differenced to achieve stationarity.

**Mathematical formulation:**

The general ARIMA(p, d, q) model on the log-price series $\ln S_t$ after $d$ rounds of differencing:

$$\phi(B)(1-B)^d \ln S_t = \theta(B)\epsilon_t$$

where:
- $B$ is the backshift operator, $B \ln S_t = \ln S_{t-1}$
- $\phi(B) = 1 - \phi_1 B - \phi_2 B^2 - \cdots - \phi_p B^p$ is the AR polynomial
- $\theta(B) = 1 + \theta_1 B + \theta_2 B^2 + \cdots + \theta_q B^q$ is the MA polynomial
- $\epsilon_t \sim \mathcal{N}(0, \sigma^2)$ are white noise innovations

**Order selection:** The optimal $(p, d, q)$ is determined by minimizing the Akaike Information Criterion:

$$\text{AIC} = 2k - 2\ln(\hat{L})$$

where $k = p + q + 1$ and $\hat{L}$ is the maximized log-likelihood. The search tests all combinations within $p, q \in \{0,1,2,3\}$ and $d=1$ (confirmed by Augmented Dickey-Fuller test). The order with the lowest AIC is retained.

**95% Confidence Interval:** Forecast variance grows linearly with horizon $h$:

$$\text{Var}(\hat{S}_{t+h}) = \sigma^2 \sum_{j=0}^{h-1} \psi_j^2$$

where $\psi_j$ are the MA-infinity representation coefficients. The 95% CI is $\hat{S}_{t+h} \pm 1.96\sqrt{\text{Var}(\hat{S}_{t+h})}$.

**Weight in ensemble:** 35%

---

### Model 2: Holt-Winters ETS (Exponential Smoothing)

**Structural assumption:** The series has a level, a local trend, and a multiplicative seasonal component. Recent observations receive exponentially decaying weights.

**Mathematical formulation (multiplicative):**

Level update:
$$\ell_t = \alpha \frac{y_t}{s_{t-m}} + (1-\alpha)(\ell_{t-1} + b_{t-1})$$

Trend update:
$$b_t = \beta(\ell_t - \ell_{t-1}) + (1-\beta)b_{t-1}$$

Seasonal update:
$$s_t = \gamma \frac{y_t}{\ell_t} + (1-\gamma)s_{t-m}$$

$h$-step forecast:
$$\hat{y}_{t+h} = (\ell_t + h b_t) \cdot s_{t+h-m}$$

where $\alpha, \beta, \gamma \in [0,1]$ are smoothing parameters estimated by minimizing the sum of squared one-step-ahead errors. The seasonal period $m$ is set to 5 (weekly) for short windows and 22 (monthly) for longer windows.

**Why this complements ARIMA:** ARIMA assumes linear dynamics in the differenced series and cannot capture multiplicative seasonality. Holt-Winters explicitly models cyclical patterns, making the two models structurally independent.

**Weight in ensemble:** 35%

---

### Model 3: Monte Carlo GBM (Geometric Brownian Motion)

**Structural assumption:** Exchange rate log-returns follow a Gaussian random walk with drift — the risk-neutral continuous-time model used in Black-Scholes theory.

**Mathematical formulation:**

Under GBM, the exchange rate $S_t$ satisfies the stochastic differential equation:

$$dS_t = \mu S_t \, dt + \sigma S_t \, dW_t$$

with exact solution:

$$S_{t+\Delta t} = S_t \exp\!\left[\left(\mu - \frac{\sigma^2}{2}\right)\Delta t + \sigma \sqrt{\Delta t} \, Z\right], \quad Z \sim \mathcal{N}(0,1)$$

**Parameter estimation from historical data:**

Daily log-returns: $r_t = \ln(S_t / S_{t-1})$

$$\hat{\mu} = \bar{r} + \frac{\hat{\sigma}^2}{2}, \quad \hat{\sigma} = \text{std}(r_t) \times \sqrt{252}$$

**Simulation:** 5,000 independent paths are simulated over the forecast horizon $T$ (in business days). For each path $i$ and horizon step $h$:

$$S_{t+h}^{(i)} = S_t \prod_{k=1}^{h} \exp\!\left[\left(\hat{\mu} - \frac{\hat{\sigma}^2}{2}\right) \frac{1}{252} + \hat{\sigma} \sqrt{\frac{1}{252}} Z_k^{(i)}\right]$$

**Quantile extraction:** From the 5,000 terminal distributions at each future date, the P5, P25, P50, P75, and P95 quantiles are extracted. The P50 (median) is used in the ensemble.

$$\hat{S}_{t+h}^{\text{MC}} = Q_{0.50}\!\left\{S_{t+h}^{(i)}\right\}_{i=1}^{5000}$$

**Probability metric displayed on dashboard:** For each future date $h$, the dashboard shows $P(S_{t+h} < S_t)$ — the fraction of simulated paths where the future rate is below the current rate, i.e., the probability of a more favourable transfer rate.

**Weight in ensemble:** 30%

---

### Ensemble Aggregation

The three model forecasts are combined as a deterministic weighted linear combination at each future date $h$:

$$\hat{S}_{t+h}^{\text{ens}} = 0.35 \cdot \hat{S}_{t+h}^{\text{ARIMA}} + 0.35 \cdot \hat{S}_{t+h}^{\text{HW}} + 0.30 \cdot \hat{S}_{t+h}^{\text{MC P50}}$$

The weights reflect the relative reliability of each model for short to medium horizons on mean-reverting FX series. ARIMA and Holt-Winters are given equal weight for their complementary linear-versus-seasonal decompositions. Monte Carlo receives slightly lower weight because GBM assumes pure random-walk dynamics (no mean reversion), which tends to underestimate long-term reversion in managed FX pairs like INR crosses.

---

### Optimal Date Selection

Given the ensemble forecast vector $\hat{\mathbf{S}}^{\text{ens}} = [\hat{S}_{t+1}^{\text{ens}}, \ldots, \hat{S}_{t+T}^{\text{ens}}]$:

**For INR → FX transfers** (buying foreign currency with Rupees), a lower rate means more units of the foreign currency per Rupee. The optimal date is:

$$h^* = \arg\min_{h \in \{1,\ldots,T\}} \hat{S}_{t+h}^{\text{ens}}$$

**For FX → INR transfers** (receiving Rupees from foreign currency), a higher rate means more Rupees per unit of foreign currency. The direction is inverted and $h^*$ maximises the ensemble:

$$h^* = \arg\max_{h \in \{1,\ldots,T\}} \hat{S}_{t+h}^{\text{ens}}$$

The saving percentage shown is:

$$\text{Saving \%} = \frac{|S_t - \hat{S}_{t+h^*}^{\text{ens}}|}{S_t} \times 100$$

**Important caveat:** This is a probabilistic estimate, not a guarantee. All three models extrapolate under specific distributional assumptions. The ensemble minimum identifies the single most-likely optimal point, but the Monte Carlo fan chart shows the full uncertainty distribution.

---

## Technical Indicators

All indicators are computed on the chart window (equal in length to the forecast horizon) to ensure visual and analytical consistency.

| Indicator | Formula | Signal Logic |
|-----------|---------|-------------|
| **RSI-14** | $RSI = 100 - \frac{100}{1 + RS}$, $RS = \frac{\text{Avg Gain}}{\text{Avg Loss}}$ over 14 periods | >70: overbought (FX expensive); <30: oversold (FX cheap) |
| **MACD(12,26,9)** | $\text{MACD} = \text{EMA}_{12} - \text{EMA}_{26}$; Signal $= \text{EMA}_9(\text{MACD})$ | MACD crossing above Signal: bullish momentum |
| **Bollinger %B** | $\%B = \frac{S_t - \text{Lower}_{20,2\sigma}}{\text{Upper}_{20,2\sigma} - \text{Lower}_{20,2\sigma}}$ | <0.1: rate near lower band (cheap to buy FX); >0.9: near upper band |
| **Stochastic(14,3)** | $\%K = \frac{S_t - \text{Low}_{14}}{\text{High}_{14} - \text{Low}_{14}} \times 100$ | <20: oversold; >80: overbought |
| **Williams %R** | $\%R = \frac{\text{High}_{14} - S_t}{\text{High}_{14} - \text{Low}_{14}} \times (-100)$ | <-80: oversold; >-20: overbought |
| **ATR-14** | $\text{ATR} = \text{EMA}_{14}(\text{TrueRange}_t)$ | Volatility magnitude in INR |
| **CCI-20** | $\text{CCI} = \frac{S_t - \text{SMA}_{20}}{0.015 \cdot \text{MAD}_{20}}$ | <-100: oversold; >+100: overbought |
| **Z-Score(20d)** | $Z = \frac{S_t - \mu_{20}}{\sigma_{20}}$ | Deviation from 20-day mean in standard deviations |
| **SMA-50 Trend** | $\text{SMA}_{50} = \frac{1}{50}\sum_{i=0}^{49} S_{t-i}$ | $S_t > \text{SMA}_{50}$: uptrend in FX rate |

The composite signal score aggregates all indicator readings into a 0–100 scale, where 0 = strong sell and 100 = strong buy (from an INR-to-FX perspective).

---

## Statistical Analysis

### Hurst Exponent (R/S Analysis)

The Hurst exponent $H$ measures long-range dependence in the return series, estimated via rescaled range analysis:

$$H = \frac{\ln(R/S)}{\ln(n)}$$

where $R/S$ is the rescaled range of the return series over $n$ observations. Interpretation:

- $H < 0.5$: Mean-reverting (anti-persistent). The rate tends to return to its mean — buy dips.
- $H = 0.5$: Geometric Brownian Motion (random walk). No exploitable autocorrelation.
- $H > 0.5$: Trending (persistent). Moves in the current direction tend to continue.

### Return Distribution Tests

- **Skewness:** $\gamma_1 = \frac{E[(r - \mu)^3]}{\sigma^3}$ — asymmetry of the log-return distribution.
- **Excess Kurtosis:** $\gamma_2 = \frac{E[(r - \mu)^4]}{\sigma^4} - 3$ — fat-tail risk relative to a normal distribution.
- **Jarque-Bera Test:** $JB = n \left(\frac{\gamma_1^2}{6} + \frac{(\gamma_2)^2}{24}\right) \sim \chi^2_2$ — tests for normality; high JB values indicate non-normal (fat-tailed) returns.
- **Augmented Dickey-Fuller Test:** Tests the null hypothesis $H_0: \phi = 1$ (unit root, non-stationary). Rejection confirms stationarity of the return series.

### Rolling Volatility

Three rolling windows of annualised volatility are plotted:

$$\sigma_{\text{ann}}^{(n)} = \sigma_{\text{daily}}^{(n)} \times \sqrt{252}, \quad \sigma_{\text{daily}}^{(n)} = \text{std}\!\left(r_{t-n+1}, \ldots, r_t\right)$$

for $n \in \{10, 20, 30\}$ trading days.

---

## Risk Metrics

### Value at Risk and Expected Shortfall

Let $r_t$ denote daily log-returns. Define the empirical quantile function $Q_\alpha$ over the historical sample.

$$\text{VaR}_{95} = -Q_{0.05}(r), \quad \text{VaR}_{99} = -Q_{0.01}(r)$$

$$\text{CVaR}_{95} = -E[r \mid r < Q_{0.05}(r)] \quad \text{(Expected Shortfall)}$$

CVaR is the average loss in the worst 5% of days — a coherent risk measure that satisfies sub-additivity, unlike VaR.

### Maximum Drawdown

$$\text{MDD} = \max_{t \in [0,T]} \frac{\text{Peak}_t - S_t}{\text{Peak}_t}, \quad \text{Peak}_t = \max_{s \leq t} S_s$$

This measures the largest peak-to-trough decline in the exchange rate over the historical window.

### Dollar-Cost Averaging Rates

The DCA rate over $n$ days is the simple arithmetic mean of the last $n$ closing rates:

$$\text{DCA}_n = \frac{1}{n} \sum_{i=0}^{n-1} S_{t-i}$$

Executing a transfer in equal instalments over $n$ days converges to this rate, reducing single-execution risk.

---

## Seasonality Analysis

### Day-of-Week Effect

For each weekday $d \in \{\text{Mon}, \ldots, \text{Fri}\}$, the mean log-return is computed over all historical observations falling on that day:

$$\bar{r}_d = \frac{1}{|T_d|} \sum_{t \in T_d} r_t$$

A significantly negative $\bar{r}_d$ (in INR-to-FX mode) indicates that the foreign currency rate tends to fall on that day — a statistically favourable day for INR-to-FX purchases.

### Monthly Seasonality

The same computation is applied by calendar month:

$$\bar{r}_m = \frac{1}{|T_m|} \sum_{t \in T_m} r_t$$

### Time-Series Decomposition (Multiplicative STL)

The rate series is decomposed as:

$$S_t = T_t \cdot C_t \cdot R_t$$

where:
- $T_t$ is the underlying trend (extracted via Loess smoothing)
- $C_t$ is the cyclical-seasonal component (periodic patterns)
- $R_t$ is the irregular residual

The decomposition reveals whether recent rate movements are trend-driven or mean-reverting seasonal noise.

---

## Adaptive Window Scaling

A core design principle of this dashboard is that **the analysis window scales with the selected forecast duration**. When a user selects a 1-week forecast, the charts and statistical models operate on data from approximately the last 30 trading days — a tight, recent window. When the user selects a 3-month forecast, models are calibrated on up to 2 years of data to capture the longer-term distributional properties.

This ensures that:
1. Short-window forecasts reflect current micro-structure and recent volatility.
2. Long-window forecasts are statistically robust via larger sample sizes.
3. Model AIC comparisons are valid within the same calibration window.

---

## Direction Toggle

The **INR → FX** mode (default) models the perspective of an investor or individual converting Indian Rupees into a foreign currency. A lower exchange rate is favourable — more foreign currency per Rupee.

The **FX → INR** mode models the perspective of repatriating foreign earnings or receiving remittances. A higher exchange rate is favourable — more Rupees per unit of foreign currency. In this mode:

- All displayed rates are inverted: $\tilde{S}_t = 1 / S_t$
- The optimal date selector switches from $\arg\min$ to $\arg\max$ of the ensemble
- The seasonality colour coding inverts (positive return days highlighted as favourable)
- Risk scenario tables reframe from FX received to INR received

---

## CNY/INR Synthetic Cross Rate

Yahoo Finance does not provide historical time-series data for the direct CNY/INR pair. The dashboard constructs a synthetic cross rate using two liquid USD cross rates:

$$S_t^{\text{CNY/INR}} = \frac{S_t^{\text{USD/INR}}}{S_t^{\text{USD/CNY}}}$$

where:
- $S_t^{\text{USD/INR}}$ is downloaded as the ticker `INR=X` (USD per INR, inverted as INR per USD)
- $S_t^{\text{USD/CNY}}$ is downloaded as the ticker `CNY=X` (USD per CNY, inverted as CNY per USD)

Both series are aligned on common trading dates (intersection of their indices) before division. This produces a synthetic daily OHLCV series for CNY/INR with the same statistical properties as any directly quoted pair.

The triangular arbitrage relationship holds exactly in liquid markets:

$$\frac{\text{USD}}{\text{INR}} \div \frac{\text{USD}}{\text{CNY}} = \frac{\text{CNY}}{\text{INR}}$$

All downstream models (ARIMA, Holt-Winters, Monte Carlo) operate identically on this synthetic series.

---

## Disclaimer

This tool is for analytical and educational purposes only. It does not constitute financial advice. All forecasts are probabilistic estimates based on historical data and statistical models. Past patterns do not guarantee future exchange rate movements. Consult a licensed financial advisor before making foreign exchange decisions.
