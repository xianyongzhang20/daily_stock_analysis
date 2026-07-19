"""A股数据获取 - 使用 akshare"""

import time
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from .base import BaseFetcher, QuoteData, HistData


class AShareFetcher(BaseFetcher):
    """A股数据获取器 (akshare + yfinance fallback)"""

    def __init__(self):
        super().__init__("a_share")
        self._imported = False
        self._yf_imported = False

    def _ensure_akshare(self):
        if not self._imported:
            import akshare as ak
            self._ak = ak
            self._imported = True

    def _ensure_yfinance(self):
        if not self._yf_imported:
            import yfinance as yf
            self._yf = yf
            self._yf_imported = True

    def _yf_code(self, code: str) -> str:
        """转为 yfinance 的 A 股代码格式"""
        if code.startswith('6'):
            return f"{code}.SS"
        return f"{code}.SZ"

    def _yf_quote(self, code: str) -> Optional[QuoteData]:
        """通过 yfinance 获取 A 股行情"""
        try:
            self._ensure_yfinance()
            ticker = self._yf.Ticker(self._yf_code(code))
            info = ticker.info
            if not info or not info.get('regularMarketPrice'):
                return None
            return QuoteData(
                code=code,
                name=info.get('longName') or info.get('shortName') or code,
                market="a_share",
                price=info.get('regularMarketPrice', 0),
                change_pct=info.get('regularMarketChangePercent', 0),
                open_px=info.get('regularMarketOpen'),
                high_px=info.get('regularMarketDayHigh'),
                low_px=info.get('regularMarketDayLow'),
                pre_close=info.get('regularMarketPreviousClose'),
                volume=info.get('regularMarketVolume'),
                pe_ttm=info.get('trailingPE'),
                pb=info.get('priceToBook'),
                market_cap=info.get('marketCap'),
            )
        except Exception as e:
            print(f"[A股-yf] {code} fallback 失败: {e}")
            return None

    def _yf_history(self, code: str, days: int = 120) -> Optional[HistData]:
        """通过 yfinance 获取 A 股历史"""
        try:
            self._ensure_yfinance()
            ticker = self._yf.Ticker(self._yf_code(code))
            df = ticker.history(period=f"{max(days, 60)}d")
            if df.empty:
                return None
            return HistData(
                code=code,
                market="a_share",
                dates=[d.strftime("%Y-%m-%d") for d in df.index],
                opens=df['Open'].tolist(),
                closes=df['Close'].tolist(),
                highs=df['High'].tolist(),
                lows=df['Low'].tolist(),
                volumes=df['Volume'].tolist(),
                changes=[float(df['Close'].iloc[i] / df['Close'].iloc[i-1] - 1) * 100
                         if i > 0 else 0 for i in range(len(df))],
            )
        except Exception as e:
            print(f"[A股-yf] {code} 历史 fallback 失败: {e}")
            return None

    def fetch_quote(self, code: str) -> Optional[QuoteData]:
        """获取A股实时行情 (akshare -> yfinance fallback)"""
        try:
            self._ensure_akshare()
            df = self._ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if not stock.empty:
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
            print(f"[A股] akshare 失败，fallback 到 yfinance: {e}")
        return self._yf_quote(code)

    def fetch_history(self, code: str, days: int = 120) -> Optional[HistData]:
        """获取A股历史K线 (akshare -> yfinance fallback)"""
        try:
            self._ensure_akshare()
            end = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")
            time.sleep(0.5)
            df = self._ak.stock_zh_a_hist(symbol=code, period="daily",
                                          start_date=start, end_date=end, adjust="qfq")
            if df is not None and not df.empty:
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
            print(f"[A股] akshare 历史失败，fallback 到 yfinance: {e}")
        return self._yf_history(code, days)

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
