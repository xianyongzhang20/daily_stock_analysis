"""数据获取基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
import json


@dataclass
class QuoteData:
    """统一行情数据结构"""
    code: str
    name: str
    market: str                     # a_share / hk_stock / us_stock
    price: float                    # 最新价
    change_pct: float               # 涨跌幅 %
    open_px: Optional[float] = None
    high_px: Optional[float] = None
    low_px: Optional[float] = None
    pre_close: Optional[float] = None
    volume: Optional[float] = None  # 成交量
    amount: Optional[float] = None  # 成交额
    turnover: Optional[float] = None  # 换手率 %
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    market_cap: Optional[float] = None  # 总市值
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


@dataclass
class HistData:
    """历史日线数据"""
    code: str
    market: str
    dates: list[str] = field(default_factory=list)
    opens: list[float] = field(default_factory=list)
    closes: list[float] = field(default_factory=list)
    highs: list[float] = field(default_factory=list)
    lows: list[float] = field(default_factory=list)
    volumes: list[float] = field(default_factory=list)
    changes: list[float] = field(default_factory=list)  # 涨跌幅 %


class BaseFetcher(ABC):
    """数据获取基类"""

    def __init__(self, market: str):
        self.market = market
        self._cache = {}

    @abstractmethod
    def fetch_quote(self, code: str) -> Optional[QuoteData]:
        """获取实时行情"""
        ...

    @abstractmethod
    def fetch_history(self, code: str, days: int = 120) -> Optional[HistData]:
        """获取历史日线"""
        ...

    def fetch_batch_quotes(self, codes: list[str]) -> list[QuoteData]:
        """批量获取行情"""
        results = []
        for code in codes:
            q = self.fetch_quote(code)
            if q:
                results.append(q)
        return results

    def to_json(self, obj) -> str:
        return json.dumps(obj, default=str, ensure_ascii=False, indent=2)
