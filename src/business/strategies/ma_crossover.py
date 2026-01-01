#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
均线突破策略
Moving Average Crossover Strategy

策略逻辑：
1. 买入信号：短期均线上穿长期均线（金叉）
2. 卖出信号：短期均线下穿长期均线（死叉）
3. 过滤条件：
   - 成交量放大（当日成交量 > 5日均量）
   - 市值范围：50-200亿
   - 流动性：日均成交额 > 1亿
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from src.business.strategies.base import TechnicalStrategy

logger = logging.getLogger(__name__)


class MACrossoverStrategy(TechnicalStrategy):
    """均线突破策略"""
    
    def __init__(
        self, 
        db,
        short_window: int = 5,
        long_window: int = 20,
        volume_window: int = 5,
        market_index_code: str = 'sh.000001',
        min_avg_turnover: float = 1e8
    ):
        """
        初始化策略
        
        Args:
            db: StockDatabase 实例
            short_window: 短期均线窗口（默认5日）
            long_window: 长期均线窗口（默认20日）
            volume_window: 成交量均线窗口（默认5日）
            market_index_code: 大盘指数代码
            min_avg_turnover: 最小日均成交额
        """
        super().__init__(db)
        self.name = f"均线突破({short_window}/{long_window})"
        self.short_window = short_window
        self.long_window = long_window
        self.volume_window = volume_window
        self.market_index_code = market_index_code
        self.min_avg_turnover = min_avg_turnover
    
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
            股票池 DataFrame
        """
        try:
            query = f"""
                SELECT full_code, code, name, total_cap, cap_category, market
                FROM market_cap_data
                WHERE total_cap >= {min_cap} 
                  AND total_cap <= {max_cap}
                  AND market IN ({','.join([f"'{m}'" for m in markets])})
            """
            pool = pd.read_sql(query, self.db.conn)
            logger.info(f"股票池: {len(pool)} 只股票 (市值 {min_cap/1e8:.0f}-{max_cap/1e8:.0f}亿)")
            return pool
        except Exception as e:
            logger.error(f"获取股票池失败: {e}")
            return pd.DataFrame()
    
    def check_liquidity(self, code: str, date: str = None, days: int = 5) -> bool:
        """
        检查流动性过滤器
        
        Args:
            code: 股票代码
            date: 检查日期
            days: 计算日均成交额的天数
            
        Returns:
            True表示通过流动性检查
        """
        try:
            # 检查是否为ST股
            stock_info = self.db.conn.execute(
                "SELECT name FROM stock_basic WHERE code = ?",
                (code,)
            ).fetchone()
            
            if stock_info:
                name = stock_info[0]
                if 'ST' in name or 'st' in name:
                    return False
            
            # 获取最近N天数据
            if date:
                from datetime import datetime, timedelta
                end_date = datetime.strptime(date, '%Y-%m-%d')
                start_date = (end_date - timedelta(days=days*2)).strftime('%Y-%m-%d')
                df = self.db.get_daily_data(code, start_date=start_date, end_date=date)
            else:
                df = self.db.get_daily_data(code)
            
            if df.empty or len(df) < days:
                return False
            
            # 取最近N天
            df = df.sort_values('date').tail(days)
            
            # 计算日均成交额
            avg_turnover = df['amount'].mean()
            
            return avg_turnover >= self.min_avg_turnover
            
        except Exception as e:
            logger.debug(f"检查流动性失败 {code}: {e}")
            return False
    
    def check_signal(
        self,
        code: str,
        date: str = None,
        check_volume: bool = True
    ) -> Optional[Dict]:
        """
        检查单只股票是否满足策略条件
        
        策略条件:
        1. 金叉: MA5 上穿 MA20
        2. 成交量放大: 当日成交量 > 5日均量
        3. 确认: 前一日MA5 < MA20，当日MA5 > MA20
        
        Args:
            code: 股票代码
            date: 检查日期
            check_volume: 是否检查成交量
            
        Returns:
            信号字典，如果不满足条件返回None
        """
        try:
            # 获取历史数据（需要足够的数据计算均线）
            if date:
                df = self.db.get_daily_data(code, end_date=date)
                if df.empty or df['date'].max() != date:
                    return None
                df = df.tail(self.long_window + 5)  # 多取几天确保数据充足
            else:
                df = self.db.get_daily_data(code)
                if df.empty:
                    return None
                df = df.tail(self.long_window + 5)
            
            if len(df) < self.long_window + 1:
                return None
            
            # 按日期排序
            df = df.sort_values('date')
            
            # 计算均线
            df['ma_short'] = df['close'].rolling(window=self.short_window).mean()
            df['ma_long'] = df['close'].rolling(window=self.long_window).mean()
            df['volume_ma'] = df['volume'].rolling(window=self.volume_window).mean()
            
            # 获取最新两天的数据
            if len(df) < 2:
                return None
            
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # 检查数据有效性
            if pd.isna(today['ma_short']) or pd.isna(today['ma_long']):
                return None
            if pd.isna(yesterday['ma_short']) or pd.isna(yesterday['ma_long']):
                return None
            
            # 条件1: 金叉（前一日MA5 < MA20，今日MA5 > MA20）
            golden_cross = (
                yesterday['ma_short'] < yesterday['ma_long'] and
                today['ma_short'] > today['ma_long']
            )
            
            if not golden_cross:
                return None
            
            # 条件2: 成交量放大（可选）
            if check_volume:
                if pd.isna(today['volume_ma']) or today['volume'] <= today['volume_ma']:
                    return None
            
            # 计算均线距离（衡量信号强度）
            ma_distance = (today['ma_short'] - today['ma_long']) / today['ma_long']
            
            # 构建信号
            signal = {
                'code': code,
                'date': today['date'],
                'price': today['close'],
                'ma_short': today['ma_short'],
                'ma_long': today['ma_long'],
                'ma_distance': ma_distance,
                'volume': today['volume'],
                'volume_ma': today['volume_ma'],
                'volume_ratio': today['volume'] / today['volume_ma'] if today['volume_ma'] > 0 else 0,
                'signal_type': 'golden_cross'
            }
            
            return signal
            
        except Exception as e:
            logger.debug(f"检查 {code} 失败: {e}")
            return None
    
    def scan(
        self,
        date: str = None,
        min_cap: float = 50e8,
        max_cap: float = 200e8,
        check_volume: bool = True,
        check_liquidity_filter: bool = True,
        max_stocks: int = None
    ) -> pd.DataFrame:
        """
        扫描股票池，找出符合条件的股票
        
        Args:
            date: 扫描日期
            min_cap: 最小市值
            max_cap: 最大市值
            check_volume: 是否检查成交量
            check_liquidity_filter: 是否检查流动性
            max_stocks: 最多扫描股票数
            
        Returns:
            信号列表 DataFrame
        """
        # 获取股票池
        pool = self.get_stock_pool(min_cap, max_cap)
        
        if pool.empty:
            logger.warning("股票池为空")
            return pd.DataFrame()
        
        if max_stocks:
            pool = pool.head(max_stocks)
        
        logger.info(f"开始扫描 {len(pool)} 只股票...")
        
        signals = []
        for idx, row in pool.iterrows():
            code = row['full_code']
            
            # 流动性过滤
            if check_liquidity_filter:
                if not self.check_liquidity(code, date):
                    continue
            
            signal = self.check_signal(
                code=code,
                date=date,
                check_volume=check_volume
            )
            
            if signal:
                # 添加股票基本信息
                signal['name'] = row['name']
                signal['market_cap'] = row['total_cap'] / 1e8
                signals.append(signal)
            
            # 进度提示
            if (idx + 1) % 100 == 0:
                logger.info(f"已扫描 {idx + 1}/{len(pool)}, 找到 {len(signals)} 个信号")
        
        logger.info(f"扫描完成: {len(signals)} 个信号")
        
        if not signals:
            return pd.DataFrame()
        
        # 转换为DataFrame
        df_signals = pd.DataFrame(signals)
        
        # 按均线距离排序（信号强度）
        df_signals = df_signals.sort_values('ma_distance', ascending=False)
        
        return df_signals
