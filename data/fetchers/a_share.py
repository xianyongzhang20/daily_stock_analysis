"""A股数据获取 - 使用 akshare"""

import time
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from .base import BaseFetcher, QuoteData, HistData


class AShareFetcher(BaseFetcher):
    """A股数据获取器"""

    def __init__(self):
        super().__init__("a_share")
        self._imported = False

    def _ensure_akshare(self):
        if not self._imported:
            import akshare as ak
            self._ak = ak
            self._imported = True

    def fetch_quote(self, code: str) -> Optional[QuoteData]:
        """获取A股实时行情"""
        try:
            self._ensure_akshare()
            df = self._ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if stock.empty:
                return None
            s = stock.iloc[0]
            return QuoteData(
                code=code,
                name=s.get('名称', ''),
                market="a_share",
                price=float(s.get('最新价', 0)),
                change_pct=float(s.get('涨跌幅', 0)),
                open_px=float(s.get('今开', 0)),
                high_px=float(s.get('最高', 0)),
                low_px=float(s.get('最低', 0)),
                pre_close=float(s.get('昨收', 0)),
                volume=float(s.get('成交量', 0)),
                amount=float(s.get('成交额', 0)),
                turnover=float(s.get('换手率', 0)),
                pe_ttm=self._safe_float(s.get('市盈率-动态')),
                pb=self._safe_float(s.get('市净率')),
                market_cap=float(s.get('总市值', 0)),
            )
        except Exception as e:
            print(f"[A股] {code} 行情获取失败: {e}")
            return None

    def fetch_history(self, code: str, days: int = 120) -> Optional[HistData]:
        """获取A股历史K线"""
        try:
            self._ensure_akshare()
            end = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")
            time.sleep(0.5)
            df = self._ak.stock_zh_a_hist(symbol=code, period="daily",
                                          start_date=start, end_date=end, adjust="qfq")
            if df is None or df.empty:
                return None
            # 取最近 days 个交易日
            df = df.tail(days)
            return HistData(
                code=code,
                market="a_share",
                dates=df['日期'].astype(str).tolist(),
                opens=df['开盘'].tolist(),
                closes=df['收盘'].tolist(),
                highs=df['最高'].tolist(),
                lows=df['最低'].tolist(),
                volumes=df['成交量'].tolist(),
                changes=df['涨跌幅'].tolist(),
            )
        except Exception as e:
            print(f"[A股] {code} 历史数据获取失败: {e}")
            return None

    def fetch_board(self, code: str) -> list[str]:
        """获取股票所属板块"""
        try:
            self._ensure_akshare()
            boards = ['航运', '水运', '交通运输', '白酒', '银行', '消费电子', '新能源']
            for bname in boards:
                try:
                    time.sleep(0.5)
                    cons = self._ak.stock_board_industry_cons_em(symbol=bname)
                    if code in cons['代码'].values:
                        return [bname]
                except:
                    pass
        except:
            pass
        return []

    @staticmethod
    def _safe_float(val) -> Optional[float]:
        if val in (None, '-', ''):
            return None
        try:
            return float(val)
        except:
            return None

    def fetch_index(self, code: str) -> Optional[QuoteData]:
        """获取指数行情"""
        return self.fetch_quote(code)
