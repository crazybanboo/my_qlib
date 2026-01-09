from ..atomic.env_init import init_qlib_env
from ..atomic.backtest_executor import create_simulator_executor, run_backtest_loop
from ..atomic.report_generator import analyze_risk, calculate_summary_stats

def standard_backtest_pipeline(
    start_time, 
    end_time, 
    strategy, 
    provider_uri="/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data"
):
    """
    标准回测流水线分子。
    线性组合：初始化 -> 创建执行器 -> 运行回测 -> 分析结果
    """
    # 1. 环境初始化
    init_qlib_env(provider_uri=provider_uri)
    
    # 2. 创建执行器
    executor = create_simulator_executor()
    
    # 3. 运行回测
    portfolio_metrics, indicators = run_backtest_loop(
        start_time=start_time,
        end_time=end_time,
        strategy=strategy,
        executor=executor
    )
    
    # 4. 结果提取 (假设频率为 1day)
    # 注意：这里为了简化假设了返回结构，实际可能需要根据频率处理
    freq = "1day"
    if freq in portfolio_metrics:
        report_normal, positions_normal = portfolio_metrics[freq]
        
        # 5. 分析指标
        analysis = analyze_risk(report_normal)
        stats = calculate_summary_stats(report_normal["return"])
        
        return {
            "report": report_normal,
            "positions": positions_normal,
            "analysis": analysis,
            "stats": stats
        }
    
    return None
