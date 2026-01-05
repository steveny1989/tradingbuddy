#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试新数据层

验证新数据层是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.layers import RawLayer, CleanedLayer, AggregatedLayer
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_basic_operations():
    """测试基本操作"""
    logger.info("="*60)
    logger.info("快速测试新数据层")
    logger.info("="*60)
    
    # 1. 测试 Cleaned Layer
    logger.info("\n1. 测试 Cleaned Layer...")
    cleaned = CleanedLayer()
    
    # 读取贵州茅台数据
    df = cleaned.get_daily_data('600519', only_valid=True)
    if df is not None and not df.empty:
        logger.info(f"   ✅ 读取成功: {len(df)} 条记录")
        logger.info(f"   日期范围: {df['date'].min()} ~ {df['date'].max()}")
        logger.info(f"   最新收盘价: {df.iloc[-1]['close']}")
    else:
        logger.error("   ❌ 读取失败")
        return False
    
    # 2. 测试 Aggregated Layer
    logger.info("\n2. 测试 Aggregated Layer...")
    aggregated = AggregatedLayer()
    
    # 计算技术指标（需要传入数据）
    try:
        count = aggregated.calculate_and_save_indicators('600519', df)
        logger.info(f"   ✅ 计算成功: {count} 条指标")
        
        # 读取指标
        indicators = aggregated.get_indicators('600519')
        if indicators is not None and not indicators.empty:
            latest = indicators.iloc[-1]
            logger.info(f"   最新指标:")
            logger.info(f"     MA20: {latest['ma20']:.2f}")
            logger.info(f"     RSI: {latest['rsi']:.2f}")
            logger.info(f"     MACD: {latest['macd']:.4f}")
    except Exception as e:
        logger.error(f"   ❌ 计算失败: {e}")
        return False
    
    # 3. 测试统计信息
    logger.info("\n3. 测试统计信息...")
    stats = cleaned.get_stats()
    logger.info(f"   总记录: {stats['daily']['total_records']:,}")
    logger.info(f"   有效记录: {stats['daily']['valid_records']:,}")
    logger.info(f"   有效率: {stats['daily']['valid_rate']*100:.1f}%")
    logger.info(f"   股票数: {stats['daily']['total_stocks']}")
    
    logger.info("\n" + "="*60)
    logger.info("✅ 所有测试通过！")
    logger.info("="*60)
    
    return True


def main():
    """主函数"""
    try:
        success = test_basic_operations()
        if success:
            logger.info("\n新数据层工作正常，可以开始使用！")
            logger.info("\n使用示例:")
            logger.info("  from src.data.layers import CleanedLayer")
            logger.info("  cleaned = CleanedLayer()")
            logger.info("  df = cleaned.get_daily_data('600519', only_valid=True)")
            return 0
        else:
            logger.error("\n测试失败，请检查错误信息")
            return 1
    except Exception as e:
        logger.error(f"\n测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
