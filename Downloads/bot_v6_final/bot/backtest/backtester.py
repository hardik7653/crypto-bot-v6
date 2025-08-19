from __future__ import annotations
import json, time, numpy as np
from pathlib import Path
from bot.config import settings
OUT = Path(settings.MODEL_PATH.parent)/"backtest_reports"
OUT.mkdir(parents=True, exist_ok=True)

def run_simple(df, signals, fee=settings.PROBA_SMOOTH_ALPHA, slippage=settings.ADX_FILTER/10000.0):
    closes = df['close'].values
    eq = 1.0; pos=0; entry_px=0.0; trades=[]
    for i,s in enumerate(signals):
        px = closes[i]
        if pos==0 and s=='BUY':
            entry_px = px*(1+slippage); entry_ts=int(df.index[i].timestamp()*1000); pos=1
        elif pos==1 and (s=='SELL' or i==len(signals)-1):
            exit_px = px*(1-slippage)
            ret = (exit_px-entry_px)/entry_px
            eq *= (1+ret)*(1-fee)
            trades.append({'entry_ts':entry_ts,'exit_ts':int(df.index[i].timestamp()*1000),'entry':entry_px,'exit':exit_px,'pnl':ret})
            pos=0
    if not trades:
        return {'n_trades':0,'final_eq':eq,'trades':trades,'sharpe':0.0,'max_dd':0.0}
    pnl=[t['pnl'] for t in trades]; eqs=[1.0]
    for p in pnl: eqs.append(eqs[-1]*(1+p)*(1-fee))
    rets = np.diff(eqs)/np.array(eqs[:-1])
    sharpe = float(np.mean(rets)/(np.std(rets)+1e-9)*np.sqrt(252))
    peak=eqs[0]; maxdd=0.0
    for e in eqs:
        if e>peak: peak=e
        dd=(peak-e)/peak if peak>0 else 0.0
        if dd>maxdd: maxdd=dd
    report={'n_trades':len(trades),'final_eq':eqs[-1],'sharpe':sharpe,'max_dd':maxdd,'trades':trades}
    OUT.joinpath(f'report_{int(time.time())}.json').write_text(json.dumps(report,indent=2))
    return report
