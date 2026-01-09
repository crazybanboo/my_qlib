from ..molecular.backtest_pipeline import standard_backtest_pipeline

def run_strategy_commander(config):
    """
    策略指挥官 (L2 协调层)
    使用控制流表逻辑编排任务。
    """
    
    # 1. 定义控制流表 (逻辑配置)
    flow_table = [
        {
            "step": "validate_config",
            "condition": lambda cfg: "start_time" in cfg and "end_time" in cfg and "strategy" in cfg,
            "action": lambda cfg: print(f"配置验证通过: {cfg['start_time']} 到 {cfg['end_time']}"),
            "on_fail": Exception("配置缺失关键字段 (start_time, end_time, strategy)")
        },
        {
            "step": "execute_backtest",
            "condition": lambda cfg: True, # 无条件执行
            "action": lambda cfg: standard_backtest_pipeline(
                start_time=cfg["start_time"],
                end_time=cfg["end_time"],
                strategy=cfg["strategy"],
                provider_uri=cfg.get("provider_uri", "/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data")
            )
        }
    ]

    # 2. 扁平化调度执行
    results = {}
    for task in flow_table:
        step_name = task["step"]
        if task["condition"](config):
            print(f"[Commander] 正在执行步骤: {step_name}")
            res = task["action"](config)
            if res:
                results[step_name] = res
        else:
            if "on_fail" in task:
                raise task["on_fail"]
            print(f"[Commander] 跳过步骤: {step_name}")

    return results.get("execute_backtest")
