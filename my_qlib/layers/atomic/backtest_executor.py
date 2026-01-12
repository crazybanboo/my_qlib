from qlib.backtest import backtest
from qlib.backtest.executor import SimulatorExecutor

def create_simulator_executor(time_per_step="day", generate_portfolio_metrics=True):
    """
    创建执行器原子
    """
    return SimulatorExecutor(
        time_per_step=time_per_step, 
        generate_portfolio_metrics=generate_portfolio_metrics
    )

def run_backtest(start_time, end_time, strategy, executor, benchmark="SH000300", account=100000000, exchange_kwargs=None):
    """
    执行回测原子 (使用 qlib.backtest.backtest 以确保执行器被正确初始化)
    """
    return backtest(
        start_time=start_time,
        end_time=end_time,
        strategy=strategy,
        executor=executor,
        benchmark=benchmark,
        account=account,
        exchange_kwargs=exchange_kwargs or {}
    )
