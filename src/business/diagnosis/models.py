# -*- coding: utf-8 -*-
"""
股票综合诊断系统数据模型

定义诊断报告的核心数据结构：
1. DimensionAnalysis - 单个维度的分析结果
2. DiagnosisReport - 完整的综合诊断报告
"""
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
import json


@dataclass
class DimensionAnalysis:
    """单个维度的分析结果"""
    
    score: int                          # 评分 (0-100)
    status: str                         # 状态: green, yellow, red
    message: str                        # 人话描述
    details: Dict                       # 详细数据
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DimensionAnalysis':
        """从字典创建实例"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DimensionAnalysis':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class DiagnosisReport:
    """完整的综合诊断报告"""
    
    code: str                           # 股票代码
    name: str                           # 股票名称
    overall_score: int                  # 综合评分 (0-100)
    overall_rating: str                 # 综合评级: 优秀/良好/一般/较差/很差
    overall_status: str                 # 综合状态: green/yellow/red
    
    # 五个维度的分析结果
    dimensions: Dict[str, DimensionAnalysis] = field(default_factory=dict)
    
    # 综合判断
    strengths: List[str] = field(default_factory=list)      # 优势列表
    weaknesses: List[str] = field(default_factory=list)     # 劣势列表
    suggestions: List[str] = field(default_factory=list)    # 投资建议列表
    summary: str = ""                                        # 综合总结
    
    updated_at: str = ""                # 更新时间
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = asdict(self)
        # 转换 dimensions 中的 DimensionAnalysis 对象
        result['dimensions'] = {
            key: value.to_dict() if isinstance(value, DimensionAnalysis) else value
            for key, value in self.dimensions.items()
        }
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DiagnosisReport':
        """从字典创建实例"""
        # 转换 dimensions 字典中的数据为 DimensionAnalysis 对象
        dimensions = {}
        if 'dimensions' in data:
            dimensions = {
                key: DimensionAnalysis.from_dict(value) if isinstance(value, dict) else value
                for key, value in data['dimensions'].items()
            }
        
        return cls(
            code=data['code'],
            name=data['name'],
            overall_score=data['overall_score'],
            overall_rating=data['overall_rating'],
            overall_status=data['overall_status'],
            dimensions=dimensions,
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            suggestions=data.get('suggestions', []),
            summary=data.get('summary', ''),
            updated_at=data.get('updated_at', '')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DiagnosisReport':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))
    
    def add_dimension(self, dimension_name: str, analysis: DimensionAnalysis) -> None:
        """添加维度分析结果"""
        self.dimensions[dimension_name] = analysis
    
    def get_dimension(self, dimension_name: str) -> Optional[DimensionAnalysis]:
        """获取指定维度的分析结果"""
        return self.dimensions.get(dimension_name)
    
    def has_dimension(self, dimension_name: str) -> bool:
        """检查是否包含指定维度"""
        return dimension_name in self.dimensions
    
    def get_available_dimensions(self) -> List[str]:
        """获取所有可用维度的名称列表"""
        return list(self.dimensions.keys())


# 辅助函数
def create_empty_diagnosis(code: str, name: str) -> DiagnosisReport:
    """创建空的诊断报告"""
    from datetime import datetime
    
    return DiagnosisReport(
        code=code,
        name=name,
        overall_score=0,
        overall_rating='未知',
        overall_status='yellow',
        dimensions={},
        strengths=[],
        weaknesses=[],
        suggestions=[],
        summary='诊断数据加载中...',
        updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


def calculate_overall_score(dimensions: Dict[str, DimensionAnalysis], 
                           weights: Optional[Dict[str, float]] = None) -> int:
    """
    计算综合评分
    
    Args:
        dimensions: 各维度分析结果
        weights: 各维度权重，默认为 {
            'technical': 0.20,
            'fundamental': 0.30,
            'sector': 0.15,
            'capital': 0.20,
            'market_comparison': 0.15
        }
    
    Returns:
        综合评分 (0-100)
    """
    if not dimensions:
        return 0
    
    # 默认权重
    if weights is None:
        weights = {
            'technical': 0.20,
            'fundamental': 0.30,
            'sector': 0.15,
            'capital': 0.20,
            'market_comparison': 0.15
        }
    
    # 计算可用维度的总权重
    available_weight = sum(weights.get(dim, 0) for dim in dimensions.keys())
    
    if available_weight == 0:
        return 0
    
    # 计算加权平均分
    weighted_sum = sum(
        dimensions[dim].score * weights.get(dim, 0)
        for dim in dimensions.keys()
    )
    
    # 归一化到 0-100
    overall_score = int(weighted_sum / available_weight)
    
    return max(0, min(100, overall_score))


def get_rating_from_score(score: int) -> str:
    """
    根据评分获取评级
    
    Args:
        score: 评分 (0-100)
    
    Returns:
        评级: 优秀/良好/一般/较差/很差
    """
    if score >= 80:
        return '优秀'
    elif score >= 65:
        return '良好'
    elif score >= 50:
        return '一般'
    elif score >= 35:
        return '较差'
    else:
        return '很差'


def get_status_from_score(score: int) -> str:
    """
    根据评分获取状态
    
    Args:
        score: 评分 (0-100)
    
    Returns:
        状态: green/yellow/red
    """
    if score >= 70:
        return 'green'
    elif score >= 50:
        return 'yellow'
    else:
        return 'red'
