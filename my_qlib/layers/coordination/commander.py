from ..molecular.backtest_pipeline import standard_backtest_pipeline, permanent_portfolio_pipeline

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
            "action": lambda cfg: print(f"配置验证通过: {cfg.get('start_time')} 到 {cfg.get('end_time')}"),
            "on_fail": Exception("配置缺失关键字段 (start_time, end_time, strategy)")
        },
        # {
        #     "step": "execute_backtest_standard",
        #     "condition": lambda cfg: cfg.get("strategy", {}).get("class") == "TopkDropoutStrategy",
        #     "action": lambda cfg: standard_backtest_pipeline(
        #         start_time=cfg["start_time"],
        #         end_time=cfg["end_time"],
        #         strategy_kwargs=cfg["strategy"]["kwargs"],
        #         provider_uri=cfg.get("provider_uri", "/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data"),
        #         benchmark=cfg.get("benchmark", "SH000300"),
        #         account=cfg.get("account", 100000000),
        #         exchange_kwargs=cfg.get("exchange_kwargs")
        #     )
        # },
        {
            "step": "execute_backtest_permanent",
            "condition": lambda cfg: cfg.get("strategy", {}).get("class") == "PermanentPortfolioStrategy",
            "action": lambda cfg: permanent_portfolio_pipeline(
                start_time=cfg["start_time"],
                end_time=cfg["end_time"],
                asset_weights=cfg["strategy"]["kwargs"]["asset_weights"],
                rebalance_freq=cfg["strategy"]["kwargs"].get("rebalance_freq", "month"),
                provider_uri=cfg.get("provider_uri", "/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data"),
                benchmark=cfg.get("benchmark", "SH000300"),
                account=cfg.get("account", 100000000),
                exchange_kwargs=cfg.get("exchange_kwargs")
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
            # 对于可选的回测步骤，如果条件不满足且没有定义 on_fail，则跳过
            if "on_fail" in task:
                raise task["on_fail"]
            print(f"[Commander] 跳过步骤: {step_name}")

    # 返回最后一次执行的回测结果
    final_res = results.get("execute_backtest_standard") or results.get("execute_backtest_permanent")
    return final_res
