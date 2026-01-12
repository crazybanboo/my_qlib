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

def format_positions_df(positions):
    """
    将原始持仓数据转换为更易读的 DataFrame。
    支持 Qlib 的 Position 对象以及普通字典结构。
    """
    data = []
    for date, pos_info in positions.items():
        # 1. 提取内部持仓对象/字典
        if isinstance(pos_info, dict):
            inner_pos = pos_info.get('position', pos_info)
        else:
            inner_pos = pos_info
            
        # 2. 根据类型提取信息
        if hasattr(inner_pos, 'get_cash'):
            # 情况 A: inner_pos 是 Qlib 的 Position 对象
            cash = inner_pos.get_cash()
            total_value = inner_pos.calculate_value()
            hold_str = []
            try:
                # 遍历持仓代码
                for code in inner_pos.get_stock_list():
                    amount = inner_pos.get_stock_amount(code)
                    price = inner_pos.get_stock_price(code)
                    stock_value = amount * price
                    # 计算权重
                    weight = stock_value / total_value if total_value != 0 else 0
                    hold_str.append(f"{code}(数量:{amount:,.0f}, 价值:{stock_value:,.2f}, 权重:{weight:.2%})")
            except Exception:
                # 备选方案
                hold_dict = getattr(inner_pos, 'position', {})
                hold_str = [str(code) for code in hold_dict if code not in ['cash', 'cash_delay']]
            holdings_label = " | ".join(hold_str)
        elif isinstance(inner_pos, dict):
            # 情况 B: inner_pos 是普通字典
            cash = inner_pos.get('cash', 0)
            total_value = inner_pos.get('now_account_value', cash)
            holdings = {k: v for k, v in inner_pos.items() if k not in ['cash', 'now_account_value', 'cash_delay']}
            hold_parts = []
            for code, detail in holdings.items():
                if isinstance(detail, dict):
                    amount = detail.get('amount', 0)
                    price = detail.get('price', 0)
                    stock_value = amount * price
                    weight = detail.get('weight', 0)
                    hold_parts.append(f"{code}(数量:{amount:,.0f}, 价值:{stock_value:,.2f}, 权重:{weight:.2%})")
                else:
                    hold_parts.append(str(code))
            holdings_label = " | ".join(hold_parts)
        else:
            cash, total_value, holdings_label = 0, 0, "Unknown"

        data.append({
            'date': date,
            'cash': cash,
            'total_value': total_value,
            'holdings': holdings_label if holdings_label else "Empty"
        })
    
    df = pd.DataFrame(data)
    if not df.empty:
        df.set_index('date', inplace=True)
    return df
