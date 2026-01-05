#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略模块
包含各种选股策略的实现
"""

from .base import BaseStrategy, TechnicalStrategy, FundamentalStrategy, QuantStrategy
from .ma_crossover import MACrossoverStrategy
from .volume_shrink import VolumeShrinkStrategy

__all__ = [
    'BaseStrategy',
    'TechnicalStrategy',
    'FundamentalStrategy',
    'QuantStrategy',
    'MACrossoverStrategy',
    'VolumeShrinkStrategy',
]
