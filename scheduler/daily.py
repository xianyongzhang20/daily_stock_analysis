"""定时任务逻辑：判断是否交易日、执行每日分析"""

from datetime import datetime, time
import tomllib
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class DailyScheduler:
    """每日分析调度器"""

    def __init__(self):
        self.markets_yaml = CONFIG_DIR / "markets.yaml"
        self.stocks_toml = CONFIG_DIR / "stocks.toml"

    def load_stocks(self) -> dict:
        """加载关注的股票列表"""
        with open(self.stocks_toml, "rb") as f:
            data = tomllib.load(f)
        return data

    def is_market_day(self, market: str) -> bool:
        """判断指定市场今天是否交易日（简易版）"""
        today = datetime.now()
        # 周末休市
        if today.weekday() >= 5:
            return False
        # TODO: 接入交易日历API（akshare交易日期查询）
        return True

    def is_trading_hours(self, market: str) -> bool:
        """判断当前是否在交易时段内"""
        from configparser import ConfigParser
        now = datetime.now().time()

        hours = {
            "a_share": (time(9, 30), time(15, 0)),
            "hk_stock": (time(9, 30), time(16, 0)),
            "us_stock": (time(9, 30), time(16, 0)),  # 美东时间，需要换算
        }
        start, end = hours.get(market, (time(0), time(23, 59)))
        return start <= now <= end
