"""
信号灯评估器

基于综合评分和风险因素生成红绿灯建议。
"""

from .models import SignalLight, TechnicalScore, LiquidityScore, MarketScore, RiskInfo


class SignalLightEvaluator:
    """信号灯评估器"""
    
    def evaluate(
        self,
        overall_score: float,
        technical_score: TechnicalScore,
        liquidity_score: LiquidityScore,
        market_score: MarketScore,
        risk_info: RiskInfo
    ) -> SignalLight:
        """
        生成信号灯评价
        
        Args:
            overall_score: 综合评分
            technical_score: 技术面评分
            liquidity_score: 流动性评分
            market_score: 市场环境评分
            risk_info: 风险信息
            
        Returns:
            SignalLight: 信号灯对象（RED/YELLOW/GREEN）
        """
        # 1. 强制红灯条件（一票否决）
        forced_red = self._check_forced_red(risk_info, liquidity_score)
        if forced_red:
            return forced_red
        
        # 2. 基于综合评分判断
        if overall_score >= 70:
            # 绿灯：建议关注或买入
            confidence = min(100, overall_score)
            return SignalLight(
                color="GREEN",
                label="可以关注",
                reason=self._generate_green_reason(technical_score, liquidity_score, market_score),
                confidence=confidence
            )
        
        elif overall_score >= 40:
            # 黄灯：建议观望
            confidence = overall_score
            return SignalLight(
                color="YELLOW",
                label="建议观望",
                reason=self._generate_yellow_reason(technical_score, liquidity_score, market_score),
                confidence=confidence
            )
        
        else:
            # 红灯：建议回避或卖出
            confidence = 100 - overall_score
            return SignalLight(
                color="RED",
                label="建议回避",
                reason=self._generate_red_reason(technical_score, liquidity_score, market_score),
                confidence=confidence
            )
    
    def _check_forced_red(self, risk_info: RiskInfo, liquidity_score: LiquidityScore) -> SignalLight:
        """检查强制红灯条件"""
        # ST 股票
        if risk_info.is_st_stock:
            return SignalLight(
                color="RED",
                label="建议回避",
                reason="ST 股票存在退市风险，不建议操作",
                confidence=0
            )
        
        # 流动性严重不足
        if liquidity_score.value < 30:
            return SignalLight(
                color="RED",
                label="建议回避",
                reason="流动性严重不足，可能难以卖出",
                confidence=0
            )
        
        # 连续亏损
        if risk_info.consecutive_losses >= 2:
            return SignalLight(
                color="RED",
                label="建议回避",
                reason="公司连续亏损，财务风险高",
                confidence=0
            )
        
        return None
    
    def _generate_green_reason(
        self,
        technical: TechnicalScore,
        liquidity: LiquidityScore,
        market: MarketScore
    ) -> str:
        """生成绿灯理由"""
        reasons = []
        
        if technical.value >= 70:
            reasons.append("技术形态良好")
        
        if liquidity.value >= 60:
            reasons.append("流动性充足")
        
        if market.value >= 60:
            reasons.append("市场环境支持")
        
        if not reasons:
            reasons.append("综合评分较高")
        
        return "，".join(reasons) + "，可以考虑关注"
    
    def _generate_yellow_reason(
        self,
        technical: TechnicalScore,
        liquidity: LiquidityScore,
        market: MarketScore
    ) -> str:
        """生成黄灯理由"""
        weak_points = []
        
        if technical.value < 60:
            weak_points.append("技术面偏弱")
        
        if liquidity.value < 50:
            weak_points.append("流动性一般")
        
        if market.value < 50:
            weak_points.append("市场环境不佳")
        
        if not weak_points:
            weak_points.append("综合评分中等")
        
        return "，".join(weak_points) + "，建议等待更好的时机"
    
    def _generate_red_reason(
        self,
        technical: TechnicalScore,
        liquidity: LiquidityScore,
        market: MarketScore
    ) -> str:
        """生成红灯理由"""
        problems = []
        
        if technical.value < 40:
            problems.append("技术形态破坏")
        
        if liquidity.value < 40:
            problems.append("流动性不足")
        
        if market.value < 40:
            problems.append("市场环境恶劣")
        
        if not problems:
            problems.append("综合评分较低")
        
        return "，".join(problems) + "，不建议操作"
