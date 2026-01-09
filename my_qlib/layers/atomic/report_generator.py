import pandas as pd
import numpy as np
from qlib.contrib.evaluate import risk_analysis

def analyze_risk(report_normal):
    """
    风险分析原子
    """
    return risk_analysis(report_normal["return"])

def calculate_summary_stats(returns):
    """
    计算统计指标原子
    """
    stats = {
        "Total Return": (returns + 1).prod() - 1,
        "Annual Return": returns.mean() * 252,
        "Sharpe Ratio": returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0,
        "Max Drawdown": (returns.cumsum().cummax() - returns.cumsum()).max(),
    }
    return stats
