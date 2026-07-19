"""技术面分析模块"""

from typing import Optional
from data.fetchers.base import HistData


class TechnicalAnalyzer:
    """技术面分析"""

    @staticmethod
    def calc_moving_avg(closes: list[float], period: int) -> Optional[float]:
        """计算移动平均线"""
        if len(closes) < period:
            return None
        return sum(closes[-period:]) / period

    @staticmethod
    def calc_ema(closes: list[float], period: int) -> Optional[float]:
        """计算指数移动平均"""
        if len(closes) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period
        for price in closes[period:]:
            ema = (price - ema) * multiplier + ema
        return ema

    @staticmethod
    def calc_rsi(closes: list[float], period: int = 14) -> Optional[float]:
        """计算 RSI"""
        if len(closes) < period + 1:
            return None
        gains, losses = 0, 0
        for i in range(-period, 0):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains += change
            else:
                losses -= change
        avg_gain = gains / period
        avg_loss = losses / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calc_macd(closes: list[float]) -> dict:
        """计算 MACD"""
        ema12 = TechnicalAnalyzer.calc_ema(closes, 12)
        ema26 = TechnicalAnalyzer.calc_ema(closes, 26)
        if ema12 is None or ema26 is None:
            return {"dif": None, "dea": None, "macd": None}
        dif = ema12 - ema26
        return {"dif": round(dif, 4), "dea": None, "macd": None}

    @staticmethod
    def calc_bollinger(closes: list[float], period: int = 20) -> dict:
        """计算布林带"""
        if len(closes) < period:
            return {"mid": None, "upper": None, "lower": None}
        recent = closes[-period:]
        mid = sum(recent) / period
        variance = sum((x - mid) ** 2 for x in recent) / period
        std = variance ** 0.5
        return {
            "mid": round(mid, 2),
            "upper": round(mid + 2 * std, 2),
            "lower": round(mid - 2 * std, 2)
        }

    def analyze(self, hist: HistData) -> dict:
        """全量技术面分析"""
        closes = hist.closes
        latest = closes[-1] if closes else 0

        ma5 = self.calc_moving_avg(closes, 5)
        ma20 = self.calc_moving_avg(closes, 20)
        ma60 = self.calc_moving_avg(closes, 60)
        rsi = self.calc_rsi(closes)
        macd = self.calc_macd(closes)
        boll = self.calc_bollinger(closes)

        signals = []
        # 均线信号
        if ma5 and ma20:
            if ma5 > ma20:
                signals.append("MA5上穿MA20(多头)")
            else:
                signals.append("MA5在MA20下方(偏空)")
        if ma20 and ma60:
            if ma20 > ma60:
                signals.append("MA20上穿MA60(中期多头)")
            else:
                signals.append("MA20在MA60下方(中期偏空)")

        # RSI 信号
        if rsi is not None:
            if rsi > 70:
                signals.append(f"RSI={rsi:.1f} 超买")
            elif rsi < 30:
                signals.append(f"RSI={rsi:.1f} 超卖")
            else:
                signals.append(f"RSI={rsi:.1f} 中性")

        # 布林带信号
        if boll.get("upper") and latest > boll["upper"]:
            signals.append("触及布林上轨")
        elif boll.get("lower") and latest < boll["lower"]:
            signals.append("触及布林下轨")

        # 成交量异常
        if len(hist.volumes) > 20:
            avg_vol = sum(hist.volumes[-20:]) / 20
            last_vol = hist.volumes[-1]
            if avg_vol > 0 and last_vol > avg_vol * 1.5:
                signals.append(f"成交量放大 {last_vol/avg_vol:.1f}x")

        return {
            "latest_price": latest,
            "ma5": round(ma5, 2) if ma5 else None,
            "ma20": round(ma20, 2) if ma20 else None,
            "ma60": round(ma60, 2) if ma60 else None,
            "rsi": round(rsi, 1) if rsi else None,
            "macd": macd,
            "bollinger": boll,
            "signals": signals,
        }
