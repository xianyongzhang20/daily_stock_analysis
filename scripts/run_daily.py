#!/usr/bin/env python3
"""daily_stock_analysis - 每日运行入口"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 确保项目根目录在 path 中
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.fetchers.a_share import AShareFetcher
from data.fetchers.hk_stock import HKStockFetcher
from data.fetchers.us_stock import USStockFetcher
from analyzers.technical import TechnicalAnalyzer
from scheduler.daily import DailyScheduler


def main():
    print(f"\n{'='*50}")
    print(f"  daily_stock_analysis — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")

    scheduler = DailyScheduler()
    stocks = scheduler.load_stocks()

    # === A股 ===
    print("📊 [A股] 获取数据...")
    a_fetcher = AShareFetcher()
    a_data = []
    for code in stocks.get("a_share", {}).get("codes", []):
        q = a_fetcher.fetch_quote(code)
        if q:
            hist = a_fetcher.fetch_history(code, days=60)
            ta = TechnicalAnalyzer()
            tech = ta.analyze(hist) if hist else {}
            a_data.append({
                "quote": q.__dict__,
                "technical": tech,
            })
            print(f"  ✓ {q.name} ({q.code}): ¥{q.price} ({q.change_pct:+.2f}%)")
        else:
            print(f"  ✗ {code}: 获取失败")

    # === 港股 ===
    print("\n📊 [港股] 获取数据...")
    hk_fetcher = HKStockFetcher()
    hk_data = []
    for code in stocks.get("hk_stock", {}).get("codes", []):
        q = hk_fetcher.fetch_quote(code)
        if q:
            hk_data.append({"quote": q.__dict__})
            print(f"  ✓ {q.name} ({q.code}): ${q.price} ({q.change_pct:+.2f}%)")
        else:
            print(f"  ✗ {code}: 获取失败")

    # === 美股 ===
    print("\n📊 [美股] 获取数据...")
    us_fetcher = USStockFetcher()
    us_data = []
    for code in stocks.get("us_stock", {}).get("codes", []):
        q = us_fetcher.fetch_quote(code)
        if q:
            us_data.append({"quote": q.__dict__})
            print(f"  ✓ {q.name} ({q.code}): ${q.price} ({q.change_pct:+.2f}%)")
        else:
            print(f"  ✗ {code}: 获取失败")

    # === 输出报告 ===
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "a_share": a_data,
        "hk_stock": hk_data,
        "us_stock": us_data,
    }

    # 保存 JSON
    output_path = ROOT / "reports" / "output"
    output_path.mkdir(parents=True, exist_ok=True)
    report_file = output_path / f"daily_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✅ 报告已保存: {report_file}")

    # 生成 Markdown 摘要
    print("\n=== 今日概览 ===")
    print(f"A股: {len(a_data)} 只 | 港股: {len(hk_data)} 只 | 美股: {len(us_data)} 只")
    print(f"数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    main()
