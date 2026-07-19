"""LLM 分析引擎"""

from pathlib import Path
from typing import Optional

PROMPTS_DIR = Path(__file__).parent / "prompts"


class LLMAnalyzer:
    """LLM 股票分析引擎"""

    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model = model
        self._prompts = {}

    def _load_prompt(self, name: str) -> str:
        """加载prompt模板"""
        if name not in self._prompts:
            path = PROMPTS_DIR / f"{name}.md"
            if path.exists():
                self._prompts[name] = path.read_text(encoding="utf-8")
            else:
                self._prompts[name] = ""
        return self._prompts[name]

    def _format_prompt(self, name: str, **kwargs) -> str:
        """填充prompt模板"""
        template = self._load_prompt(name)
        return template.format(**kwargs)

    def daily_summary(self, market_data: dict) -> str:
        """生成每日市场总结"""
        prompt = self._format_prompt(
            "daily_summary",
            market_a_share=self._fmt_market(market_data.get("a_share", {})),
            market_hk_stock=self._fmt_market(market_data.get("hk_stock", {})),
            market_us_stock=self._fmt_market(market_data.get("us_stock", {})),
            watchlist=self._fmt_watchlist(market_data.get("watchlist", [])),
        )

        # DEBUG: 返回prompt内容（供开发测试）
        # 正式环境调用外部LLM API
        return self._call_llm(prompt)

    def stock_alert(self, stock_info: dict, signals: list[str]) -> str:
        """生成个股预警"""
        prompt = self._format_prompt(
            "alert",
            code=stock_info.get("code", ""),
            name=stock_info.get("name", ""),
            market=stock_info.get("market", ""),
            price=stock_info.get("price", 0),
            change_pct=stock_info.get("change_pct", 0),
            technical_signals="\n".join(f"- {s}" for s in signals),
            history_summary=self._fmt_history(stock_info.get("history", {})),
        )
        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM（占位，需对接实际接口）

        未来可对接：
        - OpenAI / Claude / DeepSeek API
        - OpenClaw 内置 LLM
        """
        # TODO: 接入真实 LLM
        # 开发阶段返回 prompt 预览
        return f"[LLM分析]\n---\n{prompt[:500]}..."

    def _fmt_market(self, data: dict) -> str:
        rows = []
        indices = data.get("indices", [])
        for idx in indices:
            rows.append(f"  - {idx.get('name', '')} {idx.get('price', '-')} ({idx.get('change_pct', '-')}%)")
        stocks = data.get("stocks_data", [])
        for s in stocks:
            rows.append(f"  - {s.get('name', '')} ({s.get('code', '')}): ¥{s.get('price', '-')} ({s.get('change_pct', '-')}%)")
        return "\n".join(rows) if rows else "  (无数据)"

    def _fmt_watchlist(self, stocks: list) -> str:
        rows = []
        for s in stocks:
            rows.append(f"  - [{s.get('market')}] {s.get('name', '')} ({s.get('code', '')}): ${s.get('price', '-')} ({s.get('change_pct', '-')}%)")
        return "\n".join(rows) if rows else "  (无数据)"

    def _fmt_history(self, hist: dict) -> str:
        closes = hist.get("closes", [])
        if len(closes) >= 2:
            return f"近{len(closes)}日收盘价: {closes[-1]} → ... → {closes[0 if len(closes) > 5 else -1]} (区间涨跌幅约{((closes[-1]/closes[0])-1)*100:.1f}%)"
        return "无历史数据"
