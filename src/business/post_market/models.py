# -*- coding: utf-8 -*-
"""
盘后复盘系统数据模型

定义3个核心模块的数据结构：
1. MarketSentiment - 市场情绪
2. PortfolioHealth - 持仓健康
3. ActionableInsight - 明日锦囊
4. PostMarketReview - 复盘报告
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class MarketSentiment:
    """市场情绪数据模型"""
    
    date: str                           # 日期 (YYYY-MM-DD)
    status: str                         # 状态: hot, cold, neutral
    status_cn: str                      # 中文状态: 情绪火热, 情绪冰点, 情绪平淡
    recommendation: str                 # 建议: 大胆操作, 等待机会, 按兵不动
    explanation: str                    # 一句话解释
    
    # 原始数据
    limit_up_count: int                 # 涨停数量
    limit_down_count: int               # 跌停数量
    max_consecutive_limit_up: int       # 最高连板数
    total_turnover: float               # 两市成交额（元）
    
    # 计算指标
    limit_up_ratio: float               # 涨停比例
    turnover_billion: float             # 成交额（亿元）
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MarketSentiment':
        """从字典创建实例"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MarketSentiment':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class PortfolioHealth:
    """持仓健康数据模型"""
    
    code: str                           # 股票代码 (sh.600519)
    name: str                           # 股票名称
    status: str                         # 状态: green, yellow, red
    status_cn: str                      # 中文状态: 健康, 警示, 危险
    recommendation: str                 # 建议
    
    # 价格数据
    current_price: float                # 当前价格
    cost_price: Optional[float]         # 成本价格（用户输入）
    change_rate: float                  # 涨跌幅 (%)
    profit_rate: Optional[float]        # 盈亏比例 (%)
    
    # 技术指标
    ma20: float                         # 20日均线
    ma20_deviation: float               # 20日均线偏离度 (%)
    volume_ratio: float                 # 量比
    
    # 策略信号
    ma_signal: str                      # 均线信号: up, flat, down
    volume_signal: str                  # 成交量信号: normal, shrink, expand
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PortfolioHealth':
        """从字典创建实例"""
        return cls(**data)


@dataclass
class ActionableInsight:
    """明日锦囊数据模型"""
    
    rank: int                           # 排名 (1-3)
    title: str                          # 标题（板块或个股名称）
    reason: str                         # 一句话理由
    
    # 历史表现
    win_rate_30d: float                 # 30天胜率
    win_rate_90d: Optional[float]       # 90天胜率
    avg_return: float                   # 平均收益率
    max_drawdown: float                 # 最大回撤
    
    # 推荐股票
    recommended_stocks: List[str]       # 推荐股票代码列表
    
    # 回测数据
    backtest_trades: int                # 回测交易次数
    backtest_wins: int                  # 回测成功次数
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ActionableInsight':
        """从字典创建实例"""
        return cls(**data)


@dataclass
class PostMarketReview:
    """盘后复盘报告数据模型"""
    
    id: str                                     # 报告ID (YYYY-MM-DD)
    date: str                                   # 报告日期
    market_sentiment: MarketSentiment           # 市场情绪
    portfolio_health: List[PortfolioHealth]     # 持仓健康列表
    actionable_insights: List[ActionableInsight] # 明日锦囊列表
    generated_at: str                           # 生成时间
    status: str                                 # 状态: pending, completed, failed
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date,
            'market_sentiment': self.market_sentiment.to_dict(),
            'portfolio_health': [p.to_dict() for p in self.portfolio_health],
            'actionable_insights': [i.to_dict() for i in self.actionable_insights],
            'generated_at': self.generated_at,
            'status': self.status
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PostMarketReview':
        """从字典创建实例"""
        return cls(
            id=data['id'],
            date=data['date'],
            market_sentiment=MarketSentiment.from_dict(data['market_sentiment']),
            portfolio_health=[PortfolioHealth.from_dict(p) for p in data['portfolio_health']],
            actionable_insights=[ActionableInsight.from_dict(i) for i in data['actionable_insights']],
            generated_at=data['generated_at'],
            status=data['status']
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PostMarketReview':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


# 辅助函数
def create_empty_review(date: str) -> PostMarketReview:
    """创建空的复盘报告"""
    return PostMarketReview(
        id=date,
        date=date,
        market_sentiment=MarketSentiment(
            date=date,
            status='neutral',
            status_cn='情绪平淡',
            recommendation='按兵不动',
            explanation='数据加载中...',
            limit_up_count=0,
            limit_down_count=0,
            max_consecutive_limit_up=0,
            total_turnover=0.0,
            limit_up_ratio=0.0,
            turnover_billion=0.0
        ),
        portfolio_health=[],
        actionable_insights=[],
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        status='pending'
    )
