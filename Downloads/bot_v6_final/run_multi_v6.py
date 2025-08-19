
import json
from pathlib import Path
from bot.execution.exchange_connector import ExchangeConnector
from bot.strategies.ml_strategy import MLStrategy
from bot.config import settings
from bot.strategies.risk_manager import calc_sl_tp
BASE = Path(__file__).resolve().parent
cfg = json.load(open(BASE/'config.json'))
symbols = cfg.get('symbols', ['BTC/USDT'])
conn = ExchangeConnector()
ml = MLStrategy(conn)
print("Training quick multi-model on symbols:", symbols)
ml.train_multi_quick(symbols, timeframe=cfg.get('timeframe','5m'))
print("Training done. Evaluating each symbol...")
reports = {}
for s in symbols:
    df = ml._get_df(s, timeframe=cfg.get('timeframe','5m'), limit=200)
    sig, conf = ml.predict(df)
    latest = df.iloc[-1]
    price = float(latest['close']); atr = float(latest['atr'])
    sl,tp = calc_sl_tp(price, atr, 'BUY' if sig=='BUY' else 'SELL')
    reports[s] = {'signal':sig,'conf':conf,'price':price,'atr':atr,'sl':sl,'tp':tp}
print(json.dumps(reports, indent=2))
Path('v6_multi_report.json').write_text(json.dumps(reports, indent=2))
