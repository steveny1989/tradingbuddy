# -*- coding: utf-8 -*-
"""
股票评分引擎
Stock Scoring Engine

计算选股信号的置信度分数（0-100），综合考虑多个因子：
- 成交量因子（30%）
- 均线角度因子（25%）
- 大盘环境因子（20%）
- 流动性因子（15%）
- 基本面因子（10%）
"""
import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class StockScoringEngine:
    """股票评分引擎"""
    
    # 因子权重配置
    WEIGHTS = {
        'volume': 0.30,      # 成交量因子权重 30%
        'ma_angle': 0.25,    # 均线角度因子权重 25%
        'market_env': 0.20,  # 大盘环境因子权重 20%
        'liquidity': 0.15,   # 流动性因子权重 15%
        'fundamental': 0.10  # 基本面因子权重 10%
    }
    
    def __init__(self, db=None):
        """
        初始化评分引擎
        
        Args:
            db: StockDatabase 实例（用于获取大盘数据）
        """
        self.db = db
    
    def calculate_score(
        self,
        signal: Dict,
        technical_factors: Dict,
        fundamental_factors: Optional[Dict] = None
    ) -> float:
        """
        计算置信度分数（0-100）
        
        Args:
            signal: 原始信号字典
            technical_factors: 技术面因子字典
                {
                    'volume_ratio': float,  # 成交量放大倍数
                    'ma_distance': float,   # 均线距离
                    'avg_turnover': float,  # 日均成交额
                    'date': str            # 信号日期
                }
            fundamental_factors: 基本面因子字典（可选）
                {
                    'roe': float,           # 净资产收益率
                    'debt_ratio': float,    # 资产负债率
                    'net_profit': float     # 净利润
                }
        
        Returns:
            置信度分数（0-100）
        """
        try:
            # 计算各因子分数
            volume_score = self._calculate_volume_score(technical_factors.get('volume_ratio', 1.0))
            ma_angle_score = self._calculate_ma_angle_score(technical_factors.get('ma_distance', 0.0))
            market_env_score = self._calculate_market_env_score(technical_factors.get('date'))
            liquidity_score = self._calculate_liquidity_score(technical_factors.get('avg_turnover', 0.0))
            
            # 计算基本面分数
            if fundamental_factors:
                fundamental_score = self._calculate_fundamental_score(fundamental_factors)
            else:
                # 如果没有基本面数据，使用中性分数 50
                fundamental_score = 50.0
            
            # 加权计算总分
            total_score = (
                volume_score * self.WEIGHTS['volume'] +
                ma_angle_score * self.WEIGHTS['ma_angle'] +
                market_env_score * self.WEIGHTS['market_env'] +
                liquidity_score * self.WEIGHTS['liquidity'] +
                fundamental_score * self.WEIGHTS['fundamental']
            )
            
            # 确保分数在 0-100 范围内
            total_score = max(0.0, min(100.0, total_score))
            
            logger.debug(
                f"评分详情: 成交量={volume_score:.1f}, 均线角度={ma_angle_score:.1f}, "
                f"大盘环境={market_env_score:.1f}, 流动性={liquidity_score:.1f}, "
                f"基本面={fundamental_score:.1f}, 总分={total_score:.1f}"
            )
            
            return round(total_score, 2)
            
        except Exception as e:
            logger.error(f"计算评分失败: {e}")
            return 50.0  # 返回中性分数
    
    def _calculate_volume_score(self, volume_ratio: float) -> float:
        """
        计算成交量因子分数
        
        成交量放大倍数越大，分数越高
        - volume_ratio = 1.0 → 50分（无放大）
        - volume_ratio = 2.0 → 100分（放大2倍）
        - volume_ratio > 2.0 → 100分（封顶）
        
        Args:
            volume_ratio: 成交量放大倍数
        
        Returns:
            分数（0-100）
        """
        if volume_ratio <= 0:
            return 0.0
        
        # 线性映射：1.0 -> 50, 2.0 -> 100
        score = (volume_ratio - 1.0) * 50.0 + 50.0
        
        return max(0.0, min(100.0, score))
    
    def _calculate_ma_angle_score(self, ma_distance: float) -> float:
        """
        计算均线角度因子分数
        
        均线距离（ma_distance）反映金叉的强度
        - ma_distance = 0.0 → 50分（刚好金叉）
        - ma_distance = 0.01 (1%) → 75分
        - ma_distance = 0.02 (2%) → 100分
        - ma_distance > 0.02 → 100分（封顶）
        
        Args:
            ma_distance: 均线距离（短期均线 - 长期均线）/ 长期均线
        
        Returns:
            分数（0-100）
        """
        # 取绝对值，因为我们关心的是距离大小
        abs_distance = abs(ma_distance)
        
        # 线性映射：0.0 -> 50, 0.02 -> 100
        score = abs_distance * 2500.0 + 50.0
        
        return max(0.0, min(100.0, score))
    
    def _calculate_market_env_score(self, date: Optional[str] = None) -> float:
        """
        计算大盘环境因子分数
        
        根据大盘当日涨跌幅判断市场环境
        - 大盘上涨 → 分数提升
        - 大盘下跌 → 分数降低
        - 无法获取大盘数据 → 返回中性分数 50
        
        Args:
            date: 信号日期
        
        Returns:
            分数（0-100）
        """
        if not self.db or not date:
            return 50.0  # 无法获取数据，返回中性分数
        
        try:
            # 获取上证指数当日数据
            index_code = 'sh.000001'
            df = self.db.get_daily_data(index_code, start_date=date, end_date=date)
            
            if df.empty:
                return 50.0
            
            # 获取大盘涨跌幅
            index_pct_chg = df.iloc[0].get('pct_chg', 0.0)
            
            # 映射：-3% -> 20, 0% -> 50, +3% -> 80
            # 使用线性映射，每1%涨跌影响10分
            score = 50.0 + (index_pct_chg * 10.0)
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.debug(f"获取大盘数据失败: {e}")
            return 50.0
    
    def _calculate_liquidity_score(self, avg_turnover: float) -> float:
        """
        计算流动性因子分数
        
        日均成交额越大，流动性越好，分数越高
        - avg_turnover = 0 → 0分
        - avg_turnover = 1亿 → 50分
        - avg_turnover = 2亿 → 75分
        - avg_turnover >= 10亿 → 100分
        
        Args:
            avg_turnover: 日均成交额（元）
        
        Returns:
            分数（0-100）
        """
        if avg_turnover <= 0:
            return 0.0
        
        # 转换为亿元
        turnover_yi = avg_turnover / 1e8
        
        # 分段映射
        if turnover_yi >= 10.0:
            return 100.0
        elif turnover_yi >= 1.0:
            # 1亿-10亿：线性映射 50-100
            return 50.0 + (turnover_yi - 1.0) * (50.0 / 9.0)
        else:
            # 0-1亿：线性映射 0-50
            return turnover_yi * 50.0
    
    def _calculate_fundamental_score(self, fundamental_factors: Dict) -> float:
        """
        计算基本面因子分数
        
        综合考虑：
        - ROE（净资产收益率）：越高越好
        - 资产负债率：适中最好（40-60%）
        - 净利润：正值加分，负值减分
        
        Args:
            fundamental_factors: 基本面因子字典
        
        Returns:
            分数（0-100）
        """
        score = 50.0  # 基础分
        
        # ROE 评分（权重 40%）
        roe = fundamental_factors.get('roe', 0.0)
        if roe is not None and roe > 0:
            # ROE > 15% 优秀，10-15% 良好，5-10% 一般，< 5% 较差
            if roe >= 15.0:
                roe_score = 100.0
            elif roe >= 10.0:
                roe_score = 70.0 + (roe - 10.0) * 6.0
            elif roe >= 5.0:
                roe_score = 40.0 + (roe - 5.0) * 6.0
            else:
                roe_score = roe * 8.0
            
            score += (roe_score - 50.0) * 0.4
        
        # 资产负债率评分（权重 30%）
        debt_ratio = fundamental_factors.get('debt_ratio', 0.0)
        if debt_ratio is not None:
            # 40-60% 最佳，偏离越多分数越低
            if 40.0 <= debt_ratio <= 60.0:
                debt_score = 100.0
            elif debt_ratio < 40.0:
                # 负债率过低，可能资金利用效率不高
                debt_score = 50.0 + debt_ratio * 1.25
            elif debt_ratio <= 80.0:
                # 60-80%：可接受范围
                debt_score = 100.0 - (debt_ratio - 60.0) * 2.5
            else:
                # > 80%：风险较高
                debt_score = max(0.0, 50.0 - (debt_ratio - 80.0) * 2.5)
            
            score += (debt_score - 50.0) * 0.3
        
        # 净利润评分（权重 30%）
        net_profit = fundamental_factors.get('net_profit', 0.0)
        if net_profit is not None:
            if net_profit > 0:
                # 盈利加分
                profit_score = min(100.0, 50.0 + 50.0)
            elif net_profit < 0:
                # 亏损减分
                profit_score = 0.0
            else:
                profit_score = 50.0
            
            score += (profit_score - 50.0) * 0.3
        
        return max(0.0, min(100.0, score))
    
    def get_score_breakdown(
        self,
        signal: Dict,
        technical_factors: Dict,
        fundamental_factors: Optional[Dict] = None
    ) -> Dict:
        """
        获取评分详细分解
        
        Args:
            signal: 原始信号字典
            technical_factors: 技术面因子字典
            fundamental_factors: 基本面因子字典（可选）
        
        Returns:
            评分分解字典
            {
                'total_score': float,
                'breakdown': {
                    'volume': {'score': float, 'weight': float, 'contribution': float},
                    'ma_angle': {...},
                    'market_env': {...},
                    'liquidity': {...},
                    'fundamental': {...}
                }
            }
        """
        # 计算各因子分数
        volume_score = self._calculate_volume_score(technical_factors.get('volume_ratio', 1.0))
        ma_angle_score = self._calculate_ma_angle_score(technical_factors.get('ma_distance', 0.0))
        market_env_score = self._calculate_market_env_score(technical_factors.get('date'))
        liquidity_score = self._calculate_liquidity_score(technical_factors.get('avg_turnover', 0.0))
        
        if fundamental_factors:
            fundamental_score = self._calculate_fundamental_score(fundamental_factors)
        else:
            fundamental_score = 50.0
        
        # 计算总分
        total_score = (
            volume_score * self.WEIGHTS['volume'] +
            ma_angle_score * self.WEIGHTS['ma_angle'] +
            market_env_score * self.WEIGHTS['market_env'] +
            liquidity_score * self.WEIGHTS['liquidity'] +
            fundamental_score * self.WEIGHTS['fundamental']
        )
        
        total_score = max(0.0, min(100.0, total_score))
        
        return {
            'total_score': round(total_score, 2),
            'breakdown': {
                'volume': {
                    'score': round(volume_score, 2),
                    'weight': self.WEIGHTS['volume'],
                    'contribution': round(volume_score * self.WEIGHTS['volume'], 2)
                },
                'ma_angle': {
                    'score': round(ma_angle_score, 2),
                    'weight': self.WEIGHTS['ma_angle'],
                    'contribution': round(ma_angle_score * self.WEIGHTS['ma_angle'], 2)
                },
                'market_env': {
                    'score': round(market_env_score, 2),
                    'weight': self.WEIGHTS['market_env'],
                    'contribution': round(market_env_score * self.WEIGHTS['market_env'], 2)
                },
                'liquidity': {
                    'score': round(liquidity_score, 2),
                    'weight': self.WEIGHTS['liquidity'],
                    'contribution': round(liquidity_score * self.WEIGHTS['liquidity'], 2)
                },
                'fundamental': {
                    'score': round(fundamental_score, 2),
                    'weight': self.WEIGHTS['fundamental'],
                    'contribution': round(fundamental_score * self.WEIGHTS['fundamental'], 2)
                }
            }
        }
