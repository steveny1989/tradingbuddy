"""
流动性评分器

评估股票的流动性质量，识别"死水股"。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from .models import LiquidityScore


class LiquidityScorer:
    """流动性评分器"""
    
    def score(self, stock_data: pd.DataFrame) -> LiquidityScore:
        """
        计算流动性评分
        
        Args:
            stock_data: 股票数据，包含 amount, turnover_rate 等字段
            
        Returns:
            LiquidityScore: 流动性评分对象
        """
        score = 50  # 基础分
        reasons = []
        
        # 1. 日均成交额（60 分）
        amount_score, amount_reasons = self._score_amount(stock_data)
        score += amount_score
        reasons.extend(amount_reasons)
        
        # 2. 换手率（20 分）
        turnover_score, turnover_reasons = self._score_turnover(stock_data)
        score += turnover_score
        reasons.extend(turnover_reasons)
        
        # 3. 成交额稳定性（20 分）
        stability_score, stability_reasons = self._score_stability(stock_data)
        score += stability_score
        reasons.extend(stability_reasons)
        
        # 限制评分范围 [0, 100]
        score = max(0, min(100, score))
        
        # 提取关键指标
        indicators = self._extract_indicators(stock_data)
        
        return LiquidityScore(
            value=score,
            reasons=reasons,
            indicators=indicators
        )
    
    def _score_amount(self, df: pd.DataFrame) -> Tuple[float, List[str]]:
        """评分日均成交额"""
        score = 0
        reasons = []
        
        # 计算最近 20 天平均成交额
        recent_20 = df.tail(20)
        if len(recent_20) < 20:
            return score, reasons
        
        # 成交额单位：元
        avg_amount_20 = recent_20['amount'].mean()
        
        if avg_amount_20 > 500_000_000:  # 5 亿以上
            score += 40
            reasons.append(f"日均成交额 {avg_amount_20/100_000_000:.1f} 亿，流动性优秀")
        elif avg_amount_20 > 100_000_000:  # 1-5 亿
            score += 25
            reasons.append(f"日均成交额 {avg_amount_20/100_000_000:.1f} 亿，流动性良好")
        elif avg_amount_20 > 50_000_000:  # 5000 万-1 亿
            score += 10
            reasons.append(f"日均成交额 {avg_amount_20/100_000_000:.1f} 亿，流动性一般")
        else:  # 5000 万以下
            score -= 30
            reasons.append(f"日均成交额仅 {avg_amount_20/100_000_000:.2f} 亿，流动性不足")
        
        return score, reasons
    
    def _score_turnover(self, df: pd.DataFrame) -> Tuple[float, List[str]]:
        """评分换手率"""
        score = 0
        reasons = []
        
        latest = df.iloc[-1]
        
        # 检查是否有换手率数据
        if 'turnover_rate' in df.columns and pd.notna(latest['turnover_rate']):
            turnover_rate = latest['turnover_rate']
        elif 'turnover' in df.columns and pd.notna(latest['turnover']):
            turnover_rate = latest['turnover']
        else:
            # 如果没有换手率数据，尝试从成交量和流通股本计算
            # 但这需要额外的数据，这里先跳过
            return score, reasons
        
        if 2 < turnover_rate < 10:  # 正常换手率
            score += 15
            reasons.append(f"换手率 {turnover_rate:.2f}%，交易活跃")
        elif turnover_rate > 15:  # 过高
            score -= 10
            reasons.append(f"换手率 {turnover_rate:.2f}%，过度投机")
        elif turnover_rate < 1:  # 过低
            score -= 15
            reasons.append(f"换手率 {turnover_rate:.2f}%，交易清淡")
        
        return score, reasons
    
    def _score_stability(self, df: pd.DataFrame) -> Tuple[float, List[str]]:
        """评分成交额稳定性"""
        score = 0
        reasons = []
        
        # 计算最近 20 天成交额的变异系数
        recent_20 = df.tail(20)
        if len(recent_20) < 20:
            return score, reasons
        
        avg_amount_20 = recent_20['amount'].mean()
        amount_std = recent_20['amount'].std()
        
        if avg_amount_20 > 0:
            amount_cv = amount_std / avg_amount_20  # 变异系数
            
            if amount_cv < 0.5:  # 稳定
                score += 15
                reasons.append("成交额稳定，资金持续关注")
            elif amount_cv > 1.5:  # 波动大
                score -= 10
                reasons.append("成交额波动大，资金不稳定")
        
        return score, reasons
    
    def _extract_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """提取关键指标"""
        indicators = {}
        
        # 计算最近 20 天平均成交额
        recent_20 = df.tail(20)
        if len(recent_20) >= 20:
            avg_amount_20 = recent_20['amount'].mean()
            indicators['avg_amount_20'] = float(avg_amount_20)
            
            # 计算变异系数
            amount_std = recent_20['amount'].std()
            if avg_amount_20 > 0:
                indicators['amount_cv'] = float(amount_std / avg_amount_20)
        
        # 获取最新换手率
        latest = df.iloc[-1]
        if 'turnover_rate' in df.columns and pd.notna(latest['turnover_rate']):
            indicators['turnover_rate'] = float(latest['turnover_rate'])
        elif 'turnover' in df.columns and pd.notna(latest['turnover']):
            indicators['turnover_rate'] = float(latest['turnover'])
        
        return indicators
