# daily_stock_analysis

> LLM驱动的多市场股票智能分析系统

覆盖 **A股 + 港股 + 美股**，每日自动获取行情数据，通过 LLM 生成深度分析报告，支持飞书推送。

## 快速开始

```bash
pip install -r requirements.txt
```

配置股票列表 → `config/stocks.toml`

运行每日分析：
```bash
python scripts/run_daily.py
```

## 功能

- 📊 三市场行情实时获取
- 📈 技术面分析（均线、MACD、RSI、布林带）
- 🏢 基本面关键指标
- 🤖 LLM 驱动的智能解读与信号提取
- 📨 飞书推送每日简报
- ⏰ 定时自动运行

## 数据源

- A股：akshare
- 港股：yfinance
- 美股：yfinance

## 配置

详见 `config/` 目录下的配置文件。
