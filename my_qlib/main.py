import sys
import os
import pandas as pd

# 将当前目录加入路径，以便 import layers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from layers.atomic.report_generator import format_positions_df
from layers.coordination.commander import run_strategy_commander
from layers.atomic.config_loader import load_yaml_config

def main():
    print("=== Qlib 4层原子架构回测框架 ===")
    
    # 1. 从 YAML 加载基础配置
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    raw_config = load_yaml_config(config_path)
    
    # 2. 准备协调层所需的 config 格式
    backtest_cfg = raw_config.get("backtest", {})
    strategy_cfg = raw_config.get("strategy", {})
    
    config = {
        "start_time": backtest_cfg.get("start_time"),
        "end_time": backtest_cfg.get("end_time"),
        "provider_uri": backtest_cfg.get("provider_uri"),
        "benchmark": backtest_cfg.get("benchmark", "SH000300"),
        "account": backtest_cfg.get("account", 1000000),
        "exchange_kwargs": backtest_cfg.get("exchange_kwargs"),
        "strategy": strategy_cfg
    }

    try:
        results = run_strategy_commander(config)
        if results:
            print("\n回测完成！摘要指标：")
            for k, v in results["stats"].items():
                print(f"{k}: {v:.4f}")

            print("=============== 持仓明细 (Positions) ===============")
            pos_df = format_positions_df(results["positions"])
            # 设置 pandas 打印选项以便更好地显示
            pd.set_option('display.max_rows', None) # 设置最大显示行数为 None (代表无限制，全部打印)
            pd.set_option('display.max_colwidth', None)
            pd.set_option('display.width', None)
            # print(pos_df.tail(20)) # 默认打印最后20行
            print(pos_df) # 默认打印最后20行
            print("===================================================")

    except Exception as e:
        print(f"执行失败: {e}")

if __name__ == "__main__":
    main()
