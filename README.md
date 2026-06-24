# 📊 FOREX_QUANT: Advanced Quantitative FX Dashboard

> **Institutional-grade quantitative analysis for EUR/INR and USD/INR exchange rates.**  
> Designed to remove the guesswork from international money transfers by leveraging robust statistical, technical, and probabilistic models.

🔗 **Live Dashboard** → [https://chennakeshavadasa.github.io/FOREX_QUANT/](https://chennakeshavadasa.github.io/FOREX_QUANT/)

---

## 🎯 Purpose
When transferring money internationally (e.g., INR to EUR or USD), a lower exchange rate yields more foreign currency per Rupee. This dashboard synthesizes multiple quantitative models to forecast the **optimal transfer window** across different time horizons (1 Week to 3 Months). 

---

## 🔬 Comprehensive Methodology Breakdown

The engine behind this dashboard computes an array of advanced quantitative metrics to form a robust, data-driven perspective on the FX market.

### 1. Forecasting Models & Ensemble
We combine three fundamentally different mathematical approaches to predict the future price path. This avoids the pitfalls of relying on a single assumption framework.

*   **ARIMA (Autoregressive Integrated Moving Average):**
    *   **What it does:** Captures the linear autocorrelation structure in the time series.
    *   **Method:** The engine uses an auto-optimization loop to select the best `(p, d, q)` parameters by minimizing the Akaike Information Criterion (AIC). It models the momentum (AR) and shock persistence (MA) while handling non-stationarity via differencing (I).
*   **Holt-Winters ETS (Exponential Smoothing):**
    *   **What it does:** Specifically targets and projects structural seasonality and trend.
    *   **Method:** We use additive trend and additive seasonality models. For shorter durations, it catches intraday/intra-week cycles; for longer durations, it aligns with monthly/quarterly patterns.
*   **Monte Carlo GBM (Geometric Brownian Motion):**
    *   **What it does:** Provides a probabilistic distribution of future prices by simulating thousands of possible market paths.
    *   **Method:** We run **5,000 simulations** based on the historical drift (mean log-return) and volatility (standard deviation). The output creates a percentile "fan" (P5, P25, P50, P75, P95) mapping the probability landscape of the rate.
*   **The Consensus Ensemble:**
    *   The final forecast applies a weighted average: `35% ARIMA + 35% Holt-Winters + 30% Monte Carlo Median`. The minimum point of this ensemble within your chosen time horizon acts as the recommended transfer window.

### 2. Statistical Analysis & Time-Series Tests
Before predicting, the system analyzes the fundamental structural properties of the market.

*   **Hurst Exponent ($H$):**
    *   Calculated via R/S (Rescaled Range) analysis. 
    *   **$H < 0.5$**: The market is *Mean-Reverting* (prices tend to snap back to an average).
    *   **$H \approx 0.5$**: The market is a *Random Walk* (unpredictable noise).
    *   **$H > 0.5$**: The market is *Trending* (past moves strongly predict future continuation).
*   **Augmented Dickey-Fuller (ADF) Test:**
    *   Tests the time series for a unit root to determine **stationarity**. Stationarity implies statistical properties like mean and variance are constant over time.
*   **Jarque-Bera Test & Distribution Shape:**
    *   Calculates **Skewness** (asymmetry of returns) and **Excess Kurtosis** (fat tails / extreme events). The JB test checks if the return distribution is mathematically normal. FX markets often exhibit "fat tails," meaning extreme moves happen more often than a normal bell curve suggests.
*   **Autocorrelation Function (ACF):**
    *   Measures how correlated today's price is with the price from $N$ days ago.

### 3. Risk Management & Drawdown Metrics
Instead of just looking at potential upside, the engine quantifies downside exposure.

*   **Value at Risk (VaR 95% & 99%):**
    *   Calculated on a daily log-return basis. A 95% VaR of -0.90% means that on 19 out of 20 trading days, the maximum loss will not exceed 0.90%.
*   **Conditional Value at Risk (CVaR / Expected Shortfall):**
    *   Estimates the average expected loss *on the days where the VaR limit is breached*. It measures the "tail risk."
*   **Maximum Drawdown:**
    *   Calculates the largest historic peak-to-trough drop in the exchange rate.
*   **Rolling Annualized Volatility:**
    *   Maps historical standard deviation over 10-day, 20-day, and 30-day windows, multiplied by $\sqrt{252}$ to annualize the risk.

### 4. Technical Indicator Matrix
A suite of 6 independent technical indicators commonly used by proprietary trading desks.

*   **RSI (Relative Strength Index, 14-day & 7-day):** Momentum oscillator bounded between 0 and 100. >70 is historically overbought; <30 is oversold.
*   **MACD (Moving Average Convergence Divergence):** Measures trend direction and momentum shifts using 12/26/9 EMAs.
*   **Bollinger Bands (%B and Bandwidth):** Plots 2 standard deviations away from a 20-day Simple Moving Average. Identifies volatility squeezes and over-extensions.
*   **Stochastic Oscillator (14,3):** Compares the closing price to the price range over a specific period.
*   **Williams %R:** A momentum indicator acting as the inverse of the Fast Stochastic Oscillator.
*   **Z-Score (20-day rolling):** Measures how many standard deviations the current price is away from the 20-day mean. A high absolute Z-score flags extreme mean-reversion setups.
*   **Composite Signal:** The system aggregates these indicators into a unified "Buy", "Hold", or "Wait" recommendation.

### 5. Seasonality & Market Microstructure
*   **Day-of-Week Effect:** Maps the historical average return for each weekday. (e.g., if Mondays historically average a -0.15% return, EUR/USD tends to be cheaper on Mondays).
*   **Monthly Seasonality:** Identifies macroeconomic cyclical trends across the calendar year.
*   **Time-Series Decomposition:** Splits the raw price chart into three additive/multiplicative components: Trend, Seasonal, and Residual (noise).

---

## 🚀 How to Run and Update Locally

The dashboard relies on Python to fetch fresh market data and perform the heavy statistical modeling.

### Prerequisites
Make sure you have Python 3 installed along with the required quant libraries:
```bash
pip install pandas numpy scipy yfinance statsmodels ta
```

### Refreshing the Data
Whenever you want to pull the latest live market data and recompute the forecasts:

```bash
# 1. Run the quant engine (fetches Yahoo Finance data & crunches models)
python3 engine.py

# 2. Inject the newly generated multi_data.json directly into the HTML
python3 build_dashboard.py
```
After running this, `index.html` will contain the newest data. You can then simply push the changes to GitHub to update the live site.

### Updating GitHub Pages
```bash
git add .
git commit -m "Update dashboard data"
git push origin main
```
The live website will automatically update within 60 seconds.

---

## 🛠️ Architecture Stack
*   **Backend Engine:** `Python 3` (yfinance, statsmodels, scipy, pandas, ta). No active server required; pre-computes everything statically.
*   **Frontend UI:** `HTML5`, `Vanilla CSS` (Glassmorphism & institutional dark mode), `Chart.js 4.4`
*   **Deployment:** `GitHub Pages` (100% static, instantly loadable with zero latency).

> **Disclaimer:** This tool is for educational and analytical purposes only. Quantitative models rely on historical precedent which does not guarantee future results. This is not financial advice.
