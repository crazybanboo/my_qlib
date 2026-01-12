import pandas as pd
import numpy as np
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.report import analysis_position
import matplotlib.pyplot as plt

def analyze_risk(report_normal):
    """
    风险分析原子
    """
    return risk_analysis(report_normal["return"])

def plot_backtest_analysis(report_normal, show_plot=False, save_path="."):
    """
    持仓分析绘图原子
    """
    # 1. 基础报表图形
    analysis_df = report_normal.copy()
    
    # 绘图：报告图表 (设置 show_notebook=False 以获取 Figure 对象)
    # report_graph 返回 (figure,)
    figs_report = analysis_position.report_graph(analysis_df, show_notebook=False)
    if figs_report:
        for i, fig in enumerate(figs_report):
            html_path = f"{save_path}/report_graph_{i}.html"
            fig.write_html(html_path)
            print(f"已保存报告图表到: {html_path}")
    
    # 2. 风险分析图表
    # 计算风险分析所需数据
    from qlib.contrib.evaluate import risk_analysis as qlib_risk_analysis
    analysis = dict()
    analysis["excess_return_without_cost"] = qlib_risk_analysis(analysis_df["return"] - analysis_df["bench"])
    analysis["excess_return_with_cost"] = qlib_risk_analysis(analysis_df["return"] - analysis_df["bench"] - analysis_df["cost"])
    analysis_results_df = pd.concat(analysis)
    
    # risk_analysis_graph 返回 figure list
    figs_risk = analysis_position.risk_analysis_graph(analysis_results_df, analysis_df, show_notebook=False)
    if figs_risk:
        for i, fig in enumerate(figs_risk):
            html_path = f"{save_path}/risk_analysis_graph_{i}.html"
            fig.write_html(html_path)
            print(f"已保存风险分析图表到: {html_path}")
    
    return figs_report, figs_risk

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
