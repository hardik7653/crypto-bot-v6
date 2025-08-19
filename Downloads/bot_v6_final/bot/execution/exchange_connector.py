
import time, random
class MockExchange:
    def __init__(self, symbols=None):
        self.symbols = symbols or ['BTC/USDT']
    def fetch_ohlcv(self, symbol, timeframe='5m', limit=200):
        now = int(time.time()*1000)
        step = 300
        data=[]
        price = 60000.0 if 'BTC' in symbol else 2000.0 if 'ETH' in symbol else 100.0
        for i in range(limit):
            ts = now - (limit-i)*step*1000
            drift = random.uniform(-price*0.002, price*0.002)
            o = price; c = o + drift
            h = max(o,c) + abs(random.uniform(0, price*0.001))
            l = min(o,c) - abs(random.uniform(0, price*0.001))
            v = random.uniform(1,100)
            data.append([ts,o,h,l,c,v])
            price = c
        return data

class ExchangeConnector:
    def __init__(self, exchange_name='mock', use_testnet=True):
        self.ex = MockExchange()
    def fetch_ohlcv(self, symbol, timeframe='5m', limit=200):
        return self.ex.fetch_ohlcv(symbol, timeframe, limit)
