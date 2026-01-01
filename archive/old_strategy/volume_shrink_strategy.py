#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缩量三连跌策略（稳健版）
Volume Shrink Three-Day Decline Strategy (Risk-Controlled Version)

优化要点：
1. 流动性过滤：剔除ST股，要求日均成交额>1亿
2. 市场环境过滤：仅在大盘20日均线以上开仓
3. 量能逻辑修正：下跌后放量企稳（而非盲目缩量）
4. 强制平仓：3天不反弹强制出局
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from strategy.base import TechnicalStrategy

logger = logging.getLogger(__name__)


class VolumeShrinkStrategy(TechnicalStrategy):
    """缩量三连跌选股策略（稳健版）"""
    
    def __init__(self, db, market_index_code: str = 'sh.000001', min_avg_turnover: float = 1e8):
        """
        初始化策略
        
        Args:
            db: StockDatabase 实例
            market_index_code: 大盘指数代码（默认上证指数）
            min_avg_turnover: 最小日均成交额（默认1亿）
        """
        super().__init__(db)
        self.name = "缩量三连跌（稳健版）"
        self.market_index_code = market_index_code
        self.min_avg_turnover = min_avg_turnover
        
    def get_stock_pool(
        self, 
        min_cap: float = 50e8,  # 50亿
        max_cap: float = 200e8,  # 200亿
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
            # 从市值表获取符合条件的股票
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
    
    def check_market_filter(self, date: str = None) -> bool:
        """
        检查市场环境过滤器（大盘20日均线）
        
        Args:
            date: 检查日期（None表示最新）
            
        Returns:
            True表示可以开仓（大盘在20日均线以上）
        """
        try:
            # 获取大盘指数数据
            if date:
                # 获取date之前的30天数据（确保有足够数据计算20日均线）
                from datetime import datetime, timedelta
                end_date = datetime.strptime(date, '%Y-%m-%d')
                start_date = (end_date - timedelta(days=40)).strftime('%Y-%m-%d')
                df = self.db.get_daily_data(self.market_index_code, start_date=start_date, end_date=date)
            else:
                df = self.db.get_daily_data(self.market_index_code)
            
            if df.empty or len(df) < 20:
                logger.warning(f"大盘数据不足，无法计算20日均线")
                return True  # 数据不足时默认通过
            
            # 计算20日均线
            df = df.sort_values('date')
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            # 获取最新数据
            latest = df.iloc[-1]
            
            if pd.isna(latest['ma20']):
                return True
            
            # 判断是否在均线以上
            is_above_ma = latest['close'] > latest['ma20']
            
            logger.debug(f"{latest['date']} 大盘: {latest['close']:.2f}, MA20: {latest['ma20']:.2f}, 通过: {is_above_ma}")
            
            return is_above_ma
            
        except Exception as e:
            logger.warning(f"检查市场过滤器失败: {e}")
            return True  # 出错时默认通过
    
    def check_liquidity(self, code: str, date: str = None, days: int = 5, skip_st_check: bool = False) -> bool:
        """
        检查流动性过滤器（仅检查成交额）
        
        Args:
            code: 股票代码
            date: 检查日期（None表示最新）
            days: 计算日均成交额的天数
            skip_st_check: 是否跳过ST股检查（如果已在外部检查过）
            
        Returns:
            True表示通过流动性检查
        """
        try:
            # ST股检查（如果需要）
            if not skip_st_check:
                stock_info = self.db.conn.execute(
                    "SELECT name FROM stock_basic WHERE code = ?",
                    (code,)
                ).fetchone()
                
                if stock_info:
                    name = stock_info[0]
                    if 'ST' in name or 'st' in name:
                        logger.debug(f"{code} {name}: ST股，过滤")
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
            
            passed = avg_turnover >= self.min_avg_turnover
            
            if not passed:
                logger.debug(f"{code}: 日均成交额 {avg_turnover/1e8:.2f}亿 < {self.min_avg_turnover/1e8:.2f}亿")
            
            return passed
            
        except Exception as e:
            logger.debug(f"检查流动性失败 {code}: {e}")
            return False
    
    def check_signal(
        self,
        code: str,
        date: str = None,
        min_decline: float = 0.10,  # 最小跌幅10%
        check_reversal: bool = True,  # 是否检查起跌转折
        use_volume_stabilize: bool = True  # 使用"放量企稳"逻辑
    ) -> Optional[Dict]:
        """
        检查单只股票是否满足策略条件（稳健版）
        
        策略条件（稳健版）:
        1. 下跌: P0 < P3（最新价低于3天前）
        2. 放量企稳: V0 > V1（最新成交量放大，表示有资金进场）
        3. 跌幅: (P0 - P3) / P3 <= -min_decline
        4. 可选: 起跌转折 P3 > P4
        
        原版条件（激进版）:
        1. 三连跌: P0 < P1 < P2 < P3
        2. 缩量: V0 < V1 < V2
        3. 跌幅: (P0 - P3) / P3 <= -min_decline
        4. 可选: 起跌转折 P3 > P4
        
        Args:
            code: 股票代码
            date: 检查日期（None表示最新）
            min_decline: 最小跌幅
            check_reversal: 是否检查起跌转折
            use_volume_stabilize: 是否使用"放量企稳"逻辑（稳健版）
            
        Returns:
            信号字典，如果不满足条件返回None
        """
        try:
            # 获取历史数据
            if date:
                df = self.db.get_daily_data(code, end_date=date)
                if df.empty or df['date'].max() != date:
                    return None
                df = df.tail(5)  # 最近5天
            else:
                df = self.db.get_daily_data(code)
                if df.empty:
                    return None
                df = df.tail(5)
            
            if len(df) < 4:
                return None
            
            # 按日期排序（从旧到新）
            df = df.sort_values('date')
            
            # 提取价格和成交量
            prices = df['close'].values
            volumes = df['volume'].values
            dates = df['date'].values
            
            # 检查数据有效性
            if any(pd.isna(prices)) or any(pd.isna(volumes)):
                return None
            
            if use_volume_stabilize:
                # 稳健版逻辑：下跌后放量企稳
                # 条件1: 下跌 (P0 < P3)
                if not (prices[-1] < prices[-4]):
                    return None
                
                # 条件2: 放量企稳 (V0 > V1，表示有资金进场托底)
                if not (volumes[-1] > volumes[-2]):
                    return None
                
                # 额外检查：确保是真正的放量（至少放大10%）
                volume_increase = (volumes[-1] - volumes[-2]) / volumes[-2]
                if volume_increase < 0.1:
                    return None
            else:
                # 原版逻辑：三连跌缩量
                # 条件1: 三连跌 (P0 < P1 < P2 < P3)
                # 注意: prices[-1]是最新的，prices[0]是最旧的
                if not (prices[-1] < prices[-2] < prices[-3] < prices[-4]):
                    return None
                
                # 条件2: 缩量 (V0 < V1 < V2)
                if not (volumes[-1] < volumes[-2] < volumes[-3]):
                    return None
            
            # 条件3: 跌幅检查
            decline_rate = (prices[-1] - prices[-4]) / prices[-4]
            if decline_rate > -min_decline:
                return None
            
            # 条件4: 可选的起跌转折检查
            if check_reversal and len(prices) >= 5:
                if prices[-4] <= prices[-5]:  # P3 应该 > P4
                    return None
            
            # 构建信号
            signal = {
                'code': code,
                'date': dates[-1],
                'price': prices[-1],
                'decline_rate': decline_rate,
                'decline_days': 3,
                'volume_shrink': not use_volume_stabilize,
                'volume_stabilize': use_volume_stabilize,
                'p0': prices[-1],
                'p1': prices[-2],
                'p2': prices[-3],
                'p3': prices[-4],
                'v0': volumes[-1],
                'v1': volumes[-2],
                'v2': volumes[-3],
            }
            
            if len(prices) >= 5:
                signal['p4'] = prices[-5]
                signal['reversal'] = prices[-4] > prices[-5]
            
            return signal
            
        except Exception as e:
            logger.debug(f"检查 {code} 失败: {e}")
            return None
    
    def scan(
        self,
        date: str = None,
        min_cap: float = 50e8,
        max_cap: float = 200e8,
        min_decline: float = 0.10,
        check_reversal: bool = True,
        max_stocks: int = None,
        use_volume_stabilize: bool = True,
        check_market: bool = True,
        check_liquidity_filter: bool = True
    ) -> pd.DataFrame:
        """
        扫描股票池，找出符合条件的股票（稳健版 + 性能优化）
        
        Args:
            date: 扫描日期（None表示最新）
            min_cap: 最小市值
            max_cap: 最大市值
            min_decline: 最小跌幅
            check_reversal: 是否检查起跌转折
            max_stocks: 最多扫描股票数（用于测试）
            use_volume_stabilize: 是否使用"放量企稳"逻辑
            check_market: 是否检查市场环境（大盘20日均线）
            check_liquidity_filter: 是否检查流动性（ST股、成交额）
            
        Returns:
            信号列表 DataFrame
        """
        # 检查市场环境
        if check_market:
            if not self.check_market_filter(date):
                logger.warning(f"{date or '最新'}: 大盘未在20日均线以上，不开仓")
                return pd.DataFrame()
        
        # 获取股票池
        pool = self.get_stock_pool(min_cap, max_cap)
        
        if pool.empty:
            logger.warning("股票池为空")
            return pd.DataFrame()
        
        if max_stocks:
            pool = pool.head(max_stocks)
        
        logger.info(f"开始扫描 {len(pool)} 只股票...")
        
        signals = []
        scanned = 0
        filtered_st = 0
        filtered_liquidity = 0
        
        for idx, row in pool.iterrows():
            code = row['full_code']
            scanned += 1
            
            # 流动性过滤
            if check_liquidity_filter:
                # ST股过滤（快速检查，避免数据库查询）
                if 'ST' in row['name'] or 'st' in row['name']:
                    filtered_st += 1
                    continue
                
                # 成交额过滤（跳过ST检查，因为已在上面检查过）
                if not self.check_liquidity(code, date, skip_st_check=True):
                    filtered_liquidity += 1
                    continue
            
            signal = self.check_signal(
                code=code,
                date=date,
                min_decline=min_decline,
                check_reversal=check_reversal,
                use_volume_stabilize=use_volume_stabilize
            )
            
            if signal:
                # 添加股票基本信息
                signal['name'] = row['name']
                signal['market_cap'] = row['total_cap'] / 1e8  # 转换为亿
                signals.append(signal)
            
            # 进度提示
            if scanned % 100 == 0:
                logger.info(f"已扫描 {scanned}/{len(pool)}, 找到 {len(signals)} 个信号 (过滤: ST={filtered_st}, 流动性={filtered_liquidity})")
        
        logger.info(f"扫描完成: {len(signals)} 个信号 (总扫描={scanned}, ST过滤={filtered_st}, 流动性过滤={filtered_liquidity})")
        
        if not signals:
            return pd.DataFrame()
        
        # 转换为DataFrame
        df_signals = pd.DataFrame(signals)
        
        # 按跌幅排序
        df_signals = df_signals.sort_values('decline_rate')
        
        return df_signals
