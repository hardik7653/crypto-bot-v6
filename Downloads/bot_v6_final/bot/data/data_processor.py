
import pandas as pd, numpy as np
from bot.config import settings

def _adx(high, low, close, n=14):
    plus_dm = (high.diff()).clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    tr = np.maximum(high - low, np.maximum((high - close.shift(1)).abs(), (low - close.shift(1)).abs()))
    atr = tr.rolling(n, min_periods=1).mean()
    plus_di = 100 * (plus_dm.rolling(n, min_periods=1).mean() / (atr + 1e-9))
    minus_di = 100 * (minus_dm.rolling(n, min_periods=1).mean() / (atr + 1e-9))
    dx = (100 * (plus_di - minus_di).abs() / ((plus_di + minus_di) + 1e-9)).fillna(0)
    adx = dx.rolling(n, min_periods=1).mean()
    return adx

def add_indicators(df):
    df = df.copy()
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')
    df['returns'] = df['close'].pct_change().fillna(0)
    df['volatility'] = df['returns'].rolling(20).std().fillna(0)
    df['atr'] = (df['high'] - df['low']).rolling(14).mean().fillna(0)
    # simple MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['adx'] = _adx(df['high'], df['low'], df['close'], n=14)
    for L in [1,2,3,5,10]:
        df[f'ret_lag_{L}'] = df['returns'].shift(L).fillna(0)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    return df

def make_supervised(df, horizon=3):
    df = df.copy()
    H = horizon
    df['fwd_ret'] = df['close'].shift(-H)/df['close'] - 1.0
    y = pd.Series('HOLD', index=df.index)
    y[df['fwd_ret']>=0.0018] = 'BUY'
    y[df['fwd_ret']<=-0.0018] = 'SELL'
    df = df.iloc[:-H]; y = y.iloc[:-H]
    features = [c for c in df.columns if c not in ['fwd_ret','timestamp']]
    X = df[features].copy()
    return X, y, features
