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
