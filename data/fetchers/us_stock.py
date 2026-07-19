"""美股数据获取 - 使用 yfinance"""

from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf

from .base import BaseFetcher, QuoteData, HistData


class USStockFetcher(BaseFetcher):
    """美股数据获取器"""

    def __init__(self):
        super().__init__("us_stock")

    def fetch_quote(self, code: str) -> Optional[QuoteData]:
        """获取美股实时行情"""
        try:
            ticker = yf.Ticker(code)
            info = ticker.info
            if not info or not info.get('regularMarketPrice'):
                return None

            return QuoteData(
                code=code,
                name=info.get('longName') or info.get('shortName') or code,
                market="us_stock",
                price=info.get('regularMarketPrice', 0),
                change_pct=info.get('regularMarketChangePercent', 0),
                open_px=info.get('regularMarketOpen'),
                high_px=info.get('regularMarketDayHigh'),
                low_px=info.get('regularMarketDayLow'),
                pre_close=info.get('regularMarketPreviousClose'),
                volume=info.get('regularMarketVolume'),
                amount=info.get('regularMarketVolume') * info.get('regularMarketPrice', 0) if info.get('regularMarketVolume') else None,
                pe_ttm=info.get('trailingPE'),
                pb=info.get('priceToBook'),
                market_cap=info.get('marketCap'),
            )
        except Exception as e:
            print(f"[美股] {code} 行情获取失败: {e}")
            return None

    def fetch_history(self, code: str, days: int = 120) -> Optional[HistData]:
        """获取美股历史日线"""
        try:
            ticker = yf.Ticker(code)
            df = ticker.history(period=f"{days}d")
            if df.empty:
                return None
            return HistData(
                code=code,
                market="us_stock",
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
            print(f"[美股] {code} 历史数据获取失败: {e}")
            return None

    def fetch_index(self, code: str) -> Optional[QuoteData]:
        """获取美股指数行情"""
        return self.fetch_quote(code)
