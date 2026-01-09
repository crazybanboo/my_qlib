---
name: qlib助手
description: 当需要获取qlib的专有接口进行编程/debug的时候，请提前查阅文档
dependencies: 无
---

关于qlib的接口调用编写/debug，要严格遵照文档来，不要凭空想象。
目前的qlib环境装在了项目根目录的.venv里面。

**核心知识点补充：**
1. **回测接口选择**：优先使用 `qlib.backtest.backtest` 而非底层的 `backtest_loop`。前者会自动完成 `SimulatorExecutor` 的账户（trade_account）和交易环境初始化，避免 "SimulatorExecutor object has no attribute 'trade_account'" 错误。
2. **策略信号格式**：`TopkDropoutStrategy` 等策略需要的 `signal` 必须是 `pd.Series` 或 `pd.DataFrame`，且索引（Index）必须是 `<datetime, instrument>` 的 MultiIndex。
3. **关键文档路径**：
   - 回测配置与执行：参考 `qlib-docs/component/strategy.rst` 中的 "Running backtest" 部分。
   - 数据获取：参考 `qlib-docs/component/data.rst` 了解 `D.features` 和表达式引擎。
4. **环境初始化**：所有操作前必须先执行 `qlib.init()`。在中国 A 股市场下，需配合 `from qlib.config import REG_CN` 使用。

**任务指令：**
当我要求你使用qlib的某些功能时，请使用项目根目录下的qlib-docs文件夹来查阅qlib相关使用文档，然后根据文档来编写代码。
