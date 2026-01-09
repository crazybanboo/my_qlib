from qlib.backtest import backtest_loop
from qlib.backtest.executor import SimulatorExecutor

def create_simulator_executor(time_per_step="day", generate_portfolio_metrics=True):
    """
    创建执行器原子
    """
    return SimulatorExecutor(
        time_per_step=time_per_step, 
        generate_portfolio_metrics=generate_portfolio_metrics
    )

def run_backtest_loop(start_time, end_time, strategy, executor):
    """
    执行回测原子
    """
    return backtest_loop(
        start_time=start_time,
        end_time=end_time,
        trade_strategy=strategy,
        trade_executor=executor
    )
