"""基本面分析模块"""

from typing import Optional
import time


class FundamentalAnalyzer:
    """基本面分析"""

    def __init__(self):
        self._ak = None

    def _ensure_akshare(self):
        if self._ak is None:
            import akshare as ak
            self._ak = ak

    def fetch_financial_summary(self, code: str) -> dict:
        """获取A股财务摘要"""
        self._ensure_akshare()
        try:
            time.sleep(0.5)
            yc = self._ak.stock_yjbb_em(date="20240930")
            if yc is not None and not yc.empty:
                stk = yc[yc['股票代码'] == code]
                if not stk.empty:
                    r = stk.iloc[0]
                    return {
                        "revenue": r.get('营业收入-营业收入', '-'),
                        "revenue_yoy": r.get('营业收入-同比增长', '-'),
                        "net_profit": r.get('净利润-净利润', '-'),
                        "net_profit_yoy": r.get('净利润-同比增长', '-'),
                    }
        except Exception as e:
            print(f"[基本面] {code} 财报数据获取失败: {e}")
        return {}

    def fetch_dividend(self, code: str) -> list:
        """获取A股分红记录"""
        self._ensure_akshare()
        try:
            time.sleep(0.5)
            df = self._ak.stock_dividents_cninfo(symbol=code)
            if df is not None and not df.empty:
                return df.head(5).to_dict('records')
        except:
            pass
        return []

    def analyze(self, code: str, market: str) -> dict:
        """基本面分析入口"""
        result = {"market": market, "code": code}

        if market == "a_share":
            result["financials"] = self.fetch_financial_summary(code)
            result["dividend"] = self.fetch_dividend(code)

        return result
