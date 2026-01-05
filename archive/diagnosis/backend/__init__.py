"""
个股诊断模块

提供股票质量评估、多维度评分、信号灯建议和风险管理功能。
"""

from .models import (
    DiagnosisReport,
    TechnicalScore,
    LiquidityScore,
    MarketScore,
    SignalLight,
    RiskInfo,
    HistoricalPerformance,
    ComparisonReport,
    DiagnosisRecord
)

from .exceptions import (
    StockNotFoundError,
    DataInsufficientError,
    TooManyStocksError,
    DataStaleError
)

from .diagnosis_engine import StockDiagnosisEngine
from .technical_scorer import TechnicalScorer
from .liquidity_scorer import LiquidityScorer
from .market_scorer import MarketEnvironmentScorer
from .risk_calculator import RiskCalculator
from .signal_evaluator import SignalLightEvaluator
from .plain_language_generator import PlainLanguageGenerator

__all__ = [
    'DiagnosisReport',
    'TechnicalScore',
    'LiquidityScore',
    'MarketScore',
    'SignalLight',
    'RiskInfo',
    'HistoricalPerformance',
    'ComparisonReport',
    'DiagnosisRecord',
    'StockNotFoundError',
    'DataInsufficientError',
    'TooManyStocksError',
    'DataStaleError',
    'StockDiagnosisEngine',
    'TechnicalScorer',
    'LiquidityScorer',
    'MarketEnvironmentScorer',
    'RiskCalculator',
    'SignalLightEvaluator',
    'PlainLanguageGenerator',
]
