import sys
import os

# 将当前目录加入路径，以便 import layers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from layers.coordination.commander import run_strategy_commander
from layers.atomic.strategy_pool import create_simple_strategy
import pandas as pd

def main():
    # 模拟信号数据 (在实际应用中，这里可能是模型输出的信号)
    # 信号格式通常为 index: [datetime, instrument], columns: [score]
    # 简单起见，这里演示如何注入策略
    
    # 这里的 config 可以通过命令行参数解析 (argparse) 获取
    config = {
        "start_time": "2017-01-01",
        "end_time": "2020-08-01",
        "provider_uri": "~/.qlib/qlib_data/cn_data",
        # 暂时提供一个空信号的占位，实际需要用户传入信号或模型
        "strategy": None 
    }

    print("=== Qlib 4层原子架构回测框架 ===")
    
    # 用户可以在这里选择不同的策略
    # 示例：创建一个 TopK 策略
    # 注意：在没有真实信号的情况下，TopkDropoutStrategy 会报错，这里仅做展示
    # config["strategy"] = create_simple_strategy(signal=pd.Series(...))

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
