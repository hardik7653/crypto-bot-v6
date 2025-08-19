
import joblib, time, numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from bot.config import settings
from bot.data.data_processor import add_indicators, make_supervised
from bot.execution.exchange_connector import ExchangeConnector

MODEL_FILE = 'bot/models/model_v6_quick.joblib'

class MLStrategy:
    def __init__(self, connector=None):
        self.connector = connector or ExchangeConnector()
    def _get_df(self, symbol, timeframe='5m', limit=200):
        ohlcv = self.connector.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        df = add_indicators(df)
        return df
    def train_multi_quick(self, symbols, timeframe='5m'):
        Xs=[]; ys=[]; feats=None
        for s in symbols:
            df = self._get_df(s, timeframe, limit=200)
            X,y,f = make_supervised(df, horizon=settings.TARGET_HORIZON)
            if feats is None: feats = f
            Xs.append(X.reindex(columns=feats))
            ys.append(y)
        Xall = pd.concat(Xs); yall = pd.concat(ys)
        ybin = (yall=='BUY').astype(int)
        if ybin.nunique()<2:
            ybin = ybin.copy()
            ybin.iloc[:max(2,int(0.02*len(ybin)))] = 1
        scaler = StandardScaler(with_mean=False)
        Xv = scaler.fit_transform(Xall[feats].values)
        lr = LogisticRegression(max_iter=400, class_weight='balanced')
        lr.fit(Xv, ybin.values)
        joblib.dump({'scaler':scaler,'model':lr,'features':feats,'threshold':settings.PROBA_THRESHOLD}, MODEL_FILE)
        return MODEL_FILE
    def load_model(self):
        try:
            return joblib.load(MODEL_FILE)
        except:
            return None
    def predict(self, df):
        obj = self.load_model()
        if obj is None:
            return 'HOLD', 0.0
        feats = obj['features']; scaler = obj['scaler']; model = obj['model']; thr = obj.get('threshold', settings.PROBA_THRESHOLD)
        X = df[feats].iloc[[-1]].values
        Xs = scaler.transform(X)
        try:
            proba = float(model.predict_proba(Xs)[:,1][0])
        except:
            proba = 0.0
        vol_q = float(df['volatility'].rank(pct=True).iloc[-1])
        if df['adx'].iloc[-1] < settings.ADX_FILTER or not (settings.VOL_Q_LOW <= vol_q <= settings.VOL_Q_HIGH):
            return 'HOLD', 0.0
        if proba >= thr: return 'BUY', proba
        if (1.0-proba) >= thr: return 'SELL', 1.0-proba
        return 'HOLD', abs(proba-0.5)*2
