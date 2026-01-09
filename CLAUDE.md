# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**my_qlib** is a quantitative backtesting framework built on Qlib that implements a 4-layer atomic architecture. The framework separates concerns into distinct layers: atomic components (L4), coordination logic (L3), molecular pipelines (L2), and application entry point (L1).

## Running the Project

```bash
# Activate the virtual environment (Qlib is pre-installed in .venv/)
source .venv/bin/activate

# Run the backtest
python my_qlib/main.py
```

The configuration is driven by `my_qlib/config.yaml`. Modify backtest dates, strategy parameters, and other settings there.

## 4-Layer Architecture

The codebase is organized into `/my_qlib/layers/` with four levels:

### L4 - Atomic Layer (`layers/atomic/`)
Single-purpose, reusable functions. Each file contains focused atomic operations:
- `config_loader.py` - YAML configuration loading
- `data_handler.py` - Data fetching from Qlib (`D.features()`, `D.instruments()`), signal generation
- `env_init.py` - Qlib environment initialization (`qlib.init()`)
- `strategy_pool.py` - Strategy creation (e.g., `TopkDropoutStrategy`)
- `backtest_executor.py` - Executor creation (`SimulatorExecutor`) and backtest execution
- `report_generator.py` - Risk analysis and metric calculation

### L3 - Coordination Layer (`layers/coordination/`)
- `commander.py` - Uses a control flow table pattern to orchestrate execution. Validates config and dispatches to molecular pipelines with conditions and error handling.

### L2 - Molecular Layer (`layers/molecular/`)
- `backtest_pipeline.py` - Composes atomic components into complete workflows (init → signal → strategy → execute → analyze)

### L1 - Application Layer
- `main.py` - Entry point that loads YAML config and invokes the commander

## Qlib Integration Critical Points

**When working with Qlib APIs, always reference the documentation in `qlib-docs/` first.**

Key Qlib patterns used in this codebase:

1. **Use `qlib.backtest.backtest()`** - Not the lower-level `backtest_loop`. The former properly initializes the `SimulatorExecutor` with `trade_account` and trading environment.

2. **Signal format** - Strategy signals must be `pd.Series` or `pd.DataFrame` with a MultiIndex of `<datetime, instrument>`. See `data_handler.py:get_simple_signal()` for the pattern.

3. **Environment initialization** - Always call `qlib.init()` before any Qlib operations. For China A-share market, use `from qlib.config import REG_CN`.

4. **Key documentation paths**:
   - Backtest configuration: `qlib-docs/component/strategy.rst` (search for "Running backtest")
   - Data operations: `qlib-docs/component/data.rst`

## Virtual Environment

Qlib is installed in `.venv/` at the project root. The Python interpreter there has all dependencies.

## Configuration

The `config.yaml` file controls:
- `backtest.start_time` / `end_time` - Backtest period
- `backtest.provider_uri` - Path to Qlib data (default: `.qlib/qlib_data/cn_data`)
- `backtest.benchmark` - Benchmark index (default: SH000300 for CSI 300)
- `backtest.account` - Initial account value
- `strategy.class` - Strategy class name
- `strategy.kwargs.topk` / `n_drop` - Strategy parameters

## Adding New Strategies

1. Define strategy creation logic in `layers/atomic/strategy_pool.py`
2. Update `config.yaml` with new strategy class and kwargs
3. Ensure signal generation in `data_handler.py` produces compatible output

## Control Flow Pattern

The `commander.py` uses a control flow table: a list of step dictionaries with `condition`, `action`, and `on_fail` keys. This pattern allows declarative workflow orchestration with conditional execution and error handling.
