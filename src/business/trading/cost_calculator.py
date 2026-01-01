# -*- coding: utf-8 -*-
"""
交易成本计算器
统一处理佣金、滑点、印花税等交易成本
"""
from typing import Dict
from dataclasses import dataclass


@dataclass
class TradingConfig:
    """交易配置基类"""
    commission_rate: float = 0.0003      # 佣金率 0.03%
    slippage_rate: float = 0.001         # 滑点率 0.1%
    stamp_tax_rate: float = 0.001        # 印花税率 0.1%（仅卖出）
    min_commission: float = 5.0          # 最低佣金 5元


class TradingCostCalculator:
    """
    交易成本计算器
    
    统一计算交易成本，避免在回测引擎和模拟盘中重复实现
    
    Example:
        >>> config = TradingConfig(commission_rate=0.0003)
        >>> calculator = TradingCostCalculator(config)
        >>> result = calculator.calculate_cost(price=10.0, shares=1000, is_buy=True)
        >>> print(f"总成本: {result['total_cost']:.2f}")
    """
    
    def __init__(self, config: TradingConfig = None):
        """
        初始化计算器
        
        Args:
            config: 交易配置，None则使用默认配置
        """
        self.config = config or TradingConfig()
    
    def calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> Dict[str, float]:
        """
        计算交易成本
        
        Args:
            price: 委托价格
            shares: 股数（必须是100的整数倍）
            is_buy: True表示买入，False表示卖出
            
        Returns:
            包含以下字段的字典：
            - actual_price: 实际成交价（含滑点）
            - amount: 成交金额
            - commission: 佣金
            - stamp_tax: 印花税（仅卖出时有值）
            - total_cost: 总成本（买入）或实际到手（卖出）
            
        Example:
            买入: total_cost = amount + commission
            卖出: total_cost = amount - commission - stamp_tax
        """
        # 1. 计算滑点后的实际成交价
        if is_buy:
            # 买入时价格上浮
            actual_price = price * (1 + self.config.slippage_rate)
        else:
            # 卖出时价格下滑
            actual_price = price * (1 - self.config.slippage_rate)
        
        # 2. 计算成交金额
        amount = actual_price * shares
        
        # 3. 计算佣金（最低5元）
        commission = max(amount * self.config.commission_rate, 
                        self.config.min_commission)
        
        # 4. 计算印花税（仅卖出时收取）
        stamp_tax = amount * self.config.stamp_tax_rate if not is_buy else 0.0
        
        # 5. 计算总成本
        if is_buy:
            # 买入：需要支付的总金额
            total_cost = amount + commission
        else:
            # 卖出：实际到手的金额
            total_cost = amount - commission - stamp_tax
        
        return {
            'actual_price': actual_price,
            'amount': amount,
            'commission': commission,
            'stamp_tax': stamp_tax,
            'total_cost': total_cost
        }
    
    def calculate_simple_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
        """
        简化版本：直接返回总成本
        
        Args:
            price: 委托价格
            shares: 股数
            is_buy: True表示买入，False表示卖出
            
        Returns:
            总成本（买入）或实际到手（卖出）
        """
        result = self.calculate_cost(price, shares, is_buy)
        return result['total_cost']
