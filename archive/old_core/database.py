# -*- coding: utf-8 -*-
"""数据库管理模块"""
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class StockDatabase:
    """股票数据库管理类"""
    
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()
        
        # 股票基本信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_basic (
                code TEXT PRIMARY KEY,
                name TEXT,
                market TEXT,
                list_date TEXT,
                status TEXT DEFAULT 'active',
                updated_at TEXT
            )
        """)
        
        # 市场信息表（每日快照）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_snapshot (
                code TEXT,
                date TEXT,
                price REAL,
                pct_chg REAL,
                volume REAL,
                amount REAL,
                pe_ttm REAL,
                pb REAL,
                total_cap REAL,
                float_cap REAL,
                turnover REAL,
                PRIMARY KEY (code, date)
            )
        """)
        
        # 数据同步状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_status (
                code TEXT PRIMARY KEY,
                last_sync_date TEXT,
                total_records INTEGER,
                status TEXT,
                error_msg TEXT,
                updated_at TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("数据库表结构初始化完成")
    
    def save_stock_list(self, df: pd.DataFrame):
        """保存股票列表"""
        df.to_sql("stock_basic", self.conn, if_exists='replace', index=False)
        logger.info(f"保存股票列表: {len(df)} 只")
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            return pd.read_sql("SELECT * FROM stock_basic", self.conn)
        except:
            return pd.DataFrame()
    
    def save_daily_data(self, code: str, df: pd.DataFrame):
        """
        保存单只股票的日线数据（使用UPSERT避免数据丢失）
        
        Args:
            code: 股票代码
            df: 日线数据DataFrame
        """
        if df.empty:
            return
        
        table_name = f"daily_{code.replace('.', '_')}"
        
        # 先创建表结构（如果不存在）
        cursor = self.conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                date TEXT PRIMARY KEY,
                open REAL, close REAL, high REAL, low REAL,
                volume REAL, amount REAL,
                amplitude REAL, pct_chg REAL, change REAL, turnover REAL
            )
        """)
        
        # 使用INSERT OR REPLACE确保数据安全
        # 这样即使API返回不全，也不会删除历史数据
        for _, row in df.iterrows():
            cursor.execute(f"""
                INSERT OR REPLACE INTO {table_name} 
                (date, open, close, high, low, volume, amount, amplitude, pct_chg, change, turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('date'), row.get('open'), row.get('close'), 
                row.get('high'), row.get('low'), row.get('volume'), 
                row.get('amount'), row.get('amplitude'), row.get('pct_chg'), 
                row.get('change'), row.get('turnover')
            ))
        
        self.conn.commit()
        
        # 更新同步状态
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        self._update_sync_status(code, total, 'success')
    
    def append_daily_data(self, code: str, df: pd.DataFrame):
        """
        追加日线数据（增量更新，使用UPSERT避免重复）
        
        Args:
            code: 股票代码
            df: 日线数据DataFrame
        """
        if df.empty:
            return
        
        # 使用save_daily_data的安全逻辑
        # INSERT OR REPLACE会自动处理重复数据
        self.save_daily_data(code, df)
    
    def get_daily_data(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取单只股票的日线数据"""
        table_name = f"daily_{code.replace('.', '_')}"
        
        try:
            query = f"SELECT * FROM {table_name}"
            conditions = []
            
            if start_date:
                conditions.append(f"date >= '{start_date}'")
            if end_date:
                conditions.append(f"date <= '{end_date}'")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY date ASC"
            
            return pd.read_sql(query, self.conn)
        except:
            return pd.DataFrame()
    
    def table_exists(self, code: str) -> bool:
        """检查股票数据表是否存在"""
        table_name = f"daily_{code.replace('.', '_')}"
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def get_last_date(self, code: str) -> Optional[str]:
        """获取股票最后一条数据的日期"""
        if not self.table_exists(code):
            return None
        
        table_name = f"daily_{code.replace('.', '_')}"
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT MAX(date) FROM {table_name}")
            result = cursor.fetchone()
            return result[0] if result else None
        except:
            return None
    
    def _update_sync_status(self, code: str, total_records: int, status: str, error_msg: str = None):
        """更新同步状态"""
        from datetime import datetime
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sync_status 
            (code, last_sync_date, total_records, status, error_msg, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (code, datetime.now().strftime('%Y-%m-%d'), total_records, status, error_msg, 
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()
    
    def get_sync_status(self) -> pd.DataFrame:
        """获取同步状态"""
        try:
            return pd.read_sql("SELECT * FROM sync_status ORDER BY updated_at DESC", self.conn)
        except:
            return pd.DataFrame()
    
    def get_next_trading_day(self, date: str, index_code: str = 'sh.000001') -> Optional[str]:
        """
        获取下一个交易日
        
        Args:
            date: 当前日期
            index_code: 指数代码（用于判断交易日）
            
        Returns:
            下一个交易日，如果没有则返回None
        """
        try:
            # 从指数数据中获取所有交易日
            df = self.get_daily_data(index_code)
            if df.empty:
                return None
            
            # 找到大于当前日期的第一个交易日
            df = df[df['date'] > date].sort_values('date')
            if df.empty:
                return None
            
            return df['date'].iloc[0]
        except Exception as e:
            logger.error(f"获取下一个交易日失败: {e}")
            return None
    
    def get_statistics(self) -> dict:
        """获取数据库统计信息"""
        cursor = self.conn.cursor()
        
        # 统计股票数量
        cursor.execute("SELECT COUNT(*) FROM stock_basic")
        total_stocks = cursor.fetchone()[0]
        
        # 统计已下载数据的股票数量
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name LIKE 'daily_%'
        """)
        downloaded_stocks = cursor.fetchone()[0]
        
        # 统计总记录数
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'daily_%'
        """)
        tables = cursor.fetchall()
        
        total_records = 0
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records += cursor.fetchone()[0]
        
        return {
            'total_stocks': total_stocks,
            'downloaded_stocks': downloaded_stocks,
            'completion_rate': f"{downloaded_stocks/total_stocks*100:.1f}%" if total_stocks > 0 else "0%",
            'total_records': total_records,
            'avg_records_per_stock': total_records // downloaded_stocks if downloaded_stocks > 0 else 0
        }
    
    def save_market_snapshot(self, df: pd.DataFrame):
        """保存市场快照数据"""
        df.to_sql("market_snapshot", self.conn, if_exists='append', index=False)
        logger.info(f"保存市场快照: {len(df)} 条记录")
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        logger.info("数据库连接已关闭")
