from qlib.contrib.strategy.signal_strategy import TopkDropoutStrategy

def create_topk_strategy(model, dataset, topk=50, n_drop=5):
    """
    创建 TopK 策略原子。
    这里是用户主要编写和扩展策略的地方。
    """
    strategy_config = {
        "model": model,
        "dataset": dataset,
        "topk": topk,
        "n_drop": n_drop,
    }
    return TopkDropoutStrategy(**strategy_config)

def create_simple_strategy(signal, topk=50, n_drop=5):
    """
    使用外部信号创建策略
    """
    return TopkDropoutStrategy(signal=signal, topk=topk, n_drop=n_drop)
