"""
选股策略模块
基于您的Colab代码中的选股逻辑
"""
import sqlite3
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from database import DatabaseManager


class StockStrategy:
    """股票选股策略引擎"""
    
    def __init__(self, db_manager: DatabaseManager, db_name: str):
        self.db_manager = db_manager
        self.db_name = db_name
        self.conn = db_manager.get_connection(db_name)
    
    def get_universe_pool(self, min_cap: float = 5e9, max_cap: float = 20e9) -> pd.DataFrame:
        """获取符合市值条件的股票池
        
        Args:
            min_cap: 最小市值（单位：元，默认50亿）
            max_cap: 最大市值（单位：元，默认200亿）
        
        Returns:
            股票池DataFrame
        """
        try:
            # 尝试关联两张表
            query = """
                SELECT a.code, a.code_name, a.industry, b.`总市值`
                FROM stock_basic_info a
                JOIN stock_market_info b ON a.code = b.`代码`
            """
            df_universe = pd.read_sql(query, self.conn)
        except:
            # 如果JOIN失败，尝试分别读取并手动关联
            df_basic = pd.read_sql("SELECT code, code_name, industry FROM stock_basic_info", self.conn)
            df_market = pd.read_sql("SELECT `代码` as market_code, `总市值` FROM stock_market_info", self.conn)
            
            # 统一代码格式进行关联
            df_basic['pure_code'] = df_basic['code'].str.extract(r'(\d+)')
            df_market['pure_code'] = df_market['market_code'].astype(str).str.extract(r'(\d+)')
            
            df_universe = pd.merge(df_basic, df_market, on='pure_code', how='inner')
        
        # 市值筛选
        df_universe['总市值'] = pd.to_numeric(df_universe['总市值'], errors='coerce')
        df_universe['cap_num'] = df_universe['总市值']
        
        # 自动识别市值单位（如果平均值大于100万，单位是元；否则是亿元）
        avg_val = df_universe['cap_num'].mean()
        if avg_val < 1000000:
            min_cap, max_cap = min_cap / 1e8, max_cap / 1e8
        
        pool = df_universe[
            (df_universe['cap_num'] >= min_cap) & 
            (df_universe['cap_num'] <= max_cap)
        ].copy()
        
        return pool
    
    def reversal_strategy(
        self,
        pool: Optional[pd.DataFrame] = None,
        min_drop_rate: float = 0.07,
        min_days: int = 5
    ) -> pd.DataFrame:
        """起跌转折 + 缩量三连跌策略
        
        策略逻辑：
        1. 起跌转折：P(T-3) > P(T-4) - 必须是从涨转跌
        2. 三连跌：P(T) < P(T-1) < P(T-2) < P(T-3)
        3. 缩量：V(T) < V(T-1) < V(T-2)
        4. 跌幅限制：(P(T) - P(T-3)) / P(T-3) <= -min_drop_rate
        
        Args:
            pool: 股票池，如果为None则使用默认市值筛选
            min_drop_rate: 最小跌幅比例（默认7%）
            min_days: 需要的最少交易日数据
        
        Returns:
            符合条件的股票列表
        """
        if pool is None:
            pool = self.get_universe_pool()
        
        hits = []
        print(f"🔍 正在扫描 {len(pool)} 只股票，执行【起跌转折+缩量三连跌】策略...")
        
        for _, row in pool.iterrows():
            code = row['code']
            table_name = f"hist_{code.replace('.', '_')}"
            
            try:
                # 提取最近几天的数据（按日期倒序）
                df_h = pd.read_sql(
                    f"SELECT date, close, volume FROM `{table_name}` ORDER BY date DESC LIMIT {min_days}",
                    self.conn
                )
                
                if len(df_h) < min_days:
                    continue
                
                # 强制类型转换
                p = df_h['close'].astype(float).values  # 0:T(最新), 1:T-1, 2:T-2, 3:T-3, 4:T-4
                v = df_h['volume'].astype(float).values  # 0:T, 1:T-1, 2:T-2
                
                # 策略条件判断
                # 1. 起跌转折：P(T-3) > P(T-4)
                if len(p) < 5:
                    continue
                cond_reversal = p[3] > p[4]
                
                # 2. 三连跌：P(T) < P(T-1) < P(T-2) < P(T-3)
                cond_price = (p[0] < p[1]) and (p[1] < p[2]) and (p[2] < p[3])
                
                # 3. 缩量：V(T) < V(T-1) < V(T-2)
                cond_volume = (v[0] < v[1]) and (v[1] < v[2])
                
                # 4. 跌幅限制
                drop_rate = (p[0] - p[3]) / p[3]
                cond_drop = drop_rate <= -min_drop_rate
                
                if cond_reversal and cond_price and cond_volume and cond_drop:
                    hits.append({
                        '代码': code,
                        '名称': row.get('code_name', ''),
                        '行业': row.get('industry', ''),
                        '最新价': round(p[0], 2),
                        'T-3起跌价': round(p[3], 2),
                        'T-4起涨价': round(p[4], 2),
                        '三日累跌': f"{drop_rate:.2%}",
                        '最新成交量': int(v[0]),
                        '市值(亿)': round(row.get('cap_num', 0) / 1e8, 2),
                        '触发日期': df_h['date'].iloc[0]
                    })
            except Exception:
                continue
        
        return pd.DataFrame(hits)
    
    def long_term_bottom_strategy(
        self,
        pool: Optional[pd.DataFrame] = None,
        lookback_days: int = 500,
        max_drop_from_high: float = 0.40,  # 距高点跌幅>=60%
        max_rise_from_low: float = 1.20,   # 距低点涨幅<=20%
        min_days: int = 250
    ) -> pd.DataFrame:
        """长线底部策略
        
        策略逻辑：
        1. 长线超跌：当前价 / 2年最高价 <= max_drop_from_high
        2. 底部区域：当前价 / 2年最低价 <= max_rise_from_low
        
        Args:
            pool: 股票池
            lookback_days: 回看天数（默认500天，约2年）
            max_drop_from_high: 距最高点最大比例（默认0.4，即跌幅>=60%）
            max_rise_from_low: 距最低点最大比例（默认1.2，即涨幅<=20%）
            min_days: 最少需要的历史数据天数
        
        Returns:
            符合条件的股票列表
        """
        if pool is None:
            pool = self.get_universe_pool()
        
        hits = []
        print(f"🔍 正在扫描 {len(pool)} 只股票，执行【长线底部】策略...")
        
        for _, row in pool.iterrows():
            code = row['code']
            table_name = f"hist_{code.replace('.', '_')}"
            
            try:
                # 提取历史数据
                df = pd.read_sql(
                    f"SELECT date, close FROM `{table_name}` ORDER BY date DESC LIMIT {lookback_days}",
                    self.conn
                )
                
                if len(df) < min_days:
                    continue
                
                p_series = df['close'].astype(float).values
                p_curr = p_series[0]
                p_max = np.max(p_series)
                p_min = np.min(p_series)
                
                # 策略条件
                cond_oversold = (p_curr / p_max) <= max_drop_from_high
                cond_bottom = (p_curr / p_min) <= max_rise_from_low
                
                if cond_oversold and cond_bottom:
                    hits.append({
                        '代码': code,
                        '名称': row.get('code_name', ''),
                        '行业': row.get('industry', ''),
                        '当前价': round(p_curr, 2),
                        '2年最高': round(p_max, 2),
                        '2年最低': round(p_min, 2),
                        '距最高跌幅': f"{((1 - p_curr/p_max)*100):.1f}%",
                        '距最低涨幅': f"{((p_curr/p_min - 1)*100):.1f}%",
                        '市值(亿)': round(row.get('cap_num', 0) / 1e8, 2)
                    })
            except Exception:
                continue
        
        return pd.DataFrame(hits)
    
    def combined_strategy(
        self,
        pool: Optional[pd.DataFrame] = None,
        min_drop_rate: float = 0.07,
        lookback_days: int = 500,
        max_drop_from_high: float = 0.40,
        max_rise_from_low: float = 1.20,
        check_support: bool = True
    ) -> pd.DataFrame:
        """组合策略：长线底部 + 缩量三连跌 + 可选均线支撑
        
        Args:
            pool: 股票池
            min_drop_rate: 短线最小跌幅
            lookback_days: 长线回看天数
            max_drop_from_high: 距高点最大比例
            max_rise_from_low: 距低点最大比例
            check_support: 是否检查均线支撑
        
        Returns:
            符合条件的股票列表
        """
        if pool is None:
            pool = self.get_universe_pool()
        
        hits = []
        print(f"🔍 正在执行【组合策略】扫描 {len(pool)} 只股票...")
        
        for _, row in pool.iterrows():
            code = row['code']
            table_name = f"hist_{code.replace('.', '_')}"
            
            try:
                # 提取长线数据
                df_long = pd.read_sql(
                    f"SELECT date, close FROM `{table_name}` ORDER BY date DESC LIMIT {lookback_days}",
                    self.conn
                )
                if len(df_long) < 250:
                    continue
                
                # 提取短线数据（最近5天）
                df_short = pd.read_sql(
                    f"SELECT date, close, volume FROM `{table_name}` ORDER BY date DESC LIMIT 5",
                    self.conn
                )
                if len(df_short) < 5:
                    continue
                
                # 长线条件
                p_long = df_long['close'].astype(float).values
                p_curr = p_long[0]
                p_max = np.max(p_long)
                p_min = np.min(p_long)
                
                cond_long = (p_curr / p_max <= max_drop_from_high) and (p_curr / p_min <= max_rise_from_low)
                
                if not cond_long:
                    continue
                
                # 短线条件
                p = df_short['close'].astype(float).values
                v = df_short['volume'].astype(float).values
                
                cond_reversal = p[3] > p[4] if len(p) >= 5 else False
                cond_price = (p[0] < p[1]) and (p[1] < p[2]) and (p[2] < p[3])
                cond_volume = (v[0] < v[1]) and (v[1] < v[2])
                drop_rate = (p[0] - p[3]) / p[3]
                cond_drop = drop_rate <= -min_drop_rate
                
                if not (cond_reversal and cond_price and cond_volume and cond_drop):
                    continue
                
                # 可选：均线支撑检查
                support_tags = []
                if check_support:
                    df_long_sorted = df_long.sort_values('date')
                    p_series = df_long_sorted['close'].astype(float)
                    
                    ma120 = p_series.rolling(120).mean().iloc[-1] if len(p_series) >= 120 else None
                    ma250 = p_series.rolling(250).mean().iloc[-1] if len(p_series) >= 250 else None
                    
                    if ma120 and abs(p_curr - ma120) / ma120 <= 0.05:
                        support_tags.append("MA120支撑")
                    if ma250 and abs(p_curr - ma250) / ma250 <= 0.05:
                        support_tags.append("MA250支撑")
                    if (p_curr / p_min) <= 1.03:
                        support_tags.append("历史最低点")
                
                hits.append({
                    '代码': code,
                    '名称': row.get('code_name', ''),
                    '行业': row.get('industry', ''),
                    '最新价': round(p[0], 2),
                    '三日累跌': f"{drop_rate:.2%}",
                    '距2年高点': f"{((1 - p_curr/p_max)*100):.1f}%",
                    '距2年低点': f"{((p_curr/p_min - 1)*100):.1f}%",
                    '支撑特征': " + ".join(support_tags) if support_tags else "底部区域",
                    '市值(亿)': round(row.get('cap_num', 0) / 1e8, 2),
                    '触发日期': df_short['date'].iloc[0]
                })
            except Exception:
                continue
        
        return pd.DataFrame(hits)

