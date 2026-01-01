#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略基类
定义所有策略必须实现的统一接口
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Optional


class BaseStrategy(ABC):
    """策略基类 - 所有策略必须继承此类"""
    
    def __init__(self, db, **kwargs):
        """
        初始化策略
        
        Args:
            db: StockDatabase实例
            **kwargs: 策略特定参数
        """
        self.db = db
        self.name = "未命名策略"
    
    @abstractmethod
    def get_stock_pool(
        self, 
        min_cap: float = 50e8,
        max_cap: float = 200e8,
        markets: List[str] = ['sh', 'sz']
    ) -> pd.DataFrame:
        """
        获取股票池（按市值筛选）
        
        Args:
            min_cap: 最小市值（元）
            max_cap: 最大市值（元）
            markets: 市场列表
            
        Returns:
            股票池 DataFrame，必须包含列：full_code, code, name
        """
        pass
    
    @abstractmethod
    def check_signal(
        self,
        code: str,
        date: str = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        检查单只股票是否满足策略条件
        
        Args:
            code: 股票代码
            date: 检查日期（None表示最新）
            **kwargs: 策略特定参数
            
        Returns:
            信号字典，如果不满足条件返回None
            信号字典必须包含：
            - code: 股票代码
            - date: 信号日期
            - price: 当前价格
        """
        pass
    
    @abstractmethod
    def scan(
        self,
        date: str = None,
        min_cap: float = 50e8,
        max_cap: float = 200e8,
        max_stocks: int = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        扫描股票池，找出符合条件的股票
        
        Args:
            date: 扫描日期（None表示最新）
            min_cap: 最小市值
            max_cap: 最大市值
            max_stocks: 最多扫描股票数（用于测试）
            **kwargs: 策略特定参数
            
        Returns:
            信号列表 DataFrame，必须包含列：
            - code: 股票代码
            - name: 股票名称
            - date: 信号日期
            - price: 当前价格
        """
        pass
    
    def __str__(self):
        """字符串表示"""
        return f"{self.name}"
    
    def __repr__(self):
        """调试表示"""
        return f"<{self.__class__.__name__}: {self.name}>"


class TechnicalStrategy(BaseStrategy):
    """技术分析策略基类"""
    
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self.name = "技术分析策略"


class FundamentalStrategy(BaseStrategy):
    """基本面策略基类"""
    
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self.name = "基本面策略"


class QuantStrategy(BaseStrategy):
    """量化策略基类"""
    
    def __init__(self, db, **kwargs):
        super().__init__(db, **kwargs)
        self.name = "量化策略"
