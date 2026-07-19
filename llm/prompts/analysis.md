# 个股深度分析 Prompt

对以下股票进行多维度深度分析。

## 股票信息
- 代码：{code}
- 名称：{name}
- 市场：{market}

## 行情数据
- 最新价：{price}
- 涨跌幅：{change_pct}%
- 换手率：{turnover}%
- PE(TTM)：{pe}
- PB：{pb}
- 总市值：{market_cap}

## 技术面分析
{technical_analysis}

## 基本面摘要
{fundamental_summary}

## 要求
1. 评估当前估值水平（高估/合理/低估）
2. 技术面处在什么阶段（上升/震荡/下跌）
3. 近期关键催化因素
4. 多市场视角：如果该股也在其他市场上市（如A+H），对比两地价差
5. 风险与机会的权衡
6. 总字数控制在 500 字以内
