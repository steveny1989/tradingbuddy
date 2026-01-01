#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库优化工具
Database Optimization Tool

功能：
1. 创建统一大表
2. 迁移现有数据
3. 性能对比测试
"""
import sqlite3
import pandas as pd
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
    
    def create_unified_table(self):
        """创建统一的日线数据表"""
        logger.info("创建统一表 daily_data...")
        
        cursor = self.conn.cursor()
        
        # 创建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_data (
                code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume REAL,
                amount REAL,
                amplitude REAL,
                pct_chg REAL,
                change REAL,
                turnover REAL,
                PRIMARY KEY (code, date)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_date_code 
            ON daily_data(date, code)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_code_date 
            ON daily_data(code, date)
        """)
        
        self.conn.commit()
        logger.info("✅ 统一表创建完成")
    
    def migrate_data(self, limit: int = None):
        """
        迁移数据从分表到统一表
        
        Args:
            limit: 限制迁移的表数量（用于测试）
        """
        logger.info("开始数据迁移...")
        
        cursor = self.conn.cursor()
        
        # 获取所有分表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'daily_%'
            AND name != 'daily_data'
        """)
        tables = cursor.fetchall()
        
        if limit:
            tables = tables[:limit]
        
        total = len(tables)
        logger.info(f"找到 {total} 张分表")
        
        migrated = 0
        errors = 0
        total_records = 0
        
        for i, (table_name,) in enumerate(tables, 1):
            try:
                # 提取股票代码
                code = table_name.replace('daily_', '').replace('_', '.')
                
                # 检查表是否有数据
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    logger.debug(f"跳过空表: {table_name}")
                    continue
                
                # 读取数据
                df = pd.read_sql(f"SELECT * FROM {table_name}", self.conn)
                
                if df.empty:
                    continue
                
                # 添加code列
                df['code'] = code
                
                # 确保列顺序正确
                columns = ['code', 'date', 'open', 'close', 'high', 'low', 
                          'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
                
                # 只保留存在的列
                df_columns = [col for col in columns if col in df.columns]
                df = df[df_columns]
                
                # 插入数据
                df.to_sql('daily_data', self.conn, if_exists='append', index=False)
                
                migrated += 1
                total_records += len(df)
                
                if i % 100 == 0:
                    self.conn.commit()
                    logger.info(f"进度: {i}/{total} ({i/total*100:.1f}%), 已迁移: {migrated}, 记录数: {total_records:,}")
                
            except Exception as e:
                logger.error(f"迁移 {table_name} 失败: {e}")
                errors += 1
        
        self.conn.commit()
        logger.info(f"✅ 数据迁移完成: 成功 {migrated}, 失败 {errors}, 总记录数: {total_records:,}")
    
    def benchmark_query_performance(self):
        """性能基准测试"""
        logger.info("\n" + "="*80)
        logger.info("性能基准测试")
        logger.info("="*80)
        
        # 测试1: 查询单只股票历史数据
        logger.info("\n【测试1: 查询单只股票历史数据】")
        
        code = 'sh.600000'
        table_name = 'daily_sh_600000'
        
        # 方法1: 分表查询
        start = time.time()
        df1 = pd.read_sql(f"SELECT * FROM {table_name}", self.conn)
        time1 = time.time() - start
        logger.info(f"分表查询: {time1:.4f}秒, {len(df1)}条记录")
        
        # 方法2: 统一表查询
        start = time.time()
        df2 = pd.read_sql(f"SELECT * FROM daily_data WHERE code = '{code}'", self.conn)
        time2 = time.time() - start
        logger.info(f"统一表查询: {time2:.4f}秒, {len(df2)}条记录")
        logger.info(f"性能对比: {time1/time2:.2f}x")
        
        # 测试2: 查询全市场某日数据
        logger.info("\n【测试2: 查询全市场某日数据】")
        
        date = '2024-12-31'
        
        # 方法1: 分表查询（模拟）
        start = time.time()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'daily_%'
            AND name != 'daily_data'
            LIMIT 100
        """)
        tables = cursor.fetchall()
        
        results = []
        for (table_name,) in tables:
            df = pd.read_sql(
                f"SELECT * FROM {table_name} WHERE date = '{date}'", 
                self.conn
            )
            if not df.empty:
                results.append(df)
        
        time1 = time.time() - start
        total1 = sum(len(df) for df in results)
        logger.info(f"分表查询（100只股票）: {time1:.4f}秒, {total1}条记录")
        
        # 方法2: 统一表查询
        start = time.time()
        df2 = pd.read_sql(f"SELECT * FROM daily_data WHERE date = '{date}'", self.conn)
        time2 = time.time() - start
        logger.info(f"统一表查询（全市场）: {time2:.4f}秒, {len(df2)}条记录")
        logger.info(f"性能对比: {time1/time2:.2f}x")
        
        # 测试3: 查询最近N天数据
        logger.info("\n【测试3: 查询最近10天数据】")
        
        # 统一表查询
        start = time.time()
        df = pd.read_sql("""
            SELECT * FROM daily_data 
            WHERE date >= (SELECT MAX(date) FROM daily_data) - 10
            ORDER BY code, date
        """, self.conn)
        time3 = time.time() - start
        logger.info(f"统一表查询: {time3:.4f}秒, {len(df)}条记录")
        
        logger.info("\n" + "="*80)
    
    def get_statistics(self):
        """获取统计信息"""
        logger.info("\n数据库统计:")
        logger.info("-"*80)
        
        cursor = self.conn.cursor()
        
        # 分表数量
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name LIKE 'daily_%'
            AND name != 'daily_data'
        """)
        table_count = cursor.fetchone()[0]
        logger.info(f"分表数量: {table_count}")
        
        # 统一表记录数
        try:
            cursor.execute("SELECT COUNT(*) FROM daily_data")
            unified_count = cursor.fetchone()[0]
            logger.info(f"统一表记录数: {unified_count:,}")
            
            # 统一表大小
            cursor.execute("SELECT COUNT(DISTINCT code) FROM daily_data")
            stock_count = cursor.fetchone()[0]
            logger.info(f"统一表股票数: {stock_count}")
            
            avg_records = unified_count / stock_count if stock_count > 0 else 0
            logger.info(f"平均每只股票记录数: {avg_records:.0f}")
        except:
            logger.info("统一表尚未创建或为空")
        
        logger.info("-"*80)
    
    def close(self):
        """关闭连接"""
        self.conn.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库优化工具')
    parser.add_argument('--create', action='store_true', help='创建统一表')
    parser.add_argument('--migrate', action='store_true', help='迁移数据')
    parser.add_argument('--limit', type=int, help='限制迁移的表数量（测试用）')
    parser.add_argument('--benchmark', action='store_true', help='性能测试')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--all', action='store_true', help='执行所有操作')
    
    args = parser.parse_args()
    
    optimizer = DatabaseOptimizer()
    
    try:
        if args.all or args.stats:
            optimizer.get_statistics()
        
        if args.all or args.create:
            optimizer.create_unified_table()
        
        if args.all or args.migrate:
            optimizer.migrate_data(limit=args.limit)
        
        if args.all or args.benchmark:
            optimizer.benchmark_query_performance()
        
        if args.all or args.stats:
            optimizer.get_statistics()
    
    finally:
        optimizer.close()
    
    logger.info("\n✨ 完成!")


if __name__ == "__main__":
    main()
