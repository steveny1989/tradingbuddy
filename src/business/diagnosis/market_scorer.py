"""
市场环境评分器

评估大盘和板块环境是否适合操作。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from .models import MarketScore


class MarketEnvironmentScorer:
    """市场环境评分器"""
    
    def __init__(self, data_fetcher=None):
        """
        初始化市场环境评分器
        
        Args:
            data_fetcher: 数据获取器，用于获取指数和板块数据
        """
        self.data_fetcher = data_fetcher
    
    def score(self, stock_data: pd.DataFrame, sector: Optional[str] = None) -> MarketScore:
        """
        计算市场环境评分
        
        Args:
            stock_data: 股票数据（用于获取日期范围）
            sector: 股票所属板块
            
        Returns:
            MarketScore: 市场环境评分对象
        """
        score = 50  # 基础分
        reasons = []
        indicators = {}
        
        # 1. 大盘状态（50 分）
        index_score, index_reasons, index_indicators = self._score_index(stock_data)
        score += index_score
        reasons.extend(index_reasons)
        indicators.update(index_indicators)
        
        # 2. 板块表现（30 分）
        if sector and self.data_fetcher:
            sector_score, sector_reasons, sector_indicators = self._score_sector(stock_data, sector)
            score += sector_score
            reasons.extend(sector_reasons)
            indicators.update(sector_indicators)
        
        # 3. 市场成交量（20 分）
        volume_score, volume_reasons, volume_indicators = self._score_market_volume(stock_data)
        score += volume_score
        reasons.extend(volume_reasons)
        indicators.update(volume_indicators)
        
        # 限制评分范围 [0, 100]
        score = max(0, min(100, score))
        
        return MarketScore(
            value=score,
            reasons=reasons,
            indicators=indicators
        )
    
    def _score_index(self, stock_data: pd.DataFrame) -> Tuple[float, List[str], Dict[str, Any]]:
        """评分大盘状态"""
        score = 0
        reasons = []
        indicators = {}
        
        if not self.data_fetcher:
            return score, reasons, indicators
        
        try:
            # 获取上证指数数据（最近 60 天）
            end_date = stock_data.iloc[-1]['date']
            start_date = stock_data.iloc[max(0, len(stock_data) - 60)]['date']
            
            index_data = self.data_fetcher.get_daily_data('sh.000001', start_date, end_date)
            
            if len(index_data) < 20:
                return score, reasons, indicators
            
            # 计算均线
            index_data = self._calculate_ma(index_data)
            
            latest = index_data.iloc[-1]
            index_price = latest['close']
            index_ma20 = latest['ma20']
            index_ma60 = latest['ma60']
            
            indicators['index_price'] = float(index_price)
            indicators['index_ma20'] = float(index_ma20) if pd.notna(index_ma20) else None
            
            # 检查大盘与均线关系
            if pd.notna(index_ma20):
                if index_price > index_ma20:
                    score += 25
                    reasons.append("大盘站上 20 日均线，市场环境良好")
                else:
                    score -= 20
                    reasons.append("大盘跌破 20 日均线，市场环境偏弱")
            
            # 检查均线排列
            if pd.notna(index_ma20) and pd.notna(index_ma60):
                if index_ma20 > index_ma60:
                    score += 15
                    reasons.append("大盘均线多头排列")
                else:
                    score -= 10
                    reasons.append("大盘均线空头排列")
        
        except Exception as e:
            # 如果获取指数数据失败，返回中性评分
            pass
        
        return score, reasons, indicators
    
    def _score_sector(self, stock_data: pd.DataFrame, sector: str) -> Tuple[float, List[str], Dict[str, Any]]:
        """评分板块表现"""
        score = 0
        reasons = []
        indicators = {}
        
        if not self.data_fetcher:
            return score, reasons, indicators
        
        try:
            # 获取板块数据（最近 20 天）
            end_date = stock_data.iloc[-1]['date']
            start_date = stock_data.iloc[max(0, len(stock_data) - 20)]['date']
            
            sector_data = self.data_fetcher.get_sector_data(sector, start_date, end_date)
            
            if len(sector_data) < 20:
                return score, reasons, indicators
            
            # 计算板块涨跌幅
            sector_start_price = sector_data.iloc[0]['close']
            sector_end_price = sector_data.iloc[-1]['close']
            sector_change = (sector_end_price - sector_start_price) / sector_start_price
            
            indicators['sector_change'] = float(sector_change)
            
            if sector_change > 0.05:  # 板块上涨 5% 以上
                score += 25
                reasons.append(f"{sector}板块近期上涨 {sector_change*100:.1f}%，板块强势")
            elif sector_change < -0.05:  # 板块下跌 5% 以上
                score -= 20
                reasons.append(f"{sector}板块近期下跌 {sector_change*100:.1f}%，板块疲弱")
        
        except Exception as e:
            # 如果获取板块数据失败，返回中性评分
            indicators['sector_change'] = None
        
        return score, reasons, indicators
    
    def _score_market_volume(self, stock_data: pd.DataFrame) -> Tuple[float, List[str], Dict[str, Any]]:
        """评分市场成交量"""
        score = 0
        reasons = []
        indicators = {}
        
        if not self.data_fetcher:
            return score, reasons, indicators
        
        try:
            # 获取上证指数数据
            end_date = stock_data.iloc[-1]['date']
            start_date = stock_data.iloc[max(0, len(stock_data) - 20)]['date']
            
            index_data = self.data_fetcher.get_daily_data('sh.000001', start_date, end_date)
            
            if len(index_data) < 20:
                return score, reasons, indicators
            
            # 计算市场成交量比率
            recent_20 = index_data.tail(20)
            avg_market_volume = recent_20['volume'].mean()
            market_volume = index_data.iloc[-1]['volume']
            
            if avg_market_volume > 0:
                volume_ratio = market_volume / avg_market_volume
                indicators['market_volume_ratio'] = float(volume_ratio)
                
                if volume_ratio > 1.2:
                    score += 15
                    reasons.append("市场成交量放大，资金活跃")
                elif volume_ratio < 0.8:
                    score -= 10
                    reasons.append("市场成交量萎缩，观望情绪浓厚")
        
        except Exception as e:
            # 如果获取数据失败，返回中性评分
            indicators['market_volume_ratio'] = None
        
        return score, reasons, indicators
    
    def _calculate_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算均线"""
        df = df.copy()
        
        if 'ma20' not in df.columns:
            df['ma20'] = df['close'].rolling(window=20).mean()
        if 'ma60' not in df.columns:
            df['ma60'] = df['close'].rolling(window=60).mean()
        
        return df
