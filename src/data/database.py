# -*- coding: utf-8 -*-
"""数据库管理模块"""
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List
import logging
from datetime import datetime

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
        
        # 财务数据表 - 资产负债表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance_sheet (
                code TEXT,
                report_date TEXT,
                report_type TEXT,
                total_assets REAL,
                total_liabilities REAL,
                shareholders_equity REAL,
                current_assets REAL,
                current_liabilities REAL,
                cash_and_equivalents REAL,
                accounts_receivable REAL,
                inventory REAL,
                fixed_assets REAL,
                intangible_assets REAL,
                short_term_debt REAL,
                long_term_debt REAL,
                accounts_payable REAL,
                updated_at TEXT,
                PRIMARY KEY (code, report_date)
            )
        """)
        
        # 财务数据表 - 利润表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_statement (
                code TEXT,
                report_date TEXT,
                report_type TEXT,
                total_revenue REAL,
                operating_revenue REAL,
                operating_cost REAL,
                gross_profit REAL,
                operating_profit REAL,
                total_profit REAL,
                net_profit REAL,
                net_profit_parent REAL,
                basic_eps REAL,
                diluted_eps REAL,
                selling_expenses REAL,
                admin_expenses REAL,
                rd_expenses REAL,
                financial_expenses REAL,
                updated_at TEXT,
                PRIMARY KEY (code, report_date)
            )
        """)
        
        # 财务数据表 - 现金流量表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash_flow (
                code TEXT,
                report_date TEXT,
                report_type TEXT,
                operating_cash_flow REAL,
                investing_cash_flow REAL,
                financing_cash_flow REAL,
                net_cash_flow REAL,
                cash_received_from_sales REAL,
                cash_paid_for_goods REAL,
                cash_paid_to_employees REAL,
                taxes_paid REAL,
                cash_from_investments REAL,
                cash_for_fixed_assets REAL,
                cash_from_financing REAL,
                cash_for_dividends REAL,
                updated_at TEXT,
                PRIMARY KEY (code, report_date)
            )
        """)
        
        # 财务指标表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_indicators (
                code TEXT,
                report_date TEXT,
                roe REAL,
                roa REAL,
                gross_margin REAL,
                net_margin REAL,
                operating_margin REAL,
                current_ratio REAL,
                quick_ratio REAL,
                debt_to_asset_ratio REAL,
                debt_to_equity_ratio REAL,
                asset_turnover REAL,
                inventory_turnover REAL,
                receivable_turnover REAL,
                eps REAL,
                bvps REAL,
                pe_ratio REAL,
                pb_ratio REAL,
                updated_at TEXT,
                PRIMARY KEY (code, report_date)
            )
        """)
        
        # 回测结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                config TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                initial_capital REAL NOT NULL,
                final_value REAL,
                total_return REAL,
                total_profit REAL,
                max_drawdown REAL,
                total_trades INTEGER,
                completed_trades INTEGER,
                win_trades INTEGER,
                loss_trades INTEGER,
                win_rate REAL,
                avg_profit REAL,
                avg_profit_rate REAL,
                max_profit REAL,
                max_loss REAL,
                avg_hold_days REAL,
                daily_values TEXT,
                trades TEXT,
                status TEXT DEFAULT 'completed',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                error_message TEXT
            )
        """)
        
        # 为回测结果表创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtest_strategy 
            ON backtest_results(strategy_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtest_created 
            ON backtest_results(created_at DESC)
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
    
    def save_daily_data(self, code: str, df: pd.DataFrame, sync_to_unified: bool = True):
        """
        保存单只股票的日线数据（使用UPSERT避免数据丢失）
        
        Args:
            code: 股票代码
            df: 日线数据DataFrame
            sync_to_unified: 是否同步到统一表（默认True）
        """
        if df.empty:
            return
        
        table_name = f"daily_{code.replace('.', '_')}"
        
        # 先创建表结构（如果不存在）
        cursor = self.conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                date TEXT PRIMARY KEY,
                code TEXT,
                open REAL, close REAL, high REAL, low REAL,
                volume INTEGER, amount REAL,
                pct_chg REAL, turnover REAL
            )
        """)
        
        # 使用INSERT OR REPLACE确保数据安全
        for _, row in df.iterrows():
            cursor.execute(f"""
                INSERT OR REPLACE INTO {table_name} 
                (date, code, open, high, low, close, volume, amount, pct_chg, turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('date'), code,
                row.get('open'), row.get('high'), row.get('low'), row.get('close'),
                row.get('volume'), row.get('amount'), 
                row.get('pct_chg'), row.get('turnover')
            ))
        
        # 同步到统一表
        if sync_to_unified:
            self._sync_to_unified_table(code, df)
        
        self.conn.commit()
        
        # 更新同步状态
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        self._update_sync_status(code, total, 'success')
    
    def append_daily_data(self, code: str, df: pd.DataFrame, sync_to_unified: bool = True):
        """
        追加日线数据（增量更新，使用UPSERT避免重复）
        
        Args:
            code: 股票代码
            df: 日线数据DataFrame
            sync_to_unified: 是否同步到统一表（默认True）
        """
        if df.empty:
            return
        
        # 使用save_daily_data的安全逻辑
        # INSERT OR REPLACE会自动处理重复数据
        self.save_daily_data(code, df, sync_to_unified=sync_to_unified)
    
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
    
    def _sync_to_unified_table(self, code: str, df: pd.DataFrame):
        """
        同步数据到统一表
        
        Args:
            code: 股票代码
            df: 日线数据DataFrame
        """
        if df.empty:
            return
        
        try:
            # 确保统一表存在
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_data (
                    code TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL, close REAL, high REAL, low REAL,
                    volume REAL, amount REAL,
                    amplitude REAL, pct_chg REAL, change REAL, turnover REAL,
                    PRIMARY KEY (code, date)
                )
            """)
            
            # 添加code列
            df_sync = df.copy()
            df_sync['code'] = code
            
            # 计算amplitude和change（如果不存在）
            if 'amplitude' not in df_sync.columns and 'high' in df_sync.columns and 'low' in df_sync.columns and 'close' in df_sync.columns:
                # amplitude = (high - low) / close * 100
                df_sync['amplitude'] = ((df_sync['high'] - df_sync['low']) / df_sync['close'] * 100).round(2)
            
            if 'change' not in df_sync.columns and 'pct_chg' in df_sync.columns and 'close' in df_sync.columns:
                # change = close * pct_chg / 100
                df_sync['change'] = (df_sync['close'] * df_sync['pct_chg'] / 100).round(2)
            
            # 使用INSERT OR REPLACE同步数据
            for _, row in df_sync.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_data 
                    (code, date, open, close, high, low, volume, amount, amplitude, pct_chg, change, turnover)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    code, 
                    row.get('date'),
                    row.get('open'), 
                    row.get('close'),
                    row.get('high'), 
                    row.get('low'), 
                    row.get('volume'), 
                    row.get('amount'),
                    row.get('amplitude'), 
                    row.get('pct_chg'), 
                    row.get('change'), 
                    row.get('turnover')
                ))
            
            logger.debug(f"同步 {code} 的 {len(df_sync)} 条记录到统一表")
            
        except Exception as e:
            logger.warning(f"同步到统一表失败 {code}: {e}")
    
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
    
    def get_market_data_unified(self, date: str, codes: List[str] = None) -> pd.DataFrame:
        """
        从统一表获取全市场或指定股票的某日数据（高性能）
        
        Args:
            date: 日期
            codes: 股票代码列表（None表示全市场）
            
        Returns:
            DataFrame with columns: code, date, open, close, high, low, volume, amount, etc.
        """
        try:
            if codes:
                placeholders = ','.join(['?' for _ in codes])
                query = f"SELECT * FROM daily_data WHERE date = ? AND code IN ({placeholders})"
                return pd.read_sql(query, self.conn, params=[date] + codes)
            else:
                query = "SELECT * FROM daily_data WHERE date = ?"
                return pd.read_sql(query, self.conn, params=[date])
        except Exception as e:
            logger.error(f"从统一表获取数据失败: {e}")
            return pd.DataFrame()
    
    def get_recent_data_unified(self, days: int = 10, codes: List[str] = None) -> pd.DataFrame:
        """
        从统一表获取全市场或指定股票最近N天的数据（用于策略扫描）
        
        Args:
            days: 天数
            codes: 股票代码列表（None表示全市场）
            
        Returns:
            DataFrame with columns: code, date, open, close, high, low, volume, amount, etc.
        """
        try:
            if codes:
                placeholders = ','.join(['?' for _ in codes])
                query = f"""
                    SELECT * FROM daily_data 
                    WHERE date >= (SELECT date FROM daily_data ORDER BY date DESC LIMIT 1 OFFSET {days})
                    AND code IN ({placeholders})
                    ORDER BY code, date
                """
                return pd.read_sql(query, self.conn, params=codes)
            else:
                query = f"""
                    SELECT * FROM daily_data 
                    WHERE date >= (SELECT date FROM daily_data ORDER BY date DESC LIMIT 1 OFFSET {days})
                    ORDER BY code, date
                """
                return pd.read_sql(query, self.conn)
        except Exception as e:
            logger.error(f"从统一表获取最近数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_data_batch_unified(self, codes: List[str], start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        从统一表批量获取多只股票的历史数据（高性能）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame with columns: code, date, open, close, high, low, volume, amount, etc.
        """
        try:
            placeholders = ','.join(['?' for _ in codes])
            query = f"SELECT * FROM daily_data WHERE code IN ({placeholders})"
            params = codes.copy()
            
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            query += " ORDER BY code, date"
            
            return pd.read_sql(query, self.conn, params=params)
        except Exception as e:
            logger.error(f"批量获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def save_market_snapshot(self, df: pd.DataFrame):
        """保存市场快照数据"""
        df.to_sql("market_snapshot", self.conn, if_exists='append', index=False)
        logger.info(f"保存市场快照: {len(df)} 条记录")
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        logger.info("数据库连接已关闭")

    
    # ==================== 财务数据相关方法 ====================
    
    def save_balance_sheet(self, code: str, df: pd.DataFrame):
        """
        保存资产负债表数据
        
        Args:
            code: 股票代码
            df: 资产负债表DataFrame
        """
        if df.empty:
            return
        
        try:
            # 处理DataFrame，提取关键字段
            # 注意：akshare返回的列名可能不同，需要根据实际情况映射
            df_processed = df.copy()
            df_processed['code'] = code
            df_processed['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 使用INSERT OR REPLACE保存数据
            df_processed.to_sql('balance_sheet', self.conn, if_exists='append', index=False)
            logger.info(f"✅ {code} 资产负债表保存成功: {len(df)} 条记录")
            
        except Exception as e:
            logger.error(f"❌ {code} 资产负债表保存失败: {e}")
    
    def save_income_statement(self, code: str, df: pd.DataFrame):
        """
        保存利润表数据
        
        Args:
            code: 股票代码
            df: 利润表DataFrame
        """
        if df.empty:
            return
        
        try:
            df_processed = df.copy()
            df_processed['code'] = code
            df_processed['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 数据库表中已有的列
            db_columns = [
                'code', 'report_date', 'report_type',
                'total_revenue', 'operating_revenue', 'operating_cost',
                'gross_profit', 'operating_profit', 'total_profit',
                'net_profit', 'net_profit_parent', 'basic_eps', 'diluted_eps',
                'selling_expenses', 'admin_expenses', 'rd_expenses', 'financial_expenses',
                'updated_at'
            ]
            
            # 只保留存在的列
            columns_to_save = [col for col in db_columns if col in df_processed.columns]
            df_to_save = df_processed[columns_to_save]
            
            # 使用cursor逐行插入，避免重复键错误
            cursor = self.conn.cursor()
            for _, row in df_to_save.iterrows():
                placeholders = ', '.join(['?' for _ in columns_to_save])
                columns_str = ', '.join(columns_to_save)
                sql = f"INSERT OR REPLACE INTO income_statement ({columns_str}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row[col] for col in columns_to_save))
            
            self.conn.commit()
            logger.info(f"✅ {code} 利润表保存成功: {len(df)} 条记录")
            
        except Exception as e:
            logger.error(f"❌ {code} 利润表保存失败: {e}")
    
    def save_cash_flow(self, code: str, df: pd.DataFrame):
        """
        保存现金流量表数据
        
        Args:
            code: 股票代码
            df: 现金流量表DataFrame
        """
        if df.empty:
            return
        
        try:
            df_processed = df.copy()
            df_processed['code'] = code
            df_processed['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            df_processed.to_sql('cash_flow', self.conn, if_exists='append', index=False)
            logger.info(f"✅ {code} 现金流量表保存成功: {len(df)} 条记录")
            
        except Exception as e:
            logger.error(f"❌ {code} 现金流量表保存失败: {e}")
    
    def save_financial_indicators(self, code: str, df: pd.DataFrame):
        """
        保存财务指标数据
        
        Args:
            code: 股票代码
            df: 财务指标DataFrame
        """
        if df.empty:
            return
        
        try:
            df_processed = df.copy()
            df_processed['code'] = code
            df_processed['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 数据库表中已有的列
            db_columns = [
                'code', 'report_date',
                'roe', 'roa', 'gross_margin', 'net_margin', 'operating_margin',
                'current_ratio', 'quick_ratio', 'debt_to_asset_ratio', 'debt_to_equity_ratio',
                'asset_turnover', 'inventory_turnover', 'receivable_turnover',
                'eps', 'bvps', 'pe_ratio', 'pb_ratio', 'updated_at'
            ]
            
            # 字段映射（同花顺API字段 -> 数据库字段）
            field_mapping = {
                'basic_eps': 'eps',
                'roe_diluted': 'roe',  # 如果没有roe，使用roe_diluted
                'inventory_turnover_days': 'inventory_turnover',  # 转换为周转率
                'receivable_turnover_days': 'receivable_turnover',  # 转换为周转率
                'equity_multiplier': 'debt_to_equity_ratio',
            }
            
            # 应用字段映射
            for old_col, new_col in field_mapping.items():
                if old_col in df_processed.columns and new_col not in df_processed.columns:
                    df_processed[new_col] = df_processed[old_col]
            
            # 只保留数据库表中存在的列
            columns_to_save = [col for col in db_columns if col in df_processed.columns]
            df_to_save = df_processed[columns_to_save]
            
            # 使用cursor逐行插入，避免重复键错误
            cursor = self.conn.cursor()
            for _, row in df_to_save.iterrows():
                placeholders = ', '.join(['?' for _ in columns_to_save])
                columns_str = ', '.join(columns_to_save)
                sql = f"INSERT OR REPLACE INTO financial_indicators ({columns_str}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row[col] for col in columns_to_save))
            
            self.conn.commit()
            logger.info(f"✅ {code} 财务指标保存成功: {len(df)} 条记录")
            
        except Exception as e:
            logger.error(f"❌ {code} 财务指标保存失败: {e}")
    
    def get_balance_sheet(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取资产负债表数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            资产负债表DataFrame
        """
        try:
            query = "SELECT * FROM balance_sheet WHERE code = ?"
            params = [code]
            
            if start_date:
                query += " AND report_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND report_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY report_date DESC"
            
            return pd.read_sql(query, self.conn, params=params)
        except Exception as e:
            logger.error(f"获取资产负债表失败: {e}")
            return pd.DataFrame()
    
    def get_income_statement(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取利润表数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            利润表DataFrame
        """
        try:
            query = "SELECT * FROM income_statement WHERE code = ?"
            params = [code]
            
            if start_date:
                query += " AND report_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND report_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY report_date DESC"
            
            return pd.read_sql(query, self.conn, params=params)
        except Exception as e:
            logger.error(f"获取利润表失败: {e}")
            return pd.DataFrame()
    
    def get_cash_flow(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取现金流量表数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            现金流量表DataFrame
        """
        try:
            query = "SELECT * FROM cash_flow WHERE code = ?"
            params = [code]
            
            if start_date:
                query += " AND report_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND report_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY report_date DESC"
            
            return pd.read_sql(query, self.conn, params=params)
        except Exception as e:
            logger.error(f"获取现金流量表失败: {e}")
            return pd.DataFrame()
    
    def get_financial_indicators(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取财务指标数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            财务指标DataFrame
        """
        try:
            query = "SELECT * FROM financial_indicators WHERE code = ?"
            params = [code]
            
            if start_date:
                query += " AND report_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND report_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY report_date DESC"
            
            return pd.read_sql(query, self.conn, params=params)
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            return pd.DataFrame()
    
    def get_latest_financial_data(self, code: str) -> dict:
        """
        获取最新的财务数据（所有报表）
        
        Args:
            code: 股票代码
            
        Returns:
            包含最新财务数据的字典
        """
        result = {
            'code': code,
            'balance_sheet': None,
            'income_statement': None,
            'cash_flow': None,
            'financial_indicators': None
        }
        
        # 获取最新的资产负债表
        balance_sheet = self.get_balance_sheet(code)
        if not balance_sheet.empty:
            result['balance_sheet'] = balance_sheet.iloc[0].to_dict()
        
        # 获取最新的利润表
        income_statement = self.get_income_statement(code)
        if not income_statement.empty:
            result['income_statement'] = income_statement.iloc[0].to_dict()
        
        # 获取最新的现金流量表
        cash_flow = self.get_cash_flow(code)
        if not cash_flow.empty:
            result['cash_flow'] = cash_flow.iloc[0].to_dict()
        
        # 获取最新的财务指标
        financial_indicators = self.get_financial_indicators(code)
        if not financial_indicators.empty:
            result['financial_indicators'] = financial_indicators.iloc[0].to_dict()
        
        return result
    
    def get_financial_statistics(self) -> dict:
        """
        获取财务数据统计信息
        
        Returns:
            统计信息字典
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        # 统计各表的数据量
        for table in ['balance_sheet', 'income_statement', 'cash_flow', 'financial_indicators']:
            try:
                cursor.execute(f"SELECT COUNT(DISTINCT code) FROM {table}")
                stock_count = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                record_count = cursor.fetchone()[0]
                
                stats[table] = {
                    'stock_count': stock_count,
                    'record_count': record_count
                }
            except:
                stats[table] = {
                    'stock_count': 0,
                    'record_count': 0
                }
        
        return stats
    
    def get_last_update_time(self, code: str) -> Optional[str]:
        """
        获取股票财务数据最后更新时间
        
        Args:
            code: 股票代码
            
        Returns:
            最后更新时间（YYYY-MM-DD HH:MM:SS），如果没有数据返回None
        """
        try:
            cursor = self.conn.cursor()
            
            # 查询所有财务表的最后更新时间，取最新的
            tables = ['balance_sheet', 'income_statement', 'cash_flow', 'financial_indicators']
            latest_time = None
            
            for table in tables:
                cursor.execute(f"SELECT MAX(updated_at) FROM {table} WHERE code = ?", (code,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    table_time = result[0]
                    if latest_time is None or table_time > latest_time:
                        latest_time = table_time
            
            return latest_time
            
        except Exception as e:
            logger.error(f"获取最后更新时间失败 {code}: {e}")
            return None

    
    # ==================== 回测结果相关方法 ====================
    
    def save_backtest_result(self, backtest_data: dict) -> bool:
        """
        保存回测结果到数据库
        
        Args:
            backtest_data: 回测结果数据字典，包含以下字段：
                - id: 回测ID
                - strategy_id: 策略ID
                - strategy_name: 策略名称
                - config: 配置（JSON字符串）
                - start_date: 开始日期
                - end_date: 结束日期
                - initial_capital: 初始资金
                - final_value: 最终价值
                - total_return: 总收益率
                - total_profit: 总盈亏
                - max_drawdown: 最大回撤
                - total_trades: 总交易次数
                - completed_trades: 完成交易次数
                - win_trades: 盈利交易次数
                - loss_trades: 亏损交易次数
                - win_rate: 胜率
                - avg_profit: 平均盈亏
                - avg_profit_rate: 平均盈亏率
                - max_profit: 最大盈利
                - max_loss: 最大亏损
                - avg_hold_days: 平均持有天数
                - daily_values: 每日净值（JSON字符串）
                - trades: 交易记录（JSON字符串）
                - status: 状态
                - created_at: 创建时间
                - completed_at: 完成时间
                - error_message: 错误信息（可选）
                
        Returns:
            是否保存成功
        """
        try:
            import json
            
            cursor = self.conn.cursor()
            
            # 准备数据
            data = {
                'id': backtest_data['id'],
                'strategy_id': backtest_data['strategy_id'],
                'strategy_name': backtest_data['strategy_name'],
                'config': json.dumps(backtest_data.get('config', {}), ensure_ascii=False),
                'start_date': backtest_data['start_date'],
                'end_date': backtest_data['end_date'],
                'initial_capital': backtest_data['initial_capital'],
                'final_value': backtest_data.get('final_value'),
                'total_return': backtest_data.get('total_return'),
                'total_profit': backtest_data.get('total_profit'),
                'max_drawdown': backtest_data.get('max_drawdown'),
                'total_trades': backtest_data.get('total_trades'),
                'completed_trades': backtest_data.get('completed_trades'),
                'win_trades': backtest_data.get('win_trades'),
                'loss_trades': backtest_data.get('loss_trades'),
                'win_rate': backtest_data.get('win_rate'),
                'avg_profit': backtest_data.get('avg_profit'),
                'avg_profit_rate': backtest_data.get('avg_profit_rate'),
                'max_profit': backtest_data.get('max_profit'),
                'max_loss': backtest_data.get('max_loss'),
                'avg_hold_days': backtest_data.get('avg_hold_days'),
                'daily_values': json.dumps(backtest_data.get('daily_values', []), ensure_ascii=False),
                'trades': json.dumps(backtest_data.get('trades', []), ensure_ascii=False),
                'status': backtest_data.get('status', 'completed'),
                'created_at': backtest_data['created_at'],
                'completed_at': backtest_data.get('completed_at'),
                'error_message': backtest_data.get('error_message')
            }
            
            # 插入数据
            cursor.execute("""
                INSERT OR REPLACE INTO backtest_results (
                    id, strategy_id, strategy_name, config, start_date, end_date,
                    initial_capital, final_value, total_return, total_profit, max_drawdown,
                    total_trades, completed_trades, win_trades, loss_trades, win_rate,
                    avg_profit, avg_profit_rate, max_profit, max_loss, avg_hold_days,
                    daily_values, trades, status, created_at, completed_at, error_message
                ) VALUES (
                    :id, :strategy_id, :strategy_name, :config, :start_date, :end_date,
                    :initial_capital, :final_value, :total_return, :total_profit, :max_drawdown,
                    :total_trades, :completed_trades, :win_trades, :loss_trades, :win_rate,
                    :avg_profit, :avg_profit_rate, :max_profit, :max_loss, :avg_hold_days,
                    :daily_values, :trades, :status, :created_at, :completed_at, :error_message
                )
            """, data)
            
            self.conn.commit()
            logger.info(f"✅ 回测结果保存成功: {data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存回测结果失败: {e}")
            return False
    
    def get_backtest_list(
        self,
        page: int = 1,
        page_size: int = 20,
        strategy_id: str = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> dict:
        """
        获取回测历史列表（分页）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            strategy_id: 策略ID筛选（可选）
            sort_by: 排序字段
            sort_order: 排序方向（asc/desc）
            
        Returns:
            {
                'items': [...],
                'total': int,
                'page': int,
                'page_size': int,
                'total_pages': int
            }
        """
        try:
            cursor = self.conn.cursor()
            
            # 构建查询条件
            where_clause = ""
            params = []
            
            if strategy_id:
                where_clause = "WHERE strategy_id = ?"
                params.append(strategy_id)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) FROM backtest_results {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # 计算总页数
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            
            # 构建查询
            offset = (page - 1) * page_size
            query = f"""
                SELECT 
                    id, strategy_id, strategy_name, start_date, end_date,
                    initial_capital, final_value, total_return, max_drawdown,
                    total_trades, win_rate, created_at, status
                FROM backtest_results
                {where_clause}
                ORDER BY {sort_by} {sort_order.upper()}
                LIMIT ? OFFSET ?
            """
            params.extend([page_size, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 构建结果
            items = []
            for row in rows:
                items.append({
                    'id': row[0],
                    'strategy_id': row[1],
                    'strategy_name': row[2],
                    'start_date': row[3],
                    'end_date': row[4],
                    'initial_capital': row[5],
                    'final_value': row[6],
                    'total_return': row[7],
                    'max_drawdown': row[8],
                    'total_trades': row[9],
                    'win_rate': row[10],
                    'created_at': row[11],
                    'status': row[12]
                })
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"获取回测列表失败: {e}")
            return {
                'items': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
    
    def get_backtest_detail(self, backtest_id: str) -> Optional[dict]:
        """
        获取回测详情
        
        Args:
            backtest_id: 回测ID
            
        Returns:
            回测详情字典，如果不存在返回None
        """
        try:
            import json
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    id, strategy_id, strategy_name, config, start_date, end_date,
                    initial_capital, final_value, total_return, total_profit, max_drawdown,
                    total_trades, completed_trades, win_trades, loss_trades, win_rate,
                    avg_profit, avg_profit_rate, max_profit, max_loss, avg_hold_days,
                    daily_values, trades, status, created_at, completed_at, error_message
                FROM backtest_results
                WHERE id = ?
            """, (backtest_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # 解析JSON字段
            config = json.loads(row[3]) if row[3] else {}
            daily_values = json.loads(row[21]) if row[21] else []
            trades = json.loads(row[22]) if row[22] else []
            
            return {
                'id': row[0],
                'strategy_id': row[1],
                'strategy_name': row[2],
                'config': config,
                'start_date': row[4],
                'end_date': row[5],
                'initial_capital': row[6],
                'final_value': row[7],
                'total_return': row[8],
                'total_profit': row[9],
                'max_drawdown': row[10],
                'total_trades': row[11],
                'completed_trades': row[12],
                'win_trades': row[13],
                'loss_trades': row[14],
                'win_rate': row[15],
                'avg_profit': row[16],
                'avg_profit_rate': row[17],
                'max_profit': row[18],
                'max_loss': row[19],
                'avg_hold_days': row[20],
                'daily_values': daily_values,
                'trades': trades,
                'status': row[23],
                'created_at': row[24],
                'completed_at': row[25],
                'error_message': row[26]
            }
            
        except Exception as e:
            logger.error(f"获取回测详情失败: {e}")
            return None
