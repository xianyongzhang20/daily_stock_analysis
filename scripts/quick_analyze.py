#!/usr/bin/env python3
"""Quick A-share analysis via yfinance (fallback when akshare proxy blocks)"""
import sys, math
import yfinance as yf

def ma(data, p):
    if len(data) < p: return None
    return sum(data[-p:]) / p

def calc_rsi(data, p=14):
    if len(data) < p+1: return None
    gains = losses = 0
    for i in range(-p, 0):
        ch = data[i] - data[i-1]
        if ch > 0: gains += ch
        else: losses -= ch
    ag = gains / p; al = losses / p
    if al == 0: return 100.0
    return 100 - 100 / (1 + ag/al)

def bollinger(data, p=20):
    if len(data) < p: return None, None, None
    r = data[-p:]; m = sum(r)/p
    v = sum((x-m)**2 for x in r)/p
    s = math.sqrt(v)
    return round(m+2*s,2), round(m,2), round(m-2*s,2)

code = sys.argv[1] if len(sys.argv) > 1 else "000520"
if code.endswith(".SZ") or code.endswith(".SS"):
    ycode = code
else:
    ycode = code + ".SZ"  # default Shenzhen

t = yf.Ticker(ycode)
info = t.info
hist = t.history(period="6mo")
if hist.empty:
    print("No data"); sys.exit(1)

closes = hist['Close'].tolist()
volumes = hist['Volume'].tolist()

ma5 = ma(closes, 5); ma20 = ma(closes, 20); ma60 = ma(closes, 60)
rsi14 = calc_rsi(closes)
bu, bm, bl = bollinger(closes)

signals = []
if ma5 and ma20:
    signals.append("MA5上穿MA20(多头)" if ma5>ma20 else "MA5在MA20下方(偏空)")
if ma20 and ma60:
    signals.append("MA20上穿MA60(中期多头)" if ma20>ma60 else "MA20在MA60下方(中期偏空)")
if rsi14 is not None:
    if rsi14 > 70: signals.append(f"RSI={rsi14:.1f} 超买")
    elif rsi14 < 30: signals.append(f"RSI={rsi14:.1f} 超卖")
    else: signals.append(f"RSI={rsi14:.1f} 中性")
if bu and closes[-1] > bu: signals.append("触及布林上轨")
if bl and closes[-1] < bl: signals.append("触及布林下轨")
if len(volumes) > 20:
    av = sum(volumes[-20:])/20
    if av > 0 and volumes[-1] > av * 1.5:
        signals.append(f"成交量放大 {volumes[-1]/av:.1f}x")

pct_6m = (closes[-1]/closes[0]-1)*100
pct_5d = (closes[-1]/closes[-6]-1)*100 if len(closes)>=6 else 0
vol_ratio = volumes[-1]/(sum(volumes[-20:])/20) if len(volumes)>20 else 0

print(f"## {info.get('longName',code)} ({code}) — 实时分析")
print(f"数据: yfinance | 时间: 2026-07-19")
print()
print("### 📊 行情")
print(f"价格: ¥{info.get('regularMarketPrice',0):.2f}  |  涨跌: {info.get('regularMarketChangePercent',0):+.2f}%")
print(f"开盘: ¥{info.get('regularMarketOpen',0):.2f}  |  最高: ¥{info.get('regularMarketDayHigh',0):.2f}")
print(f"最低: ¥{info.get('regularMarketDayLow',0):.2f}  |  昨收: ¥{info.get('regularMarketPreviousClose',0):.2f}")
pe = info.get('trailingPE','-')
pb = info.get('priceToBook','-')
cap = info.get('marketCap',0)
print(f"量: {info.get('regularMarketVolume',0):,.0f}")
print(f"PE: {pe}  |  PB: {pb:.2f}" if isinstance(pb,float) else f"PE: {pe}  |  PB: {pb}")
if cap: print(f"市值: ¥{cap/1e8:.2f}亿")
print()
print("### 📈 技术面")
if ma5: print(f"MA5: ¥{ma5:.2f}  |  MA20: ¥{ma20:.2f}  |  MA60: ¥{ma60:.2f}")
if rsi14: print(f"RSI(14): {rsi14:.1f}")
if bu: print(f"布林: {bu}/{bm}/{bl}")
print()
print("**信号:**")
for s in signals:
    print(f"  - {s}")
print()
print("### 📋 近10个交易日")
print(f"{'日期':>8}  {'收盘':>6}  {'涨跌':>7}  {'量(万)':>8}")
for i in range(max(0,len(hist.index)-10), len(hist.index)):
    d = hist.index[i].strftime("%m-%d")
    c = closes[i]
    chg = (closes[i]/closes[i-1]-1)*100 if i>0 else 0
    v = volumes[i]/1e4
    print(f"{d:>8}  ¥{c:>5.2f}  {chg:>+6.2f}%  {v:>8.0f}")
print()
print(f"### 📊 区间统计")
print(f"近半年: {pct_6m:+.1f}%  |  区间高: ¥{max(closes):.2f}  |  区间低: ¥{min(closes):.2f}")
print(f"近5日: {pct_5d:+.2f}%")
print(f"最近量/20日均量: {vol_ratio:.2f}x")
print()
print("---")
print("*基于yfinance数据，非实时行情，仅供参考。*")
