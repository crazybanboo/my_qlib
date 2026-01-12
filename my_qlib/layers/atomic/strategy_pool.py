from typing import Any, Optional, Dict, List, Union, cast
import copy
import pandas as pd

from qlib.contrib.strategy.signal_strategy import TopkDropoutStrategy, WeightStrategyBase
from qlib.backtest.decision import TradeDecisionWO
from qlib.backtest.position import Position

class PermanentPortfolioStrategy(WeightStrategyBase):
    """
    哈利·布朗永久投资组合策略原子。
    固定权重分配：股票 25%, 长债 25%, 黄金 25%,现金 25%。
    支持月度/年度/每日再平衡。
    """
    def __init__(self, asset_weights: Dict[str, float], rebalance_freq: str = "month", **kwargs: Any):
        """
        :param asset_weights: 资产权重字典，例如 {'SH518880': 0.25, 'SZ159513': 0.125, ...}
        :param rebalance_freq: 再平衡频率，可选 'day', 'month', 'year'
        """
        # 为基类提供默认信号，防止 create_signal_from(None) 报错
        if "signal" not in kwargs:
            kwargs["signal"] = pd.Series(dtype=float)
        super().__init__(**kwargs)
        self.asset_weights = asset_weights
        self.rebalance_freq = rebalance_freq
        self.last_rebalance_date: Optional[pd.Timestamp] = None

    def generate_target_weight_position(
        self, 
        trade_start_time: pd.Timestamp, 
        **kwargs: Any
    ) -> Optional[Dict[str, float]]:
        """
        生成目标权重持仓。
        :param trade_start_time: 当前交易步骤的时间
        :param kwargs: 包含 score, current, trade_end_time 等冗余参数
        """
        # 判断是否需要再平衡
        need_rebalance = False
        if self.rebalance_freq == "day":
            need_rebalance = True
        elif self.rebalance_freq == "month":
            if self.last_rebalance_date is None or trade_start_time.month != self.last_rebalance_date.month:
                need_rebalance = True
        elif self.rebalance_freq == "year":
            if self.last_rebalance_date is None or trade_start_time.year != self.last_rebalance_date.year:
                need_rebalance = True
        
        if need_rebalance:
            self.last_rebalance_date = trade_start_time
            return self.asset_weights
        
        return None # 返回 None 表示本周期不调整权重

    def generate_trade_decision(self, execute_result: Any = None) -> TradeDecisionWO:
        """
        重写交易决策逻辑，绕过对 signal 的强制检查。
        """
        trade_step = self.trade_calendar.get_trade_step()
        trade_start_time, trade_end_time = self.trade_calendar.get_step_time(trade_step)
        
        # 预估信号的时间段（虽然本策略不用，但为了兼容性保留）
        pred_start_time, pred_end_time = self.trade_calendar.get_step_time(trade_step, shift=1)
        
        # 获取当前持仓快照
        # self.trade_position 返回的是 BasePosition，这里显式转换为 Position
        current_temp = cast(Position, copy.deepcopy(self.trade_position))
        
        # 获取目标权重
        target_weight_position = self.generate_target_weight_position(
            trade_start_time=trade_start_time,
            score=None, 
            current=current_temp, 
            trade_end_time=trade_end_time
        )
        
        # 如果 target_weight_position 为 None，则 generate_order_list_from_target_weight_position 会返回空列表
        order_list = self.order_generator.generate_order_list_from_target_weight_position(
            current=current_temp,
            trade_exchange=self.trade_exchange,
            risk_degree=self.get_risk_degree(trade_step),
            target_weight_position=target_weight_position,  # type: ignore
            pred_start_time=pred_start_time,
            pred_end_time=pred_end_time,
            trade_start_time=trade_start_time,
            trade_end_time=trade_end_time,
        )
        return TradeDecisionWO(order_list, self)

def create_topk_strategy(model: Any, dataset: Any, topk: int = 50, n_drop: int = 5) -> TopkDropoutStrategy:
    """
    创建 TopK 策略原子。
    """
    return TopkDropoutStrategy(model=model, dataset=dataset, topk=topk, n_drop=n_drop)

def create_simple_strategy(signal: Any, topk: int = 50, n_drop: int = 5) -> TopkDropoutStrategy:
    """
    使用外部信号创建策略
    """
    return TopkDropoutStrategy(signal=signal, topk=topk, n_drop=n_drop)

def create_permanent_strategy(asset_weights: Dict[str, float], rebalance_freq: str = "month") -> PermanentPortfolioStrategy:
    """
    创建永久投资组合策略原子。
    """
    return PermanentPortfolioStrategy(asset_weights=asset_weights, rebalance_freq=rebalance_freq)
