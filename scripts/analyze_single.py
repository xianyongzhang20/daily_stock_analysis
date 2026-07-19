#!/usr/bin/env python3
"""单只股票分析脚本"""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.fetchers.a_share import AShareFetcher
from data.fetchers.hk_stock import HKStockFetcher
from data.fetchers.us_stock import USStockFetcher
from analyzers.technical import TechnicalAnalyzer

MARKET_MAP = {
    "a_share": AShareFetcher,
    "hk_stock": HKStockFetcher,
    "us_stock": USStockFetcher,
}

def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_single.py <代码> [市场]")
        print("  市场: a_share(默认) / hk_stock / us_stock")
        sys.exit(1)

    code = sys.argv[1]
    market = sys.argv[2] if len(sys.argv) > 2 else "a_share"
    Fetcher = MARKET_MAP.get(market)
    if not Fetcher:
        print(f"不支持的市场: {market}")
        sys.exit(1)

    f = Fetcher()
    q = f.fetch_quote(code)
    if not q:
        print(f"行情获取失败: {code}")
        sys.exit(1)

    d = q.__dict__
    hist = f.fetch_history(code, days=120)
    ta = TechnicalAnalyzer()
    tech = ta.analyze(hist) if hist else {}

    # 输出
    print(f"## {d['name']} ({d['code']}) — 实时分析")
    print(f"时间: {d['timestamp']}")
    print()
    print("### 📊 行情")
    print(f"价格: ¥{d['price']}  |  涨跌: {d['change_pct']:+.2f}%")
    print(f"开盘: ¥{d['open_px']}  |  最高: ¥{d['high_px']}  |  最低: ¥{d['low_px']}  |  昨收: ¥{d['pre_close']}")
    print(f"换手: {d.get('turnover','-')}%")
    if d.get('volume'):
        print(f"量: {d['volume']/1e4:.0f}万手  |  额: ¥{d.get('amount',0)/1e8:.2f}亿")
    print(f"PE(TTM): {d.get('pe_ttm','-')}  |  PB: {d.get('pb','-')}")
    if d.get('market_cap'):
        print(f"市值: ¥{d['market_cap']/1e8:.2f}亿")
    print()
    print("### 📈 技术面")
    print(f"MA5: {tech.get('ma5','-')}  |  MA20: {tech.get('ma20','-')}  |  MA60: {tech.get('ma60','-')}")
    print(f"RSI(14): {tech.get('rsi','-')}")
    print(f"布林: {tech.get('bollinger',{}).get('upper','-')} / {tech.get('bollinger',{}).get('mid','-')} / {tech.get('bollinger',{}).get('lower','-')}")
    print()
    print("**信号:**")
    for s in tech.get('signals', []):
        print(f"  - {s}")

    if hist:
        print()
        print("### 📋 近10个交易日")
        for i in range(max(0, len(hist.dates)-10), len(hist.dates)):
            print(f"  {hist.dates[i]}  开:{hist.opens[i]}  收:{hist.closes[i]}  涨跌:{hist.changes[i]:+.2f}%")

if __name__ == "__main__":
    main()
