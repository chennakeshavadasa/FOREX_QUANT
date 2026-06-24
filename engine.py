#!/usr/bin/env python3
"""
Multi-Currency Quantitative Analysis Engine
=============================================
Supports: EUR/INR, USD/INR (easily extensible)
Forecast durations: 7, 14, 30, 60, 90 days
"""

import json, warnings, sys
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from scipy import stats
from scipy.stats import skew, kurtosis
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller, acf
from statsmodels.tsa.seasonal import seasonal_decompose
import ta

warnings.filterwarnings("ignore")
np.random.seed(42)

PAIRS = {
    "EURINR": {"ticker": "EURINR=X", "base": "EUR", "quote": "INR", "name": "Euro / Indian Rupee",   "flag": "🇪🇺🇮🇳"},
    "USDINR": {"ticker": "INR=X",    "base": "USD", "quote": "INR", "name": "US Dollar / Indian Rupee","flag": "🇺🇸🇮🇳"},
    "GBPINR": {"ticker": "GBPINR=X", "base": "GBP", "quote": "INR", "name": "UK Pound / Indian Rupee", "flag": "🇬🇧🇮🇳"},
    "JPYINR": {"ticker": "JPYINR=X", "base": "JPY", "quote": "INR", "name": "Japanese Yen / Indian Rupee", "flag": "🇯🇵🇮🇳"},
    "CNYINR": {"ticker": "CNYINR=X", "base": "CNY", "quote": "INR", "name": "Chinese Yuan / Indian Rupee", "flag": "🇨🇳🇮🇳"},
    "SGDINR": {"ticker": "SGDINR=X", "base": "SGD", "quote": "INR", "name": "Singapore Dollar / Indian Rupee", "flag": "🇸🇬🇮🇳"},
    "HKDINR": {"ticker": "HKDINR=X", "base": "HKD", "quote": "INR", "name": "Hong Kong Dollar / Indian Rupee", "flag": "🇭🇰🇮🇳"},
}

DURATIONS = {
    7:  {"lookback": 180, "label": "1 Week",   "seasonal_period": 5},
    14: {"lookback": 365, "label": "2 Weeks",  "seasonal_period": 5},
    30: {"lookback": 365, "label": "1 Month",  "seasonal_period": 5},
    60: {"lookback": 730, "label": "2 Months", "seasonal_period": 22},
    90: {"lookback": 730, "label": "3 Months", "seasonal_period": 22},
}
MC_SIMS = 5000

def fetch_data(ticker, lookback):
    end   = datetime.now()
    start = end - timedelta(days=lookback + 60)
    print(f"  [DATA] {ticker} → {start.date()} to {end.date()}")
    
    if ticker == 'CNYINR=X':
        df_inr = yf.download('INR=X', start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True, progress=False)
        df_cny = yf.download('CNY=X', start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True, progress=False)
        df_inr = df_inr.ffill().dropna()
        df_cny = df_cny.ffill().dropna()
        if isinstance(df_inr.columns, pd.MultiIndex):
            df_inr.columns = df_inr.columns.get_level_values(0)
            df_cny.columns = df_cny.columns.get_level_values(0)
        common = df_inr.index.intersection(df_cny.index)
        df_inr = df_inr.loc[common]
        df_cny = df_cny.loc[common]
        df = df_inr[['Close', 'Open', 'High', 'Low']] / df_cny[['Close', 'Open', 'High', 'Low']]
        df['Volume'] = 0
    else:
        df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True, progress=False)
        df = df.ffill().dropna()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    df.index = pd.to_datetime(df.index)
    df = df.tail(lookback)
    print(f"  [DATA] {len(df)} rows, latest close: {df['Close'].iloc[-1]:.4f}")
    return df

def indicators(df):
    c, h, l = df['Close'], df['High'], df['Low']
    df['SMA_5']  = c.rolling(5).mean()
    df['SMA_10'] = c.rolling(10).mean()
    df['SMA_20'] = c.rolling(20).mean()
    df['SMA_50'] = c.rolling(50).mean()
    df['EMA_9']  = c.ewm(span=9,  adjust=False).mean()
    df['EMA_21'] = c.ewm(span=21, adjust=False).mean()

    bb = ta.volatility.BollingerBands(close=c, window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_mid']   = bb.bollinger_mavg()
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_pct']   = bb.bollinger_pband()
    df['BB_width'] = (df['BB_upper']-df['BB_lower'])/df['BB_mid']*100

    df['RSI_14'] = ta.momentum.RSIIndicator(close=c, window=14).rsi()
    df['RSI_7']  = ta.momentum.RSIIndicator(close=c, window=7).rsi()

    macd = ta.trend.MACD(close=c, window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd.macd(); df['MACD_signal'] = macd.macd_signal(); df['MACD_hist'] = macd.macd_diff()

    st = ta.momentum.StochasticOscillator(high=h, low=l, close=c, window=14, smooth_window=3)
    df['Stoch_K'] = st.stoch(); df['Stoch_D'] = st.stoch_signal()

    df['WillR']  = ta.momentum.WilliamsRIndicator(high=h, low=l, close=c, lbp=14).williams_r()
    df['ATR_14'] = ta.volatility.AverageTrueRange(high=h, low=l, close=c, window=14).average_true_range()
    df['CCI_20'] = ta.trend.CCIIndicator(high=h, low=l, close=c, window=20).cci()

    df['Log_Return'] = np.log(c / c.shift(1))
    df['Return_1d']  = c.pct_change(1) * 100
    df['Return_5d']  = c.pct_change(5) * 100
    df['ZScore']     = (c - c.rolling(20).mean()) / c.rolling(20).std()
    df['Vol_10d']    = df['Log_Return'].rolling(10).std() * np.sqrt(252) * 100
    df['Vol_20d']    = df['Log_Return'].rolling(20).std() * np.sqrt(252) * 100
    return df

def hurst(ts, max_lag=100):
    ts = list(ts)
    lags, tau = range(2, min(max_lag, len(ts)//2)), []
    for lag in lags:
        sub = [ts[i:i+lag] for i in range(0, len(ts)-lag, lag)]
        rs = []
        for seg in sub:
            seg = np.array(seg)
            dm  = seg - seg.mean()
            R   = np.max(np.cumsum(dm)) - np.min(np.cumsum(dm))
            S   = seg.std(ddof=1)
            if S > 0: rs.append(R/S)
        if rs: tau.append(np.mean(rs))
    if len(tau) < 2: return 0.5
    la = np.array(list(lags)[:len(tau)])
    return np.polyfit(np.log(la), np.log(tau), 1)[0]

def statistics(df):
    r = df['Log_Return'].dropna()
    c = df['Close']
    adf_s, adf_p, *_ = adfuller(r)
    mu, sig = r.mean(), r.std()
    v95, v99 = np.percentile(r,5), np.percentile(r,1)
    return {
        "mu_daily":        float(mu),
        "sigma_daily":     float(sig),
        "ann_vol_pct":     float(sig*np.sqrt(252)*100),
        "skewness":        float(skew(r)),
        "excess_kurtosis": float(kurtosis(r, fisher=True)),
        "var_95":          float(v95*100),
        "var_99":          float(v99*100),
        "cvar_95":         float(r[r<=v95].mean()*100),
        "cvar_99":         float(r[r<=v99].mean()*100),
        "sharpe_ratio":    float((mu/sig)*np.sqrt(252) if sig>0 else 0),
        "hurst_exp":       float(hurst(c.values.tolist())),
        "adf_stat":        float(adf_s), "adf_p": float(adf_p),
        "jb_stat":         float(stats.jarque_bera(r)[0]),
        "jb_p":            float(stats.jarque_bera(r)[1]),
        "acf_lags":        acf(r, nlags=20, fft=True)[1:11].tolist(),
    }

def sr_levels(df):
    c, h, l = df['Close'], df['High'], df['Low']
    window = max(3, len(df)//10)
    lH, lL, lC = float(h.iloc[-1]), float(l.iloc[-1]), float(c.iloc[-1])
    PP = (lH+lL+lC)/3
    lvls = {
        "pivot":lH,"current":round(lC,4),"pivot_pp":round(PP,4),
        "R1":round(2*PP-lL,4),"R2":round(PP+(lH-lL),4),"R3":round(lH+2*(PP-lL),4),
        "S1":round(2*PP-lH,4),"S2":round(PP-(lH-lL),4),"S3":round(lL-2*(lH-PP),4),
    }
    local_h, local_l = [], []
    for i in range(window, len(c)-window):
        if h.iloc[i] == h.iloc[i-window:i+window+1].max(): local_h.append(float(h.iloc[i]))
        if l.iloc[i] == l.iloc[i-window:i+window+1].min(): local_l.append(float(l.iloc[i]))
    def cluster(lvs, pct=0.003):
        if not lvs: return []
        lvs = sorted(set(lvs)); cl = [[lvs[0]]]
        for lv in lvs[1:]:
            (cl[-1].append(lv) if (lv-cl[-1][-1])/cl[-1][-1]<pct else cl.append([lv]))
        return [round(np.mean(c),4) for c in cl]
    lvls["resistance_zones"] = cluster(local_h)[-6:]
    lvls["support_zones"]    = cluster(local_l)[:6]
    return lvls

def arima_forecast(series, n):
    best_aic, best_order = np.inf, (1,1,1)
    for p in range(0,4):
        for q in range(0,4):
            try:
                m = ARIMA(series, order=(p,1,q)).fit()
                if m.aic < best_aic: best_aic, best_order = m.aic, (p,1,q)
            except: pass
    print(f"  [ARIMA] order={best_order}, AIC={best_aic:.2f}")
    m = ARIMA(series, order=best_order).fit()
    fc = m.get_forecast(steps=n); ci = fc.conf_int(alpha=0.05)
    return {
        "order":   list(best_order), "aic": float(best_aic),
        "forecast":[round(v,4) for v in fc.predicted_mean.values],
        "lower_95":[round(v,4) for v in ci.iloc[:,0].values],
        "upper_95":[round(v,4) for v in ci.iloc[:,1].values],
    }

def hw_forecast(series, n, seasonal_period):
    try:
        m = ExponentialSmoothing(series, trend='add', seasonal='add',
            seasonal_periods=seasonal_period, initialization_method="estimated").fit(optimized=True)
        fc = m.forecast(n); rs = float(m.resid.std()); z = 1.96
        return {
            "forecast": [round(v,4) for v in fc.values],
            "lower_95": [round(v-z*rs,4) for v in fc.values],
            "upper_95": [round(v+z*rs,4) for v in fc.values],
            "alpha":float(m.params.get('smoothing_level',0)),
        }
    except Exception as e:
        print(f"  [HW] fallback: {e}")
        last = float(series.iloc[-1]); rs = float(series.pct_change().std()*last)
        return {"forecast":[round(last,4)]*n,"lower_95":[round(last-2*rs,4)]*n,"upper_95":[round(last+2*rs,4)]*n,"alpha":0.0}

def mc_forecast(series, n, n_sims=MC_SIMS):
    lr = np.log(series/series.shift(1)).dropna()
    mu, sig, S0 = lr.mean(), lr.std(), float(series.iloc[-1])
    sims = np.zeros((n, n_sims))
    for t in range(n):
        prev = S0 if t==0 else sims[t-1]
        sims[t] = prev * np.exp((mu-0.5*sig**2) + sig*np.random.standard_normal(n_sims))
    pcts = np.percentile(sims,[5,25,50,75,95],axis=1)
    prob_below = (sims < S0).mean(axis=1)
    return {
        "S0":round(S0,4),"mu_daily":float(mu),"sigma_daily":float(sig),
        "p5": [round(v,4) for v in pcts[0]],"p25":[round(v,4) for v in pcts[1]],
        "p50":[round(v,4) for v in pcts[2]],"p75":[round(v,4) for v in pcts[3]],
        "p95":[round(v,4) for v in pcts[4]],
        "prob_below_current":[round(float(p),4) for p in prob_below],
        "best_transfer_day_idx":int(np.argmin(pcts[2])),
    }

def seasonality(df):
    df2 = df.copy()
    df2['DOW']   = df2.index.dayofweek
    df2['Month'] = df2.index.month
    df2['R']     = df2['Close'].pct_change()*100
    dow_s   = df2.groupby('DOW')['R'].agg(['mean','std','count']).round(4)
    mon_s   = df2.groupby('Month')['R'].agg(['mean','std','count']).round(4)
    day_names   = ['Monday','Tuesday','Wednesday','Thursday','Friday']
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    dow = {day_names[i]:{"mean_return":float(r['mean']),"std":float(r['std']),"count":int(r['count'])} for i,r in dow_s.iterrows() if i<5}
    mon = {month_names[i-1]:{"mean_return":float(r['mean']),"std":float(r['std']),"count":int(r['count'])} for i,r in mon_s.iterrows()}
    try:
        dc = seasonal_decompose(df['Close'], model='multiplicative', period=5, extrapolate_trend='freq')
        N  = min(90, len(dc.trend))
        return {"dow":dow,"monthly":mon,
                "decomp_trend":   [round(v,4) for v in dc.trend.values[-N:]],
                "decomp_seasonal":[round(v,4) for v in dc.seasonal.values[-N:]],
                "decomp_residual":[round(v,4) for v in dc.resid.values[-N:]]}
    except:
        return {"dow":dow,"monthly":mon,"decomp_trend":[],"decomp_seasonal":[],"decomp_residual":[]}

def signals(df):
    lat = df.iloc[-1]
    def safe(k): return float(lat[k]) if k in lat.index and not np.isnan(lat[k]) else 0.0
    rsi = safe('RSI_14'); macd_h = safe('MACD_hist'); bb = safe('BB_pct')
    z   = safe('ZScore'); sk = safe('Stoch_K'); sd = safe('Stoch_D')
    close = safe('Close'); sma50 = safe('SMA_50')
    sig = {}
    sig['RSI']       = {'signal':'OVERSOLD (BUY)' if rsi<35 else 'Weak BUY' if rsi<45 else 'OVERBOUGHT (SELL)' if rsi>65 else 'Mild SELL' if rsi>55 else 'Neutral','value':round(rsi,2),'strength':'Strong' if rsi<35 or rsi>65 else 'Moderate' if rsi<45 or rsi>55 else 'Weak'}
    sig['MACD']      = {'signal':'Bullish' if macd_h>0 else 'Bearish','value':round(macd_h,4),'strength':'Strong' if abs(macd_h)>0.1 else 'Weak'}
    sig['BB']        = {'signal':'Near Lower (BUY)' if bb<0.1 else 'Near Upper (SELL)' if bb>0.9 else 'Mid Band','value':round(bb,3),'strength':'Strong' if bb<0.1 or bb>0.9 else 'Neutral'}
    sig['ZScore']    = {'signal':'Strong BUY (cheap)' if z<-2 else 'Mild BUY' if z<-1 else 'Strong SELL (exp)' if z>2 else 'Mild SELL' if z>1 else 'Neutral','value':round(z,3),'strength':'Strong' if abs(z)>2 else 'Moderate' if abs(z)>1 else 'Weak'}
    sig['Stochastic']= {'signal':'OVERSOLD (BUY)' if sk<20 and sd<20 else 'OVERBOUGHT (SELL)' if sk>80 and sd>80 else 'Neutral','value':round(sk,2),'strength':'Strong' if (sk<20 and sd<20) or (sk>80 and sd>80) else 'Weak'}
    sig['SMA_Trend'] = {'signal':'Uptrend' if close>sma50 else 'Downtrend','value':round(close-sma50,4),'strength':'Moderate'}
    buy  = sum(1 for s in sig.values() if any(w in s['signal'] for w in ['BUY','Bullish','cheap']))
    sell = sum(1 for s in sig.values() if any(w in s['signal'] for w in ['SELL','Bearish','exp']))
    total = len(sig); score = (buy/total)*100
    sig['composite'] = {'buy_count':buy,'sell_count':sell,'total':total,'score':round(score,1),
        'recommendation':('STRONG BUY NOW' if score>=66 else 'BUY (Favorable)' if score>=50 else 'WAIT - May fall more' if score>=33 else 'HOLD/WAIT - Trending high')}
    return sig

def risk(df, amount=100000):
    c = df['Close']; r = df['Log_Return'].dropna()
    rate = float(c.iloc[-1])
    dd   = ((c - c.cummax()) / c.cummax() * 100)
    r14d = c.pct_change(14).dropna()*100
    return {
        "current_rate":round(rate,4),
        "units_per_lakh":round(amount/rate,2),
        "var_95_1d":round(np.percentile(r,5)*100,4),
        "max_drawdown_pct":round(float(dd.min()),2),
        "best_14d_move_pct":round(float(r14d.max()),2),
        "worst_14d_move_pct":round(float(r14d.min()),2),
        "dca_5d_rate":round(float(c.tail(5).mean()),4),
        "dca_10d_rate":round(float(c.tail(10).mean()),4),
    }

def safe_list(series, digits=4):
    return [round(float(v),digits) if (v is not None and not np.isnan(v) and not np.isinf(v)) else None for v in series]

def run_pair(pair_key, forecast_days):
    pair  = PAIRS[pair_key]
    dur   = DURATIONS[forecast_days]
    print(f"\n{'='*55}")
    print(f"  {pair['flag']} {pair['name']} | Forecast: {dur['label']}")
    print(f"{'='*55}")

    df = fetch_data(pair['ticker'], dur['lookback'])
    df = indicators(df)

    hist_n_map = {7: 30, 14: 60, 30: 90, 60: 180, 90: 250}
    hist_n = min(hist_n_map.get(forecast_days, 120), len(df))
    H = df.tail(hist_n).copy()
    
    # Visual charts strictly match forecast window
    H_chart = df.tail(forecast_days).copy()

    # Forecast dates (business days)
    last = H.index[-1]; fc_dates = []; d = last+timedelta(days=1)
    while len(fc_dates) < forecast_days:
        if d.weekday()<5: fc_dates.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    print("  [STATS] Statistical analysis…")
    st_out = statistics(H)
    print("  [S/R]   Support/Resistance…")
    sr_out = sr_levels(H)
    print("  [ARIMA] ARIMA forecast…")
    ar_out = arima_forecast(H['Close'], forecast_days)
    print("  [HW]    Holt-Winters forecast…")
    hw_out = hw_forecast(H['Close'], forecast_days, dur['seasonal_period'])
    print("  [MC]    Monte Carlo (5000 paths)…")
    mc_out = mc_forecast(H['Close'], forecast_days)
    print("  [SEAS]  Seasonality…")
    se_out = seasonality(H)
    print("  [SIG]   Signals…")
    sg_out = signals(H)
    print("  [RISK]  Risk metrics…")
    rk_out = risk(H)

    # Ensemble
    w = {"arima":0.35,"hw":0.35,"mc":0.30}
    ens = [round(w['arima']*ar_out['forecast'][i]+w['hw']*hw_out['forecast'][i]+w['mc']*mc_out['p50'][i],4) for i in range(forecast_days)]
    best_idx = int(np.argmin(ens))

    history = {
        "dates":   [d.strftime("%Y-%m-%d") for d in H_chart.index],
        "close":   safe_list(H_chart['Close']),   "open":  safe_list(H_chart['Open']),
        "high":    safe_list(H_chart['High']),    "low":   safe_list(H_chart['Low']),
        "sma20":   safe_list(H_chart['SMA_20']),  "sma50": safe_list(H_chart['SMA_50']),
        "ema21":   safe_list(H_chart['EMA_21']),
        "bb_upper":safe_list(H_chart['BB_upper']),"bb_lower":safe_list(H_chart['BB_lower']),
        "bb_mid":  safe_list(H_chart['BB_mid']),  "bb_pct":safe_list(H_chart['BB_pct']),
        "rsi14":   safe_list(H_chart['RSI_14']),  "rsi7":  safe_list(H_chart['RSI_7']),
        "macd":    safe_list(H_chart['MACD']),    "macd_sig":safe_list(H_chart['MACD_signal']),
        "macd_hist":safe_list(H_chart['MACD_hist']),
        "stoch_k": safe_list(H_chart['Stoch_K']), "stoch_d":safe_list(H_chart['Stoch_D']),
        "atr":     safe_list(H_chart['ATR_14']),  "cci":   safe_list(H_chart['CCI_20']),
        "zscore":  safe_list(H_chart['ZScore']),  "willr": safe_list(H_chart['WillR']),
        "vol10":   safe_list(H_chart['Vol_10d']), "vol20": safe_list(H_chart['Vol_20d']),
        "returns": safe_list(H_chart['Return_1d']),
    }

    return {
        "meta": {
            "pair":pair_key,"ticker":pair['ticker'],"name":pair['name'],"flag":pair['flag'],
            "base":pair['base'],"quote":pair['quote'],
            "analysis_date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points":len(df),"current_rate":sr_out['current'],
            "forecast_days":forecast_days,"forecast_label":dur['label'],
        },
        "history":history,"statistics":st_out,"support_resistance":sr_out,
        "arima":ar_out,"holt_winters":hw_out,"monte_carlo":mc_out,
        "seasonality":se_out,"signals":sg_out,"risk":rk_out,
        "forecast":{
            "dates":fc_dates,"arima":ar_out['forecast'],"hw":hw_out['forecast'],
            "mc_p50":mc_out['p50'],"mc_p5":mc_out['p5'],"mc_p95":mc_out['p95'],
            "arima_lower":ar_out['lower_95'],"arima_upper":ar_out['upper_95'],
            "ensemble":ens,
            "best_transfer_day_idx":best_idx,
            "best_transfer_date":fc_dates[best_idx],
            "best_transfer_rate":ens[best_idx],
        }
    }

def main():
    ALL_DURATIONS = [7, 14, 30, 60, 90]
    ALL_PAIRS     = ["EURINR", "USDINR", "GBPINR", "JPYINR", "CNYINR", "SGDINR", "HKDINR"]
    output = {}

    for pair in ALL_PAIRS:
        output[pair] = {}
        for dur in ALL_DURATIONS:
            key = str(dur)
            try:
                output[pair][key] = run_pair(pair, dur)
                print(f"  ✓ {pair}/{dur}d done — best: {output[pair][key]['forecast']['best_transfer_date']} @ {output[pair][key]['forecast']['best_transfer_rate']:.4f}")
            except Exception as e:
                print(f"  ✗ {pair}/{dur}d failed: {e}")
                import traceback; traceback.print_exc()

    out_path = "multi_data.json"
    with open(out_path, "w") as f:
        json.dump(output, f, separators=(',',':'), default=str)
    size = len(json.dumps(output, separators=(',',':')))
    print(f"\n✅ Saved → {out_path} ({size/1024:.1f} KB)")
    return output

if __name__ == "__main__":
    main()
