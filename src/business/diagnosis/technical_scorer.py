"""
技术面评分器

评估股票的技术形态质量，包括均线形态、成交量变化、价格位置、MACD 和 RSI 指标。
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from .models import TechnicalScore


class TechnicalScorer:
    """技术面评分器"""
    
    def score(self, stock_data: pd.DataFrame) -> TechnicalScore:
        """
        计算技术面评分
        
        Args:
            stock_data: 股票数据（至少 60 天），包含 close, volume, ma5, ma20, ma60 等字段
            
        Returns:
            TechnicalScore: 技术面评分对象
        """
        if len(stock_data) < 60:
            raise ValueError(f"数据不足: 需要至少 60 天数据，实际只有 {len(stock_data)} 天")
        
        score = 50  # 基础分
        reasons = []
        
        # 确保数据按日期排序
        stock_data = stock_data.sort_values('date')
        
        # 计算技术指标（如果不存在）
        stock_data = self._calculate_indicators(stock_data)
        
        # 1. 均线形态（30 分）
        ma_score, ma_reasons = self._score_ma_pattern(stock_data)
        score += ma_score
        reasons.extend(ma_reasons)
        
        # 2. 成交量变化（25 分）
        volume_score, volume_reasons = self._score_volume(stock_data)
        score += volume_score
        reasons.extend(volume_reasons)
        
        # 3. 价格位置（20 分）
        price_score, price_reasons = self._score_price_position(stock_data)
        score += price_score
        reasons.extend(price_reasons)
        
        # 4. MACD 指标（15 分）
        macd_score, macd_reasons = self._score_macd(stock_data)
        score += macd_score
        reasons.extend(macd_reasons)
        
        # 5. RSI 指标（10 分）
        rsi_score, rsi_reasons = self._score_rsi(stock_data)
        score += rsi_score
        reasons.extend(rsi_reasons)
        
        # 限制评分范围 [0, 100]
        score = max(0, min(100, score))
        
        # 提取关键指标
        indicators = self._extract_indicators(stock_data)
        
        return TechnicalScore(
            value=score,
            reasons=reasons,
            indicators=indicators
        )
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        df = df.copy()
        
        # 计算均线（如果不存在）
        if 'ma5' not in df.columns:
            df['ma5'] = df['close'].rolling(window=5).mean()
        if 'ma20' not in df.columns:
            df['ma20'] = df['close'].rolling(window=20).mean()
        if 'ma60' not in df.columns:
            df['ma60'] = df['close'].rolling(window=60).mean()
        
        # 计算 MACD
        if 'macd' not in df.columns or 'macd_signal' not in df.columns:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 计算 RSI
        if 'rsi' not in df.columns:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def _score_ma_pattern(self, df: pd.DataFrame) -> tuple:
        """评分均线形态"""
        score = 0
        reasons = []
        
        # 获取最新数据
        latest = df.iloc[-1]
        ma5 = latest['ma5']
        ma20 = latest['ma20']
        ma60 = latest['ma60']
        current_price = latest['close']
        
        # 检查多头/空头排列
        if pd.notna(ma5) and pd.notna(ma20) and pd.notna(ma60):
            if ma5 > ma20 > ma60:  # 多头排列
                score += 25
                reasons.append("均线呈多头排列，趋势向上")
            elif ma5 < ma20 < ma60:  # 空头排列
                score -= 20
                reasons.append("均线呈空头排列，趋势向下")
        
        # 检查价格与 20 日均线关系
        if pd.notna(ma20):
            if current_price > ma20:
                score += 5
                reasons.append("股价站上 20 日均线")
            else:
                score -= 5
                reasons.append("股价跌破 20 日均线")
        
        return score, reasons
    
    def _score_volume(self, df: pd.DataFrame) -> tuple:
        """评分成交量变化"""
        score = 0
        reasons = []
        
        # 计算最近 20 天平均成交量
        recent_20 = df.tail(20)
        if len(recent_20) < 20:
            return score, reasons
        
        avg_volume_20 = recent_20['volume'].mean()
        recent_volume = df.iloc[-1]['volume']
        
        if avg_volume_20 > 0:
            volume_ratio = recent_volume / avg_volume_20
            
            if volume_ratio > 2.0:  # 放量突破
                score += 20
                reasons.append(f"成交量放大 {volume_ratio:.1f} 倍，资金活跃")
            elif volume_ratio > 1.5:
                score += 10
                reasons.append(f"成交量温和放大 {volume_ratio:.1f} 倍")
            elif volume_ratio < 0.5:  # 缩量
                score -= 15
                reasons.append("成交量严重萎缩，资金流出")
        
        return score, reasons
    
    def _score_price_position(self, df: pd.DataFrame) -> tuple:
        """评分价格位置"""
        score = 0
        reasons = []
        
        # 获取最近 60 天的高低点
        recent_60 = df.tail(60)
        if len(recent_60) < 60:
            return score, reasons
        
        high_60 = recent_60['high'].max()
        low_60 = recent_60['low'].min()
        current_price = df.iloc[-1]['close']
        
        if high_60 > low_60:
            price_position = (current_price - low_60) / (high_60 - low_60)
            
            if price_position > 0.8:  # 接近高位
                score += 10
                reasons.append("股价接近近期高点，强势")
            elif price_position < 0.3:  # 接近低位
                score += 15
                reasons.append("股价处于近期低位，安全边际高")
        
        return score, reasons
    
    def _score_macd(self, df: pd.DataFrame) -> tuple:
        """评分 MACD 指标"""
        score = 0
        reasons = []
        
        if len(df) < 2:
            return score, reasons
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        if pd.notna(latest['macd_hist']) and pd.notna(previous['macd_hist']):
            macd_hist = latest['macd_hist']
            prev_macd_hist = previous['macd_hist']
            
            if macd_hist > 0 and prev_macd_hist <= 0:  # 金叉
                score += 15
                reasons.append("MACD 金叉，买入信号")
            elif macd_hist < 0 and prev_macd_hist >= 0:  # 死叉
                score -= 15
                reasons.append("MACD 死叉，卖出信号")
        
        return score, reasons
    
    def _score_rsi(self, df: pd.DataFrame) -> tuple:
        """评分 RSI 指标"""
        score = 0
        reasons = []
        
        latest = df.iloc[-1]
        
        if pd.notna(latest['rsi']):
            rsi = latest['rsi']
            
            if 30 < rsi < 70:  # 正常区间
                score += 5
            elif rsi > 80:  # 超买
                score -= 10
                reasons.append("RSI 超买，注意回调风险")
            elif rsi < 20:  # 超卖
                score += 10
                reasons.append("RSI 超卖，可能反弹")
        
        return score, reasons
    
    def _extract_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """提取关键指标"""
        latest = df.iloc[-1]
        recent_20 = df.tail(20)
        recent_60 = df.tail(60)
        
        indicators = {
            'ma5': float(latest['ma5']) if pd.notna(latest['ma5']) else None,
            'ma20': float(latest['ma20']) if pd.notna(latest['ma20']) else None,
            'ma60': float(latest['ma60']) if pd.notna(latest['ma60']) else None,
            'macd_hist': float(latest['macd_hist']) if pd.notna(latest['macd_hist']) else None,
            'rsi': float(latest['rsi']) if pd.notna(latest['rsi']) else None,
        }
        
        # 计算成交量比率
        if len(recent_20) >= 20:
            avg_volume_20 = recent_20['volume'].mean()
            recent_volume = latest['volume']
            if avg_volume_20 > 0:
                indicators['volume_ratio'] = float(recent_volume / avg_volume_20)
        
        # 计算价格位置
        if len(recent_60) >= 60:
            high_60 = recent_60['high'].max()
            low_60 = recent_60['low'].min()
            current_price = latest['close']
            if high_60 > low_60:
                indicators['price_position'] = float((current_price - low_60) / (high_60 - low_60))
        
        return indicators
