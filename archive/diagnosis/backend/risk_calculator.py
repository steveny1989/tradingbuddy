"""
风险计算器

计算止损止盈价位和风险等级。
"""

import numpy as np
import pandas as pd
from typing import List
from .models import RiskInfo


class RiskCalculator:
    """风险计算器"""
    
    def __init__(self, financial_fetcher=None):
        """
        初始化风险计算器
        
        Args:
            financial_fetcher: 财务数据获取器，用于检查连续亏损等财务风险
        """
        self.financial_fetcher = financial_fetcher
    
    def calculate(self, stock_data: pd.DataFrame, code: str, name: str) -> RiskInfo:
        """
        计算风险信息
        
        Args:
            stock_data: 股票数据
            code: 股票代码
            name: 股票名称
            
        Returns:
            RiskInfo: 风险信息对象
        """
        latest = stock_data.iloc[-1]
        current_price = latest['close']
        
        # 1. 计算波动率（用于调整止损止盈）
        volatility = self._calculate_volatility(stock_data)
        
        # 2. 根据波动率调整止损止盈比例
        stop_loss_pct, take_profit_pct, risk_level = self._adjust_risk_params(volatility)
        
        # 3. 计算具体价位
        stop_loss_price = current_price * (1 + stop_loss_pct)
        take_profit_price = current_price * (1 + take_profit_pct)
        
        # 4. 计算盈亏比
        risk_reward_ratio = abs(take_profit_pct / stop_loss_pct)
        
        # 5. 检查风险因素
        is_st_stock = self._check_st_stock(name)
        consecutive_losses = self._check_consecutive_losses(code)
        has_major_litigation = self._check_litigation(code)
        
        # 6. 生成风险警告
        warnings = self._generate_warnings(
            is_st_stock, consecutive_losses, has_major_litigation, volatility
        )
        
        # 7. 调整风险等级
        if is_st_stock or consecutive_losses >= 2:
            risk_level = "EXTREME"
            # ST 股票使用更严格的止损
            stop_loss_pct = -0.05
            stop_loss_price = current_price * (1 + stop_loss_pct)
        
        return RiskInfo(
            current_price=current_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            risk_reward_ratio=risk_reward_ratio,
            volatility=volatility,
            risk_level=risk_level,
            is_st_stock=is_st_stock,
            consecutive_losses=consecutive_losses,
            has_major_litigation=has_major_litigation,
            warnings=warnings
        )
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """计算年化波动率"""
        # 使用最近 60 天的数据计算波动率
        recent_60 = df.tail(60)
        if len(recent_60) < 30:
            return 0.3  # 默认中等波动率
        
        # 计算日收益率
        returns = recent_60['close'].pct_change().dropna()
        
        if len(returns) == 0:
            return 0.3
        
        # 计算年化波动率（假设一年 252 个交易日）
        volatility = returns.std() * np.sqrt(252)
        
        return float(volatility)
    
    def _adjust_risk_params(self, volatility: float) -> tuple:
        """根据波动率调整止损止盈比例"""
        if volatility > 0.5:  # 高波动
            stop_loss_pct = -0.10  # -10%
            take_profit_pct = 0.20  # +20%
            risk_level = "HIGH"
        elif volatility > 0.3:  # 中等波动
            stop_loss_pct = -0.08  # -8%
            take_profit_pct = 0.15  # +15%
            risk_level = "MEDIUM"
        else:  # 低波动
            stop_loss_pct = -0.06  # -6%
            take_profit_pct = 0.12  # +12%
            risk_level = "LOW"
        
        return stop_loss_pct, take_profit_pct, risk_level
    
    def _check_st_stock(self, name: str) -> bool:
        """检查是否为 ST 股票"""
        if not name:
            return False
        
        # 检查股票名称是否包含 ST 或 *ST
        return name.startswith("ST") or name.startswith("*ST") or "ST" in name
    
    def _check_consecutive_losses(self, code: str) -> int:
        """检查连续亏损年数"""
        if not self.financial_fetcher:
            return 0
        
        try:
            # 获取最近 3 年的利润数据
            income_data = self.financial_fetcher.get_income_statement(code, years=3)
            
            if income_data is None or len(income_data) == 0:
                return 0
            
            # 按报告日期排序（降序）
            income_data = income_data.sort_values('report_date', ascending=False)
            
            # 统计连续亏损年数
            consecutive_losses = 0
            for _, row in income_data.iterrows():
                net_profit = row.get('net_profit', 0) or row.get('net_profit_parent', 0)
                if net_profit < 0:
                    consecutive_losses += 1
                else:
                    break
            
            return consecutive_losses
        
        except Exception as e:
            return 0
    
    def _check_litigation(self, code: str) -> bool:
        """检查是否有重大诉讼"""
        # 这个功能需要额外的数据源，暂时返回 False
        # 未来可以接入公告数据或第三方数据源
        return False
    
    def _generate_warnings(
        self,
        is_st_stock: bool,
        consecutive_losses: int,
        has_major_litigation: bool,
        volatility: float
    ) -> List[str]:
        """生成风险警告列表"""
        warnings = []
        
        if is_st_stock:
            warnings.append("高风险预警：该股票为 ST 股，存在退市风险")
        
        if consecutive_losses >= 2:
            warnings.append(f"财务风险：公司连续 {consecutive_losses} 年亏损")
        elif consecutive_losses == 1:
            warnings.append("财务风险：公司上一年度亏损")
        
        if has_major_litigation:
            warnings.append("法律风险：公司存在重大诉讼")
        
        if volatility > 0.6:
            warnings.append(f"波动风险：股价波动率较高（{volatility*100:.1f}%），注意控制仓位")
        
        return warnings
