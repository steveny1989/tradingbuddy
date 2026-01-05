# -*- coding: utf-8 -*-
"""
情绪面分析器

分析股票的市场情绪和股性特征：
1. 涨跌停基因 - 识别"妖股"体质
2. 波动性分析 - 评估风险等级
3. 股性判断 - 稳健/活跃/妖股
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from src.data.database_adapter import DatabaseAdapter


class SentimentAnalyzer:
    """情绪面分析器"""
    
    def __init__(self):
        self.db = DatabaseAdapter()
    
    def analyze_sentiment(self, code: str, days: int = 30) -> Dict:
        """
        分析股票情绪面
        
        Args:
            code: 股票代码
            days: 分析天数，默认30天
            
        Returns:
            Dict: 情绪分析报告
        """
        # 获取历史数据
        df = self.db.get_daily_data(code)
        if df.empty:
            return self._empty_report(code)
        
        # 取最近N天
        df = df.sort_values('date').tail(days).copy()
        
        if len(df) < 5:
            return self._empty_report(code)
        
        # 1. 涨跌停分析
        limit_analysis = self._analyze_limit_moves(df)
        
        # 2. 波动性分析
        volatility_analysis = self._analyze_volatility(df)
        
        # 3. 股性判断
        character = self._judge_stock_character(limit_analysis, volatility_analysis)
        
        # 4. 生成状态和建议
        status, message = self._generate_sentiment_status(
            limit_analysis, volatility_analysis, character
        )
        
        return {
            'code': code,
            'status': status,
            'message': message,
            'character': character,
            'limit_analysis': limit_analysis,
            'volatility_analysis': volatility_analysis,
            'analysis_days': len(df)
        }
    
    def _analyze_limit_moves(self, df: pd.DataFrame) -> Dict:
        """
        分析涨跌停情况
        
        Returns:
            Dict: {
                'limit_up_days': 涨停次数,
                'limit_down_days': 跌停次数,
                'max_consecutive_up': 最高连板数,
                'yesterday_limit_up': 昨日是否涨停,
                'recent_limit_up': 近期涨停日期列表
            }
        """
        # 计算涨跌幅（如果没有pctChg字段）
        if 'pctChg' not in df.columns:
            df['pctChg'] = df['close'].pct_change() * 100
        
        # 识别涨跌停（考虑ST股票10%和普通股票10%的差异，这里简化为9.9%）
        df['is_limit_up'] = df['pctChg'] >= 9.9
        df['is_limit_down'] = df['pctChg'] <= -9.9
        
        limit_up_days = int(df['is_limit_up'].sum())
        limit_down_days = int(df['is_limit_down'].sum())
        
        # 计算最高连板数
        max_consecutive_up = self._calculate_max_consecutive(df['is_limit_up'])
        
        # 昨日是否涨停
        yesterday_limit_up = bool(df.iloc[-1]['is_limit_up']) if len(df) > 0 else False
        
        # 近期涨停日期
        recent_limit_up = df[df['is_limit_up']]['date'].tolist()
        
        return {
            'limit_up_days': limit_up_days,
            'limit_down_days': limit_down_days,
            'max_consecutive_up': max_consecutive_up,
            'yesterday_limit_up': yesterday_limit_up,
            'recent_limit_up': recent_limit_up[-5:] if recent_limit_up else []  # 最近5次
        }
    
    def _calculate_max_consecutive(self, series: pd.Series) -> int:
        """计算最大连续True的数量"""
        max_count = 0
        current_count = 0
        
        for value in series:
            if value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """
        分析波动性
        
        Returns:
            Dict: {
                'avg_amplitude': 平均振幅,
                'max_amplitude': 最大振幅,
                'avg_change': 平均涨跌幅,
                'volatility_score': 波动性评分 (0-100)
            }
        """
        # 计算涨跌幅（如果没有pctChg字段）
        if 'pctChg' not in df.columns:
            df['pctChg'] = df['close'].pct_change() * 100
        
        # 计算振幅（如果没有amplitude字段，用high-low计算）
        if 'amplitude' in df.columns:
            amplitudes = df['amplitude'].abs()
        else:
            amplitudes = ((df['high'] - df['low']) / df['low'] * 100).abs()
        
        avg_amplitude = float(amplitudes.mean())
        max_amplitude = float(amplitudes.max())
        
        # 平均涨跌幅
        avg_change = float(df['pctChg'].abs().mean())
        
        # 波动性评分（0-100）
        # 基于平均振幅：0-2% → 0-20分，2-4% → 20-50分，4-6% → 50-80分，>6% → 80-100分
        if avg_amplitude < 2:
            volatility_score = avg_amplitude / 2 * 20
        elif avg_amplitude < 4:
            volatility_score = 20 + (avg_amplitude - 2) / 2 * 30
        elif avg_amplitude < 6:
            volatility_score = 50 + (avg_amplitude - 4) / 2 * 30
        else:
            volatility_score = min(100, 80 + (avg_amplitude - 6) / 2 * 20)
        
        return {
            'avg_amplitude': round(avg_amplitude, 2),
            'max_amplitude': round(max_amplitude, 2),
            'avg_change': round(avg_change, 2),
            'volatility_score': round(volatility_score, 1)
        }
    
    def _judge_stock_character(self, limit_analysis: Dict, volatility_analysis: Dict) -> str:
        """
        判断股性
        
        Returns:
            'demon': 妖股（高风险高收益）
            'active': 活跃（中等风险收益）
            'stable': 稳健（低风险低收益）
        """
        limit_up_days = limit_analysis['limit_up_days']
        max_consecutive = limit_analysis['max_consecutive_up']
        avg_amplitude = volatility_analysis['avg_amplitude']
        
        # 妖股特征：多次涨停或高连板或高波动
        if limit_up_days >= 5 or max_consecutive >= 3 or avg_amplitude > 6:
            return 'demon'
        
        # 活跃股特征：有涨停或中等波动
        if limit_up_days >= 2 or avg_amplitude > 3:
            return 'active'
        
        # 稳健股：低波动
        return 'stable'
    
    def _generate_sentiment_status(
        self, 
        limit_analysis: Dict, 
        volatility_analysis: Dict,
        character: str
    ) -> tuple[str, str]:
        """
        生成情绪面状态和建议
        
        Returns:
            (status, message)
        """
        limit_up_days = limit_analysis['limit_up_days']
        max_consecutive = limit_analysis['max_consecutive_up']
        yesterday_limit_up = limit_analysis['yesterday_limit_up']
        avg_amplitude = volatility_analysis['avg_amplitude']
        
        # 昨日涨停 - 特殊处理
        if yesterday_limit_up:
            return (
                'yellow',
                f'昨日涨停，今日可能继续冲高或回调，注意涨停板打开要及时止盈'
            )
        
        # 妖股
        if character == 'demon':
            if limit_up_days >= 5:
                return (
                    'yellow',
                    f'该股属于"妖股"体质，近30天涨停{limit_up_days}次，波动极大，心脏不好别碰'
                )
            elif max_consecutive >= 3:
                return (
                    'yellow',
                    f'该股曾{max_consecutive}连板，属于"妖股"体质，波动极大，适合短线高手'
                )
            else:
                return (
                    'yellow',
                    f'该股波动极大（日均振幅{avg_amplitude:.1f}%），风险较高，不适合新手'
                )
        
        # 活跃股
        if character == 'active':
            if limit_up_days > 0:
                return (
                    'green',
                    f'该股股性活跃，近30天涨停{limit_up_days}次，适合波段操作'
                )
            else:
                return (
                    'green',
                    f'该股波动适中（日均振幅{avg_amplitude:.1f}%），适合中短线交易'
                )
        
        # 稳健股
        return (
            'green',
            f'该股波动平稳（日均振幅{avg_amplitude:.1f}%），近30天无涨停，适合长线持有'
        )
    
    def _empty_report(self, code: str) -> Dict:
        """返回空报告"""
        return {
            'code': code,
            'status': 'yellow',
            'message': '数据不足，无法分析情绪面',
            'character': 'unknown',
            'limit_analysis': {},
            'volatility_analysis': {},
            'analysis_days': 0
        }
    
    def generate_sentiment_report(self, code: str, days: int = 30) -> Dict:
        """
        生成情绪面报告（便捷方法）
        
        Args:
            code: 股票代码
            days: 分析天数
            
        Returns:
            Dict: 情绪分析报告
        """
        return self.analyze_sentiment(code, days)


# 便捷函数
def analyze_stock_sentiment(code: str, days: int = 30) -> Dict:
    """
    分析股票情绪面（便捷函数）
    
    Args:
        code: 股票代码
        days: 分析天数
        
    Returns:
        Dict: 情绪分析报告
    """
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_sentiment(code, days)
