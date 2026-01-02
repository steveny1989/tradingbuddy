"""
诊断模块的数据模型定义
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


@dataclass
class TechnicalScore:
    """技术面评分"""
    value: float  # 评分值 (0-100)
    reasons: List[str]  # 评分理由
    indicators: Dict[str, float]  # 关键指标
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiquidityScore:
    """流动性评分"""
    value: float  # 评分值 (0-100)
    reasons: List[str]  # 评分理由
    indicators: Dict[str, float]  # 关键指标
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MarketScore:
    """市场环境评分"""
    value: float  # 评分值 (0-100)
    reasons: List[str]  # 评分理由
    indicators: Dict[str, Any]  # 关键指标
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SignalLight:
    """信号灯"""
    color: str  # RED/YELLOW/GREEN
    label: str  # 建议标签（如"可以关注"）
    reason: str  # 信号理由
    confidence: float  # 信号强度 (0-100)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RiskInfo:
    """风险信息"""
    current_price: float  # 当前价格
    stop_loss_price: float  # 止损价位
    take_profit_price: float  # 止盈价位
    stop_loss_pct: float  # 止损百分比
    take_profit_pct: float  # 止盈百分比
    risk_reward_ratio: float  # 盈亏比
    volatility: float  # 波动率
    risk_level: str  # 风险等级 (LOW/MEDIUM/HIGH/EXTREME)
    
    # 风险因素
    is_st_stock: bool  # 是否 ST 股
    consecutive_losses: int  # 连续亏损年数
    has_major_litigation: bool  # 是否有重大诉讼
    warnings: List[str] = field(default_factory=list)  # 风险警告列表
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HistoricalPerformance:
    """历史表现"""
    diagnosis_date: str  # 诊断日期
    diagnosis_price: float  # 诊断时价格
    days_3_return: Optional[float] = None  # 3 天收益率
    days_5_return: Optional[float] = None  # 5 天收益率
    days_10_return: Optional[float] = None  # 10 天收益率
    excess_return: Optional[float] = None  # 相对大盘超额收益
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosisReport:
    """诊断报告"""
    code: str  # 股票代码
    name: str  # 股票名称
    current_price: float  # 当前价格
    change_pct: float  # 涨跌幅
    
    # 评分
    overall_score: float  # 综合评分 (0-100)
    technical_score: TechnicalScore  # 技术面评分
    liquidity_score: LiquidityScore  # 流动性评分
    market_score: MarketScore  # 市场环境评分
    
    # 信号灯
    signal_light: SignalLight  # 红绿灯建议
    
    # 诊断意见
    diagnosis_text: str  # 大白话诊断
    
    # 风险管理
    risk_info: RiskInfo  # 风险信息
    
    # 历史表现
    historical_performance: Optional[HistoricalPerformance] = None
    
    # 元数据
    timestamp: datetime = field(default_factory=datetime.now)  # 诊断时间
    data_update_time: Optional[datetime] = None  # 数据更新时间
    disclaimer: str = "本诊断仅供参考，不构成投资建议。投资者据此操作，风险自担。"
    
    # 数据来源
    data_source: str = "同花顺 API"
    data_coverage: str = "最近 90 天 K 线数据"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于 JSON 序列化"""
        result = {
            'code': self.code,
            'name': self.name,
            'current_price': self.current_price,
            'change_pct': self.change_pct,
            'overall_score': self.overall_score,
            'technical_score': self.technical_score.to_dict(),
            'liquidity_score': self.liquidity_score.to_dict(),
            'market_score': self.market_score.to_dict(),
            'signal_light': self.signal_light.to_dict(),
            'diagnosis_text': self.diagnosis_text,
            'risk_info': self.risk_info.to_dict(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'data_update_time': self.data_update_time.isoformat() if self.data_update_time else None,
            'disclaimer': self.disclaimer,
            'data_source': self.data_source,
            'data_coverage': self.data_coverage,
        }
        
        if self.historical_performance:
            result['historical_performance'] = self.historical_performance.to_dict()
        
        return result
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class ComparisonReport:
    """对比报告"""
    stocks: List[Dict[str, Any]]  # 股票列表（简化版诊断信息）
    recommendation: str  # 优先级建议
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'stocks': self.stocks,
            'recommendation': self.recommendation,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class DiagnosisRecord:
    """诊断历史记录"""
    id: str  # 诊断 ID
    code: str  # 股票代码
    name: str  # 股票名称
    diagnosis_time: datetime  # 诊断时间
    diagnosis_price: float  # 诊断时价格
    current_price: Optional[float] = None  # 当前价格
    change_pct: Optional[float] = None  # 涨跌幅
    overall_score: float = 0.0  # 综合评分
    signal_light: Optional[Dict[str, Any]] = None  # 信号灯
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'diagnosis_time': self.diagnosis_time.isoformat() if self.diagnosis_time else None,
            'diagnosis_price': self.diagnosis_price,
            'current_price': self.current_price,
            'change_pct': self.change_pct,
            'overall_score': self.overall_score,
            'signal_light': self.signal_light,
        }
