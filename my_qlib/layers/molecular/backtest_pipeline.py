from ..atomic.env_init import init_qlib_env
from ..atomic.backtest_executor import create_simulator_executor, run_backtest
from ..atomic.report_generator import analyze_risk, calculate_summary_stats, plot_backtest_analysis
from ..atomic.data_handler import get_simple_signal
from ..atomic.strategy_pool import create_simple_strategy, create_permanent_strategy

def standard_backtest_pipeline(
    start_time, 
    end_time, 
    strategy_kwargs, 
    provider_uri="/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data",
    benchmark="SH000300",
    account=100000000,
    exchange_kwargs=None
):
    """
    标准回测流水线分子。
    线性组合：初始化 -> 信号生成 -> 创建策略 -> 创建执行器 -> 运行回测 -> 分析结果
    """
    # 1. 环境初始化
    init_qlib_env(provider_uri=provider_uri)
    
    # 2. 信号生成 (L4 原子)
    signal = get_simple_signal(start_time, end_time)
    
    # 3. 创建策略 (L4 原子)
    strategy = create_simple_strategy(
        signal=signal, 
        topk=strategy_kwargs.get("topk", 50),
        n_drop=strategy_kwargs.get("n_drop", 5)
    )
    
    # 4. 创建执行器
    executor = create_simulator_executor()
    
    # 5. 运行回测
    portfolio_metrics, indicators = run_backtest(
        start_time=start_time,
        end_time=end_time,
        strategy=strategy,
        executor=executor,
        benchmark=benchmark,
        account=account,
        exchange_kwargs=exchange_kwargs
    )
    
    # 4. 结果提取 (假设频率为 1day)
    # 注意：这里为了简化假设了返回结构，实际可能需要根据频率处理
    freq = "1day"
    if freq in portfolio_metrics:
        report_normal, positions_normal = portfolio_metrics[freq]
        
        # 5. 分析指标
        analysis = analyze_risk(report_normal)
        stats = calculate_summary_stats(report_normal["return"])
        
        # 6. 绘图分析 (L4 原子)
        # 获取标的列表 (用于绘制价格图)
        instruments = list(signal.index.get_level_values('instrument').unique()) if not signal.empty else None
        plot_backtest_analysis(
            report_normal, 
            instruments=instruments, 
            start_time=start_time, 
            end_time=end_time
        )
        
        return {
            "report": report_normal,
            "positions": positions_normal,
            "indicators": indicators,
            "analysis": analysis,
            "stats": stats
        }
    
    return None

def permanent_portfolio_pipeline(
    start_time,
    end_time,
    asset_weights,
    rebalance_freq="month",
    min_weight=0.15,
    max_weight=0.35,
    asset_groups=None,
    provider_uri="/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data",
    benchmark="SH000300",
    account=100000000,
    exchange_kwargs=None
):
    """
    永久投资组合回测流水线分子。
    """
    # 1. 环境初始化
    init_qlib_env(provider_uri=provider_uri)

    # 2. 创建策略 (L4 原子) - 固定权重策略不需要预测信号
    strategy = create_permanent_strategy(
        asset_weights=asset_weights, 
        rebalance_freq=rebalance_freq,
        min_weight=min_weight,
        max_weight=max_weight,
        asset_groups=asset_groups
    )

    # 3. 创建执行器
    executor = create_simulator_executor()

    # 4. 运行回测
    portfolio_metrics, indicators = run_backtest(
        start_time=start_time,
        end_time=end_time,
        strategy=strategy,
        executor=executor,
        benchmark=benchmark,
        account=account,
        exchange_kwargs=exchange_kwargs
    )

    # 5. 结果处理
    freq = "1day"
    if freq in portfolio_metrics:
        report_normal, positions_normal = portfolio_metrics[freq]
        analysis = analyze_risk(report_normal)
        stats = calculate_summary_stats(report_normal["return"])
        
        # 6. 绘图分析
        # 获取标的列表 (用于绘制价格图)
        instruments = list(asset_weights.keys())
        plot_backtest_analysis(
            report_normal, 
            instruments=instruments, 
            start_time=start_time, 
            end_time=end_time
        )
        
        return {
            "report": report_normal,
            "positions": positions_normal,
            "indicators": indicators,
            "analysis": analysis,
            "stats": stats
        }
    return None
