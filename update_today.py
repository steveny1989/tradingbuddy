#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速更新脚本 - 更新最新交易日数据
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.data.fetcher import DataFetcher
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """更新最新交易日数据"""
    logger.info("="*60)
    logger.info("🔄 快速更新最新交易日数据")
    logger.info("="*60)
    
    try:
        # 初始化 fetcher
        fetcher = DataFetcher()
        
        # 更新 2026-01-05 的数据
        logger.info("\n更新 2026-01-05 的数据...")
        fetcher.update_daily(date='20260105')
        
        logger.info("\n✅ 更新完成！")
        
        # 显示统计
        logger.info("\n查看更新后的状态...")
        stats = fetcher.get_stats()
        
        logger.info(f"\n📊 数据统计:")
        logger.info(f"  Raw Layer: {stats['raw']['daily']['total_records']:,} 条")
        logger.info(f"  Cleaned Layer: {stats['cleaned']['daily']['valid_records']:,} 条")
        logger.info(f"  数据质量: {stats['summary']['valid_rate']*100:.1f}%")
        
    except Exception as e:
        logger.error(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
