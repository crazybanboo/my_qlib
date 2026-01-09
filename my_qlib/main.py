import sys
import os
import pandas as pd

# 将当前目录加入路径，以便 import layers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from layers.coordination.commander import run_strategy_commander
from layers.atomic.config_loader import load_yaml_config

def main():
    print("=== Qlib 4层原子架构回测框架 ===")
    
    # 1. 从 YAML 加载基础配置
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    raw_config = load_yaml_config(config_path)
    
    # 2. 准备协调层所需的 config 格式
    # 将 yaml 中的分层配置平铺或按需转换
    backtest_cfg = raw_config.get("backtest", {})
    strategy_cfg = raw_config.get("strategy", {})
    
    config = {
        "start_time": backtest_cfg.get("start_time"),
        "end_time": backtest_cfg.get("end_time"),
        "provider_uri": backtest_cfg.get("provider_uri"),
        "benchmark": backtest_cfg.get("benchmark", "SH000300"),
        "account": backtest_cfg.get("account", 100000000),
        # 传递参数而不是对象，由 L3 管道负责创建
        "strategy_kwargs": {
            "topk": strategy_cfg.get("kwargs", {}).get("topk", 50),
            "n_drop": strategy_cfg.get("kwargs", {}).get("n_drop", 5)
        }
    }

    try:
        results = run_strategy_commander(config)
        if results:
            print("\n回测完成！摘要指标：")
            for k, v in results["stats"].items():
                print(f"{k}: {v:.4f}")
    except Exception as e:
        print(f"执行失败: {e}")

if __name__ == "__main__":
    main()
