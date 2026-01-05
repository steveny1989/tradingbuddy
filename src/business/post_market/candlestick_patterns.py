# -*- coding: utf-8 -*-
"""
K线形态识别模块

不依赖talib，用纯Python实现常见K线形态识别
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class PatternResult:
    """形态识别结果"""
    pattern_name: str           # 形态名称 (英文)
    pattern_name_cn: str        # 形态名称 (中文)
    signal: str                 # 信号: bullish/bearish/neutral
    signal_cn: str              # 信号 (中文): 看涨/看跌/中性
    confidence: str             # 置信度: high/medium/low
    description: str            # 人话描述
    emoji: str                  # 表情符号


class CandlestickAnalyzer:
    """K线形态分析器"""
    
    def __init__(self, open_price: float, high: float, low: float, close: float):
        """
        初始化K线分析器
        
        Args:
            open_price: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
        """
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        
        # 计算基本指标
        self.body = abs(close - open_price)
        self.upper_shadow = high - max(open_price, close)
        self.lower_shadow = min(open_price, close) - low
        self.range = high - low
        
        # 避免除零
        if self.range == 0:
            self.range = 0.0001
        
        # 计算比例
        self.body_ratio = self.body / self.range
        self.upper_shadow_ratio = self.upper_shadow / self.range
        self.lower_shadow_ratio = self.lower_shadow / self.range
        
        # 判断阴阳
        self.is_bullish = close > open_price
        self.is_bearish = close < open_price
    
    def is_hammer(self) -> bool:
        """
        识别锤子线 (Hammer) - 见底信号
        
        特征:
        - 下影线长度 >= 实体长度的2倍
        - 上影线很短 (< 实体长度的0.3倍)
        - 实体占比较小 (< 30%)
        """
        if self.body == 0:
            return False
        
        return (
            self.lower_shadow >= self.body * 2 and
            self.upper_shadow < self.body * 0.3 and
            self.body_ratio < 0.3 and
            self.lower_shadow_ratio > 0.5
        )
    
    def is_hanging_man(self) -> bool:
        """
        识别上吊线 (Hanging Man) - 见顶信号
        
        形态和锤子线一样，但出现在上涨趋势中
        这里只识别形态，趋势判断由外部完成
        """
        return self.is_hammer()
    
    def is_doji(self) -> bool:
        """
        识别十字星 (Doji) - 变盘信号
        
        特征:
        - 实体很小 (< 5%的振幅)
        - 有明显的上下影线
        """
        return (
            self.body_ratio < 0.05 and
            self.upper_shadow > 0 and
            self.lower_shadow > 0
        )
    
    def is_long_legged_doji(self) -> bool:
        """
        识别长腿十字星 (Long-Legged Doji) - 强烈变盘信号
        
        特征:
        - 实体很小
        - 上下影线都很长 (各占30%以上)
        """
        return (
            self.body_ratio < 0.05 and
            self.upper_shadow_ratio > 0.3 and
            self.lower_shadow_ratio > 0.3
        )
    
    def is_gravestone_doji(self) -> bool:
        """
        识别墓碑线 (Gravestone Doji) - 见顶信号
        
        特征:
        - 实体很小
        - 有很长的上影线 (> 60%)
        - 几乎没有下影线 (< 10%)
        """
        return (
            self.body_ratio < 0.05 and
            self.upper_shadow_ratio > 0.6 and
            self.lower_shadow_ratio < 0.1
        )
    
    def is_dragonfly_doji(self) -> bool:
        """
        识别蜻蜓线 (Dragonfly Doji) - 见底信号
        
        特征:
        - 实体很小
        - 有很长的下影线 (> 60%)
        - 几乎没有上影线 (< 10%)
        """
        return (
            self.body_ratio < 0.05 and
            self.lower_shadow_ratio > 0.6 and
            self.upper_shadow_ratio < 0.1
        )
    
    def is_long_white_candle(self, pct_chg: float) -> bool:
        """
        识别大阳线 (Long White Candle) - 强势上涨
        
        特征:
        - 阳线
        - 实体占比大 (> 70%)
        - 涨幅较大 (> 3%)
        - 上下影线都很短
        """
        return (
            self.is_bullish and
            self.body_ratio > 0.7 and
            pct_chg > 3.0 and
            self.upper_shadow_ratio < 0.15 and
            self.lower_shadow_ratio < 0.15
        )
    
    def is_long_black_candle(self, pct_chg: float) -> bool:
        """
        识别大阴线 (Long Black Candle) - 强势下跌
        
        特征:
        - 阴线
        - 实体占比大 (> 70%)
        - 跌幅较大 (< -3%)
        - 上下影线都很短
        """
        return (
            self.is_bearish and
            self.body_ratio > 0.7 and
            pct_chg < -3.0 and
            self.upper_shadow_ratio < 0.15 and
            self.lower_shadow_ratio < 0.15
        )


class PatternRecognizer:
    """K线形态识别器"""
    
    @staticmethod
    def recognize_single_candle(
        open_price: float,
        high: float,
        low: float,
        close: float,
        pct_chg: float = 0.0,
        trend: str = 'neutral'
    ) -> Optional[PatternResult]:
        """
        识别单根K线形态
        
        Args:
            open_price: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            pct_chg: 涨跌幅 (%)
            trend: 趋势 (up/down/neutral)
        
        Returns:
            PatternResult or None
        """
        analyzer = CandlestickAnalyzer(open_price, high, low, close)
        
        # 按优先级检查形态
        
        # 1. 特殊十字星 (优先级高)
        if analyzer.is_gravestone_doji():
            return PatternResult(
                pattern_name='gravestone_doji',
                pattern_name_cn='墓碑线',
                signal='bearish',
                signal_cn='看跌',
                confidence='high',
                description='这根K线很有意思，开盘后一路冲高，但收盘时又跌回开盘价附近，说明上方抛压很重。这种形态叫"墓碑线"，通常是见顶信号，建议谨慎',
                emoji='🔴'
            )
        
        if analyzer.is_dragonfly_doji():
            return PatternResult(
                pattern_name='dragonfly_doji',
                pattern_name_cn='蜻蜓线',
                signal='bullish',
                signal_cn='看涨',
                confidence='high',
                description='今天这根K线挺特别的，开盘后一度大跌，但尾盘又被拉回来了，说明下方有人在接盘。这种形态叫"蜻蜓线"，往往是见底信号，可以关注',
                emoji='🟢'
            )
        
        if analyzer.is_long_legged_doji():
            return PatternResult(
                pattern_name='long_legged_doji',
                pattern_name_cn='长腿十字星',
                signal='neutral',
                signal_cn='中性',
                confidence='high',
                description='今天盘中波动很大，上下都试探了一遍，但最后收在开盘价附近。这说明多空双方在激烈争夺，谁也没占到便宜。这种时候最好观望，等方向明确了再说',
                emoji='🟡'
            )
        
        # 2. 锤子线 / 上吊线 (需要结合趋势)
        if analyzer.is_hammer():
            if trend == 'down':
                return PatternResult(
                    pattern_name='hammer',
                    pattern_name_cn='锤子线',
                    signal='bullish',
                    signal_cn='看涨',
                    confidence='high',
                    description='注意看这根K线，虽然盘中一度大跌，但最后被拉了回来，下影线很长。这说明下方有人在抄底，空方打不下去了。这种形态叫"锤子线"，经常出现在底部，可能要反弹了',
                    emoji='🟢'
                )
            elif trend == 'up':
                return PatternResult(
                    pattern_name='hanging_man',
                    pattern_name_cn='上吊线',
                    signal='bearish',
                    signal_cn='看跌',
                    confidence='medium',
                    description='这根K线形态有点危险，虽然收盘价还不错，但盘中曾经大幅下跌。在上涨趋势中出现这种形态，说明多方力量开始减弱了，要小心回调',
                    emoji='🔴'
                )
        
        # 3. 大阳线 / 大阴线
        if analyzer.is_long_white_candle(pct_chg):
            return PatternResult(
                pattern_name='long_white_candle',
                pattern_name_cn='大阳线',
                signal='bullish',
                signal_cn='看涨',
                confidence='high',
                description=f'今天走得很强势，全天上涨{pct_chg:.1f}%，而且几乎没有回调，收了一根大阳线。这说明买盘很积极，多方力量很强，短期趋势向好',
                emoji='🟢'
            )
        
        if analyzer.is_long_black_candle(pct_chg):
            return PatternResult(
                pattern_name='long_black_candle',
                pattern_name_cn='大阴线',
                signal='bearish',
                signal_cn='看跌',
                confidence='high',
                description=f'今天走得很弱，全天下跌{abs(pct_chg):.1f}%，而且几乎没有反弹，收了一根大阴线。这说明卖盘很汹涌，空方力量很强，短期要注意风险',
                emoji='🔴'
            )
        
        # 4. 普通十字星
        if analyzer.is_doji():
            return PatternResult(
                pattern_name='doji',
                pattern_name_cn='十字星',
                signal='neutral',
                signal_cn='中性',
                confidence='medium',
                description='今天收了一根十字星，开盘价和收盘价几乎一样。这说明多空双方势均力敌，谁也没占到便宜。这种时候方向不明，建议先观望，等突破了再说',
                emoji='🟡'
            )
        
        return None
    
    @staticmethod
    def recognize_two_candles(
        prev_open: float,
        prev_high: float,
        prev_low: float,
        prev_close: float,
        curr_open: float,
        curr_high: float,
        curr_low: float,
        curr_close: float
    ) -> Optional[PatternResult]:
        """
        识别两根K线组合形态
        
        Args:
            prev_*: 前一天的OHLC
            curr_*: 当天的OHLC
        
        Returns:
            PatternResult or None
        """
        prev_analyzer = CandlestickAnalyzer(prev_open, prev_high, prev_low, prev_close)
        curr_analyzer = CandlestickAnalyzer(curr_open, curr_high, curr_low, curr_close)
        
        # 看涨吞没 (Bullish Engulfing)
        if (
            prev_analyzer.is_bearish and
            curr_analyzer.is_bullish and
            curr_open < prev_close and
            curr_close > prev_open and
            curr_analyzer.body_ratio > 0.6
        ):
            return PatternResult(
                pattern_name='bullish_engulfing',
                pattern_name_cn='看涨吞没',
                signal='bullish',
                signal_cn='看涨',
                confidence='high',
                description='看这两天的K线，昨天还是阴线，今天直接来了一根大阳线，把昨天的跌幅全吃回来了。这种形态叫"看涨吞没"，说明多方开始发力了，可能要反转向上',
                emoji='🟢'
            )
        
        # 看跌吞没 (Bearish Engulfing)
        if (
            prev_analyzer.is_bullish and
            curr_analyzer.is_bearish and
            curr_open > prev_close and
            curr_close < prev_open and
            curr_analyzer.body_ratio > 0.6
        ):
            return PatternResult(
                pattern_name='bearish_engulfing',
                pattern_name_cn='看跌吞没',
                signal='bearish',
                signal_cn='看跌',
                confidence='high',
                description='注意这两天的走势，昨天还涨得好好的，今天突然来了一根大阴线，把昨天的涨幅全吞了。这种形态叫"看跌吞没"，说明空方开始反扑了，要小心',
                emoji='🔴'
            )
        
        return None
    
    @staticmethod
    def recognize_multi_candles(df: pd.DataFrame) -> Optional[PatternResult]:
        """
        识别多根K线组合形态（3根或更多）
        
        Args:
            df: 最近的K线数据（至少3根）
        
        Returns:
            PatternResult or None
        """
        if len(df) < 3:
            return None
        
        # 获取最近3天
        recent = df.tail(3)
        day1 = recent.iloc[0]
        day2 = recent.iloc[1]
        day3 = recent.iloc[2]
        
        # 三连阳
        if (day1['close'] > day1['open'] and 
            day2['close'] > day2['open'] and 
            day3['close'] > day3['open'] and
            day3['close'] > day2['close'] > day1['close']):
            
            total_gain = (day3['close'] - day1['open']) / day1['open'] * 100
            return PatternResult(
                pattern_name='three_white_soldiers',
                pattern_name_cn='三连阳',
                signal='bullish',
                signal_cn='看涨',
                confidence='high',
                description=f'连续三天收阳线，而且一天比一天高，累计涨了{total_gain:.1f}%。这种走势叫"红三兵"，说明多方力量很强，买盘持续涌入，短期看涨',
                emoji='🟢'
            )
        
        # 三连阴
        if (day1['close'] < day1['open'] and 
            day2['close'] < day2['open'] and 
            day3['close'] < day3['open'] and
            day3['close'] < day2['close'] < day1['close']):
            
            total_loss = (day3['close'] - day1['open']) / day1['open'] * 100
            return PatternResult(
                pattern_name='three_black_crows',
                pattern_name_cn='三连阴',
                signal='bearish',
                signal_cn='看跌',
                confidence='high',
                description=f'连续三天收阴线，而且一天比一天低，累计跌了{abs(total_loss):.1f}%。这种走势叫"三只乌鸦"，说明空方力量很强，卖盘持续涌出，短期看跌',
                emoji='🔴'
            )
        
        return None
    
    @staticmethod
    def analyze_stock_pattern(df: pd.DataFrame, trend_days: int = 20) -> Dict:
        """
        分析股票的K线形态
        
        Args:
            df: 包含OHLC数据的DataFrame
            trend_days: 用于判断趋势的天数
        
        Returns:
            分析结果字典
        """
        if len(df) < 2:
            return {'pattern': None, 'trend': 'neutral', 'volume_signal': 'normal'}
        
        # 确保数据按日期排序
        df = df.sort_values('date')
        
        # 获取最新两天的数据
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 判断趋势 (用MA20)
        if len(df) >= trend_days:
            recent_prices = df['close'].tail(trend_days)
            ma = recent_prices.mean()
            current_price = latest['close']
            
            if current_price > ma * 1.05:
                trend = 'up'
            elif current_price < ma * 0.95:
                trend = 'down'
            else:
                trend = 'neutral'
        else:
            trend = 'neutral'
        
        # 判断成交量
        if len(df) >= 5:
            recent_volume = df['volume'].tail(5).mean()
            current_volume = latest['volume']
            volume_ratio = current_volume / recent_volume if recent_volume > 0 else 1.0
            
            if volume_ratio > 1.5:
                volume_signal = 'expand'  # 放量
            elif volume_ratio < 0.7:
                volume_signal = 'shrink'  # 缩量
            else:
                volume_signal = 'normal'
        else:
            volume_signal = 'normal'
            volume_ratio = 1.0
        
        # 先检查多根K线组合形态（优先级最高）
        if len(df) >= 3:
            multi_candle_pattern = PatternRecognizer.recognize_multi_candles(df)
            if multi_candle_pattern:
                # 根据成交量调整描述
                if volume_signal == 'expand':
                    multi_candle_pattern.description += f"，而且成交量也在放大（量比{volume_ratio:.1f}），这个趋势比较可靠"
                
                return {
                    'pattern': multi_candle_pattern,
                    'trend': trend,
                    'date': latest['date'],
                    'volume_signal': volume_signal,
                    'volume_ratio': volume_ratio
                }
        
        # 再检查两根K线组合形态
        two_candle_pattern = PatternRecognizer.recognize_two_candles(
            prev['open'], prev['high'], prev['low'], prev['close'],
            latest['open'], latest['high'], latest['low'], latest['close']
        )
        
        if two_candle_pattern:
            # 根据成交量调整描述
            if volume_signal == 'expand':
                two_candle_pattern.description += f"，而且今天还放量了（量比{volume_ratio:.1f}），信号更可靠"
            elif volume_signal == 'shrink':
                two_candle_pattern.description += f"，不过今天成交量不大（量比{volume_ratio:.1f}），还需要观察"
            
            return {
                'pattern': two_candle_pattern,
                'trend': trend,
                'date': latest['date'],
                'volume_signal': volume_signal,
                'volume_ratio': volume_ratio
            }
        
        # 再检查单根K线形态
        pct_chg = latest.get('pct_chg', 0.0)
        single_candle_pattern = PatternRecognizer.recognize_single_candle(
            latest['open'],
            latest['high'],
            latest['low'],
            latest['close'],
            pct_chg,
            trend
        )
        
        if single_candle_pattern:
            # 根据成交量调整描述
            if volume_signal == 'expand':
                single_candle_pattern.description += f"，而且今天还放量了（量比{volume_ratio:.1f}），这个信号比较可靠"
            elif volume_signal == 'shrink':
                single_candle_pattern.description += f"，不过今天成交量萎缩（量比{volume_ratio:.1f}），力度不够"
        
        return {
            'pattern': single_candle_pattern,
            'trend': trend,
            'date': latest['date'],
            'volume_signal': volume_signal,
            'volume_ratio': volume_ratio
        }


# 便捷函数
def analyze_candlestick_pattern(df: pd.DataFrame) -> Dict:
    """
    分析K线形态（便捷函数）
    
    Args:
        df: 包含OHLC数据的DataFrame
    
    Returns:
        分析结果
    """
    return PatternRecognizer.analyze_stock_pattern(df)
