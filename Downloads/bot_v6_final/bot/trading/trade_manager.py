from __future__ import annotations
import csv, os, time
from pathlib import Path
from bot.config import settings

LOG_CSV = Path(settings.MODEL_PATH.parent)/"trade_logs.csv"
if not LOG_CSV.exists():
    with open(LOG_CSV,"w",newline="") as f:
        writer=csv.writer(f); writer.writerow(["ts","symbol","signal","price","sl","tp","size","conf"])

def execute_trade(symbol, signal, price, sl, tp, size=None, conf=0.0):
    ts = int(time.time()*1000)
    with open(LOG_CSV,"a",newline="") as f:
        writer=csv.writer(f)
        writer.writerow([ts,symbol,signal,price,sl,tp,size,conf])
    return {"ts":ts,"symbol":symbol,"signal":signal,"price":price,"sl":sl,"tp":tp,"size":size,"conf":conf}
