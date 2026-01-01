"""
策略模块
"""
from strategy.base import BaseStrategy, TechnicalStrategy, FundamentalStrategy, QuantStrategy
from strategy.volume_shrink_strategy import VolumeShrinkStrategy
from strategy.ma_crossover_strategy import MACrossoverStrategy
from strategy.backtest_engine import BacktestEngine

__all__ = [
    'BaseStrategy',
    'TechnicalStrategy',
    'FundamentalStrategy',
    'QuantStrategy',
    'VolumeShrinkStrategy',
    'MACrossoverStrategy',
    'BacktestEngine',
]
