
def calc_sl_tp(price, atr, side):
    if atr<=0:
        return None, None
    if side=='BUY':
        sl = price - 1.5*atr
        tp = price + 3.0*atr
    else:
        sl = price + 1.5*atr
        tp = price - 3.0*atr
    return sl, tp
