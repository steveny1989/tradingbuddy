# -*- coding: utf-8 -*-
"""
数据迁移工具

将现有数据库的数据迁移到新的三层架构
- 从 data/a_share.db 迁移日线数据
- 从 data/stock_data.db 迁移分表数据（如果存在）
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import pandas as pd
from datetime import datetime
from src.data.layers import RawLayer, CleanedLayer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self):
        self.raw_layer = RawLayer()
        self.cleaned_layer = CleanedLayer()
        
        self.old_db_path = 'data/a_share.db'
        self.stock_data_db = 'data/stock_data.db'
    
    def check_old_databases(self):
        """检查旧数据库是否存在"""
        logger.info("检查旧数据库...")
        
        if os.path.exists(self.old_db_path):
            # 检查daily_data表
            with sqlite3.connect(self.old_db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) as count, COUNT(DISTINCT code) as stocks
                    FROM daily_data
                """)
                row = cursor.fetchone()
                logger.info(f"✓ {self.old_db_path} 存在")
                logger.info(f"  daily_data表: {row[0]:,} 条记录, {row[1]} 只股票")
                return True
        else:
            logger.warning(f"✗ {self.old_db_path} 不存在")
            return False
    
    def migrate_daily_data(self, limit: int = None, test_mode: bool = False):
        """
        迁移日线数据
        
        Args:
            limit: 限制迁移的股票数量（用于测试）
            test_mode: 测试模式，只迁移少量数据
        """
        logger.info("\n" + "="*60)
        logger.info("开始迁移日线数据")
        logger.info("="*60)
        
        if not os.path.exists(self.old_db_path):
            logger.error(f"数据库不存在: {self.old_db_path}")
            return
        
        with sqlite3.connect(self.old_db_path) as conn:
            # 获取所有股票代码
            if test_mode:
                logger.info("测试模式：只迁移3只股票")
                cursor = conn.execute("SELECT DISTINCT code FROM daily_data LIMIT 3")
            elif limit:
                logger.info(f"限制模式：只迁移{limit}只股票")
                cursor = conn.execute(f"SELECT DISTINCT code FROM daily_data LIMIT {limit}")
            else:
                cursor = conn.execute("SELECT DISTINCT code FROM daily_data")
            
            codes = [row[0] for row in cursor.fetchall()]
            logger.info(f"找到 {len(codes)} 只股票需要迁移")
        
        # 统计信息
        total_migrated = 0
        total_valid = 0
        total_invalid = 0
        failed_codes = []
        
        for idx, code in enumerate(codes, 1):
            try:
                logger.info(f"\n[{idx}/{len(codes)}] 迁移 {code}...")
                
                # 从旧数据库读取
                with sqlite3.connect(self.old_db_path) as conn:
                    df = pd.read_sql_query("""
                        SELECT code, date, open, high, low, close, volume, amount
                        FROM daily_data
                        WHERE code = ?
                        ORDER BY date
                    """, conn, params=(code,))
                
                if df.empty:
                    logger.warning(f"  {code} 没有数据")
                    continue
                
                logger.info(f"  读取到 {len(df)} 条记录")
                
                # 保存到Raw Layer
                raw_count = self.raw_layer.save_daily_data(df, source='migration_a_share')
                logger.info(f"  ✓ Raw Layer: {raw_count} 条")
                
                # 清洗到Cleaned Layer
                clean_stats = self.cleaned_layer.clean_and_save_daily_data(df, source='migration_a_share')
                logger.info(f"  ✓ Cleaned Layer: {clean_stats['valid']}/{clean_stats['total']} 有效 ({clean_stats['valid_rate']*100:.1f}%)")
                
                total_migrated += clean_stats['total']
                total_valid += clean_stats['valid']
                total_invalid += clean_stats['invalid']
                
            except Exception as e:
                logger.error(f"  ✗ 迁移失败: {e}")
                failed_codes.append(code)
        
        # 打印总结
        logger.info("\n" + "="*60)
        logger.info("迁移完成")
        logger.info("="*60)
        logger.info(f"成功迁移: {len(codes) - len(failed_codes)}/{len(codes)} 只股票")
        logger.info(f"总记录数: {total_migrated:,}")
        logger.info(f"有效记录: {total_valid:,} ({total_valid/total_migrated*100:.1f}%)")
        logger.info(f"无效记录: {total_invalid:,}")
        
        if failed_codes:
            logger.warning(f"\n失败的股票 ({len(failed_codes)}):")
            for code in failed_codes[:10]:  # 只显示前10个
                logger.warning(f"  - {code}")
            if len(failed_codes) > 10:
                logger.warning(f"  ... 还有 {len(failed_codes)-10} 只")
    
    def verify_migration(self):
        """验证迁移结果"""
        logger.info("\n" + "="*60)
        logger.info("验证迁移结果")
        logger.info("="*60)
        
        # 获取统计信息
        raw_stats = self.raw_layer.get_stats()
        cleaned_stats = self.cleaned_layer.get_stats()
        
        logger.info("\nRaw Layer:")
        logger.info(f"  总记录: {raw_stats['daily']['total_records']:,}")
        logger.info(f"  股票数: {raw_stats['daily']['total_stocks']}")
        
        logger.info("\nCleaned Layer:")
        logger.info(f"  总记录: {cleaned_stats['daily']['total_records']:,}")
        logger.info(f"  有效记录: {cleaned_stats['daily']['valid_records']:,} ({cleaned_stats['daily']['valid_rate']*100:.1f}%)")
        logger.info(f"  停牌记录: {cleaned_stats['daily']['suspended_records']:,}")
        logger.info(f"  股票数: {cleaned_stats['daily']['total_stocks']}")
        
        # 对比旧数据库
        if os.path.exists(self.old_db_path):
            with sqlite3.connect(self.old_db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM daily_data")
                old_count = cursor.fetchone()[0]
                logger.info(f"\n旧数据库 (a_share.db):")
                logger.info(f"  总记录: {old_count:,}")
                
                # 计算迁移率
                migration_rate = cleaned_stats['daily']['total_records'] / old_count * 100 if old_count > 0 else 0
                logger.info(f"\n迁移率: {migration_rate:.1f}%")
                
                if migration_rate < 95:
                    logger.warning("⚠️  迁移率低于95%，可能有数据丢失")
                else:
                    logger.info("✅ 迁移率正常")
    
    def sample_check(self, code: str = '600519'):
        """抽样检查数据质量"""
        logger.info("\n" + "="*60)
        logger.info(f"抽样检查: {code}")
        logger.info("="*60)
        
        # 从旧数据库读取
        with sqlite3.connect(self.old_db_path) as conn:
            old_df = pd.read_sql_query("""
                SELECT * FROM daily_data
                WHERE code = ?
                ORDER BY date DESC
                LIMIT 10
            """, conn, params=(code,))
        
        # 从新数据库读取
        new_df = self.cleaned_layer.get_daily_data(code, only_valid=True)
        
        if new_df is not None:
            new_df = new_df.sort_values('date', ascending=False).head(10)
        
        logger.info(f"\n旧数据库最新10条:")
        if not old_df.empty:
            for _, row in old_df.iterrows():
                logger.info(f"  {row['date']}: close={row['close']}, volume={row['volume']}")
        
        logger.info(f"\n新数据库最新10条:")
        if new_df is not None and not new_df.empty:
            for _, row in new_df.iterrows():
                logger.info(f"  {row['date']}: close={row['close']}, volume={row['volume']}, valid={row['is_valid']}")
        else:
            logger.warning("  没有数据")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据迁移工具')
    parser.add_argument('--test', action='store_true', help='测试模式（只迁移3只股票）')
    parser.add_argument('--limit', type=int, help='限制迁移的股票数量')
    parser.add_argument('--verify-only', action='store_true', help='只验证，不迁移')
    parser.add_argument('--sample', type=str, help='抽样检查指定股票')
    
    args = parser.parse_args()
    
    migrator = DataMigrator()
    
    # 检查旧数据库
    if not migrator.check_old_databases():
        logger.error("旧数据库不存在，无法迁移")
        return
    
    if args.verify_only:
        # 只验证
        migrator.verify_migration()
    elif args.sample:
        # 抽样检查
        migrator.sample_check(args.sample)
    else:
        # 执行迁移
        migrator.migrate_daily_data(
            limit=args.limit,
            test_mode=args.test
        )
        
        # 验证结果
        migrator.verify_migration()
        
        # 抽样检查
        migrator.sample_check('600519')
    
    logger.info("\n✅ 完成！")


if __name__ == "__main__":
    main()
