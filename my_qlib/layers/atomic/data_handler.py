from qlib.data import D

def get_instruments(market: str = "csi300"):
    """
    获取股票池
    """
    return D.instruments(market=market)

def get_benchmark(benchmark: str = "SH000300"):
    """
    获取基准
    """
    return benchmark

def get_simple_signal(start_time, end_time, market="csi300"):
    """
    生成一个简单的信号原子。
    这里我们直接用 $close 的每日变化率作为信号（仅作演示）。
    """
    instruments = D.instruments(market=market)
    # 获取收盘价
    df = D.features(instruments, ["$close"], start_time=start_time, end_time=end_time)
    if df.empty:
        import pandas as pd
        return pd.Series(dtype=float)
        
    # 计算简单的每日收益率作为信号
    # 注意：Qlib 的策略通常需要一个 Series，其索引为 <datetime, instrument>
    # 我们这里简单地将 $close 的变化作为分值
    df['score'] = df['$close'].groupby(level='instrument').pct_change()
    return df['score'].fillna(0)
