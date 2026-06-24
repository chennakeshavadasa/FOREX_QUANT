# FOREX_QUANT: Advanced Quantitative FX Dashboard

**Institutional-grade quantitative analysis framework for EUR/INR and USD/INR exchange rates.**  
Designed to optimize international capital transfers by forecasting optimal execution windows through the synthesis of robust statistical, probabilistic, and technical models.

🔗 **Live Dashboard** → [https://chennakeshavadasa.github.io/FOREX_QUANT/](https://chennakeshavadasa.github.io/FOREX_QUANT/)

---

## Purpose and Scope
In the context of cross-border capital allocation (specifically translating INR to base currencies like EUR or USD), minimizing the exchange rate maximizes the foreign currency yield. This framework operationalizes an ensemble of quantitative models to forecast the optimal execution window across configurable investment horizons (1 week to 3 months).

---

## Quantitative Methodology Breakdown

The core engine computes an array of advanced quantitative metrics to establish a data-driven, probabilistic perspective on the foreign exchange market microstructure.

### 1. Forecasting Models & Ensemble Architecture
We aggregate three fundamentally orthogonal mathematical approaches to forecast price trajectories. This multi-model ensemble mitigates the model risk inherent in single-assumption frameworks.

*   **ARIMA (Autoregressive Integrated Moving Average):**
    *   **Mechanism:** Captures linear dependencies and autocorrelation structures within the time series.
    *   **Execution:** The engine leverages an auto-optimization routine to derive the optimal `(p, d, q)` parameters by minimizing the Akaike Information Criterion (AIC). It models momentum via the AR component, mean-reversion of shocks via the MA component, and integrates difference transformations (I) to achieve stationarity.
*   **Holt-Winters ETS (Exponential Smoothing):**
    *   **Mechanism:** Isolates and projects structural seasonality and localized trend vectors.
    *   **Execution:** We employ additive trend and seasonal components. For condensed timeframes, it captures intraday and intra-week cyclicality; for extended horizons, it adapts to macroeconomic monthly and quarterly patterns.
*   **Monte Carlo GBM (Geometric Brownian Motion):**
    *   **Mechanism:** Generates a probabilistic distribution of future rate paths by simulating stochastic market permutations.
    *   **Execution:** We execute 5,000 independent simulations utilizing historical drift (mean log-return) and volatility (standard deviation). The output constructs a percentile fan (P5, P25, P50, P75, P95) to quantify the probability mass of the forecasted rate.
*   **Consensus Ensemble:**
    *   The final projected trajectory is a weighted amalgamation: `35% ARIMA + 35% Holt-Winters + 30% Monte Carlo Median`. The global minimum of this ensemble within the selected time horizon dictates the recommended transfer window.

### 2. Statistical Analysis & Time-Series Tests
Before predictive modeling, the system rigorously tests the structural properties of the market data.

*   **Hurst Exponent (H):**
    *   Calculated via Rescaled Range (R/S) analysis to measure the long-term memory of the series.
    *   **H < 0.5**: The market exhibits mean-reverting properties.
    *   **H ≈ 0.5**: The market follows a Brownian motion (Random Walk).
    *   **H > 0.5**: The market is trending, demonstrating persistent autocorrelation.
*   **Augmented Dickey-Fuller (ADF) Test:**
    *   Tests the null hypothesis that a unit root is present in the time series sample. Rejection of the null hypothesis confirms stationarity, a prerequisite for robust linear forecasting.
*   **Jarque-Bera Test & Distributional Moments:**
    *   Quantifies Skewness (asymmetry) and Excess Kurtosis (tail thickness). The JB test evaluates normality. FX markets typically exhibit leptokurtic distributions (fat tails), rendering standard normal assumptions inadequate for extreme event modeling.
*   **Autocorrelation Function (ACF):**
    *   Measures the correlation of the asset's log-returns with its own lagged values to detect serial dependencies.

### 3. Risk Management & Drawdown Metrics
Upside potential is contextualized through strict downside exposure quantification.

*   **Value at Risk (VaR 95% & 99%):**
    *   Estimated using the historical distribution of daily log-returns. A 95% VaR of -0.90% indicates a 5% probability that the daily loss will exceed 0.90%.
*   **Conditional Value at Risk (CVaR / Expected Shortfall):**
    *   Calculates the expected magnitude of the loss given that the VaR threshold has been breached. It serves as a superior measure of tail risk.
*   **Maximum Drawdown:**
    *   Calculates the most severe historical peak-to-trough retracement, providing a baseline for maximum historical capital degradation.
*   **Rolling Annualized Volatility:**
    *   Computes the standard deviation of log-returns over discrete trailing windows (10-day, 20-day, 30-day), annualized via multiplication by the square root of 252 trading days.

### 4. Technical Indicator Matrix
A suite of mathematical indicators employed to identify momentum shifts and volatility compression.

*   **RSI (Relative Strength Index):** A momentum oscillator constrained between 0 and 100, measuring the velocity and magnitude of directional price movements.
*   **MACD (Moving Average Convergence Divergence):** Evaluates the divergence between 12-period and 26-period Exponential Moving Averages (EMA) to identify trend acceleration.
*   **Bollinger Bands (%B and Bandwidth):** Constructs a dynamic volatility envelope 2 standard deviations away from a 20-period Simple Moving Average (SMA). Bandwidth compression frequently precedes volatility expansion.
*   **Stochastic Oscillator:** Normalizes the closing price relative to the high-low range over a defined lookback period.
*   **Williams %R:** An inverse momentum indicator quantifying overbought and oversold conditions.
*   **Z-Score (20-day rolling):** Represents the number of standard deviations the current spot rate deviates from its 20-day moving average, functioning as a primary signal for mean-reversion trades.

### 5. Seasonality & Market Microstructure
*   **Day-of-Week Effect:** Analyzes the empirical mean return stratified by weekday to identify systemic inefficiencies in liquidity provision.
*   **Monthly Seasonality:** Extracts macroscopic macroeconomic cycles and structural flows over the calendar year.
*   **Time-Series Decomposition:** Applies a multiplicative decomposition algorithm to partition the raw price feed into discrete Trend, Seasonal, and Residual (stochastic noise) components.

---

## Local Execution and System Updates

The analytical engine executes via Python, performing live data acquisition and statistical modeling prior to static deployment.

### System Requirements
Python 3.x is required alongside the following libraries:
```bash
pip install pandas numpy scipy yfinance statsmodels ta
```

### Data Refresh Protocol
To ingest the latest market data and recalculate the ensemble forecasts:

```bash
# 1. Execute the quantitative engine (fetches data and runs statistical models)
python3 engine.py

# 2. Compile the updated data array directly into the static dashboard architecture
python3 build_dashboard.py
```
Execution of these scripts updates the state of `index.html`. 

### Deployment to GitHub Pages
```bash
git add .
git commit -m "chore: Update quantitative data array"
git push origin main
```
Given the GitHub Actions CI/CD pipeline, the live environment will reflect the updated data structures within approximately 60 seconds.

---

## Architecture Stack
*   **Analytical Backend:** `Python 3` (yfinance, statsmodels, scipy, pandas, ta). Computations are performed statically ahead of time.
*   **Frontend Interface:** `HTML5`, `Vanilla CSS`, `Chart.js 4.4`.
*   **Deployment Infrastructure:** `GitHub Pages` utilizing custom GitHub Actions workflows for static site generation.

> **Disclaimer:** This framework is provided strictly for educational and analytical purposes. Quantitative models rely fundamentally on historical stationarity and precedent, which do not guarantee future market behavior. This repository does not constitute financial advice.
