"""
大白话生成器

将技术指标转换为普通人能理解的自然语言。
"""

import pandas as pd
from .models import TechnicalScore, LiquidityScore, MarketScore, SignalLight


class PlainLanguageGenerator:
    """大白话生成器"""
    
    def generate(
        self,
        stock_data: pd.DataFrame,
        name: str,
        technical_score: TechnicalScore,
        liquidity_score: LiquidityScore,
        market_score: MarketScore,
        signal_light: SignalLight
    ) -> str:
        """
        生成大白话诊断意见
        
        Args:
            stock_data: 股票数据
            name: 股票名称
            technical_score: 技术面评分
            liquidity_score: 流动性评分
            market_score: 市场环境评分
            signal_light: 信号灯
            
        Returns:
            str: 大白话诊断文本
        """
        sections = []
        
        # 1. 开场白（基于信号灯）
        opening = self._generate_opening(name, signal_light)
        sections.append(opening)
        
        # 2. 技术面描述
        tech_text = self._describe_technical(technical_score, stock_data)
        sections.append(tech_text)
        
        # 3. 资金面描述
        liquidity_text = self._describe_liquidity(liquidity_score, stock_data)
        sections.append(liquidity_text)
        
        # 4. 市场环境描述
        market_text = self._describe_market(market_score)
        sections.append(market_text)
        
        # 5. 建议操作
        suggestion = self._generate_suggestion(signal_light, technical_score, liquidity_score)
        sections.append(suggestion)
        
        return "\n\n".join(sections)
    
    def _generate_opening(self, name: str, signal_light: SignalLight) -> str:
        """生成开场白"""
        if signal_light.color == "GREEN":
            return f"从客观数据看，{name}目前表现不错。"
        elif signal_light.color == "YELLOW":
            return f"从客观数据看，{name}目前处于观望期。"
        else:
            return f"从客观数据看，{name}目前存在一些问题。"
    
    def _describe_technical(self, technical_score: TechnicalScore, stock_data: pd.DataFrame) -> str:
        """描述技术面"""
        latest = stock_data.iloc[-1]
        current_price = latest['close']
        
        indicators = technical_score.indicators
        volume_ratio = indicators.get('volume_ratio', 1.0)
        ma5 = indicators.get('ma5')
        ma20 = indicators.get('ma20')
        
        if technical_score.value >= 70:
            if volume_ratio and volume_ratio > 2.0:
                return f"技术面上，股价目前是 {current_price:.2f} 元，短期均线（{ma5:.2f}）已经突破长期均线（{ma20:.2f}），而且成交量突然放大了 {volume_ratio:.1f} 倍，说明有资金在进场。"
            else:
                return f"技术面上，股价目前是 {current_price:.2f} 元，均线呈现多头排列，趋势向上，形态比较健康。"
        
        elif technical_score.value < 40:
            if volume_ratio and volume_ratio < 0.5:
                return f"技术面上，股价目前是 {current_price:.2f} 元，短期均线（{ma5:.2f}）已经跌破长期均线（{ma20:.2f}），而且成交量严重萎缩，资金在流出。"
            else:
                return f"技术面上，股价目前是 {current_price:.2f} 元，均线呈现空头排列，趋势向下，形态已经破坏。"
        
        else:
            return f"技术面上，股价目前是 {current_price:.2f} 元，处于横盘整理状态，方向还不明确。"
    
    def _describe_liquidity(self, liquidity_score: LiquidityScore, stock_data: pd.DataFrame) -> str:
        """描述流动性"""
        indicators = liquidity_score.indicators
        avg_amount = indicators.get('avg_amount_20', 0)
        turnover = indicators.get('turnover_rate', 0)
        
        if liquidity_score.value >= 60:
            return f"资金面上，这只股票日均成交额有 {avg_amount/100_000_000:.1f} 亿，换手率 {turnover:.2f}%，流动性不错，买卖都比较方便。"
        
        elif liquidity_score.value < 40:
            return f"资金面上，这只股票日均成交额只有 {avg_amount/100_000_000:.2f} 亿，换手率 {turnover:.2f}%，流动性不太好，可能不容易卖出去。"
        
        else:
            return f"资金面上，这只股票日均成交额 {avg_amount/100_000_000:.1f} 亿，流动性一般。"
    
    def _describe_market(self, market_score: MarketScore) -> str:
        """描述市场环境"""
        if market_score.value >= 60:
            return "市场环境方面，大盘目前比较稳定，整体环境还不错。"
        elif market_score.value < 40:
            return "市场环境方面，大盘目前比较弱，整体环境不太好，建议谨慎。"
        else:
            return "市场环境方面，大盘目前震荡，没有明确方向。"
    
    def _generate_suggestion(
        self,
        signal_light: SignalLight,
        technical_score: TechnicalScore,
        liquidity_score: LiquidityScore
    ) -> str:
        """生成建议"""
        if signal_light.color == "GREEN":
            if technical_score.value >= 80 and liquidity_score.value >= 60:
                return "综合来看，这只股票目前符合我们的选股标准，可以考虑小仓位试探。但记得设好止损，控制风险。"
            else:
                return "综合来看，这只股票目前还可以，可以加入自选继续观察，等待更好的买入时机。"
        
        elif signal_light.color == "YELLOW":
            return "综合来看，这只股票目前还不够明确，建议先观望，等趋势更清晰再做决定。"
        
        else:
            if liquidity_score.value < 40:
                return "综合来看，这只股票目前不太适合操作，特别是流动性不足，建议回避。"
            else:
                return "综合来看，这只股票目前风险较大，不建议操作。如果已经持有，建议考虑止损。"
