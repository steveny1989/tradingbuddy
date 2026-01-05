#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 V2 三层数据架构系统

快速验证新系统是否正常工作
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.fetcher_v2 import DataFetcherV2
from src.data.database_adapter import DatabaseAdapter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_fetcher_v2():
    """测试 DataFetcherV2"""
    logger.info("\n" + "="*60)
    logger.info("测试 1: DataFetcherV2 初始化")
    logger.info("="*60)
    
    try:
        fetcher = DataFetcherV2()
        logger.info("✅ DataFetcherV2 初始化成功")
        return fetcher
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        return None


def test_fetch_single_stock(fetcher):
    """测试获取单只股票数据"""
    logger.info("\n" + "="*60)
    logger.info("测试 2: 获取单只股票数据 (贵州茅台 600519)")
    logger.info("="*60)
    
    try:
        # 获取最近5天的数据
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
        
        df = fetcher.fetch_history('600519', start_date=start_date, end_date=end_date)
        
        if df is not None and not df.empty:
            logger.info(f"✅ 获取成功，共 {len(df)} 条记录")
            logger.info(f"\n数据预览:\n{df.head()}")
            return df
        else:
            logger.warning("⚠️ 返回数据为空")
            return None
            
    except Exception as e:
        logger.error(f"❌ 获取失败: {e}")
        return None


def test_save_to_layers(fetcher, df):
    """测试保存到三层架构"""
    logger.info("\n" + "="*60)
    logger.info("测试 3: 保存到三层架构")
    logger.info("="*60)
    
    if df is None or df.empty:
        logger.warning("⚠️ 没有数据可保存")
        return False
    
    try:
        stats = fetcher.save_stock_data('600519', df)
        
        logger.info("✅ 保存成功")
        logger.info(f"  Raw Layer: {stats['raw']} 条")
        logger.info(f"  Cleaned Layer: {stats['cleaned']} 条有效")
        logger.info(f"  Invalid: {stats['invalid']} 条")
        logger.info(f"  Valid Rate: {stats['valid_rate']*100:.1f}%")
        logger.info(f"  Aggregated Layer: {stats['aggregated']} 条指标")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 保存失败: {e}")
        return False


def test_read_from_adapter():
    """测试通过 DatabaseAdapter 读取数据"""
    logger.info("\n" + "="*60)
    logger.info("测试 4: 通过 DatabaseAdapter 读取数据")
    logger.info("="*60)
    
    try:
        db = DatabaseAdapter()
        
        # 读取日线数据
        df = db.get_daily_data('600519')
        if df is not None and not df.empty:
            logger.info(f"✅ 读取日线数据成功: {len(df)} 条")
            logger.info(f"  日期范围: {df['date'].min()} ~ {df['date'].max()}")
        else:
            logger.warning("⚠️ 日线数据为空")
        
        # 读取技术指标
        indicators = db.get_indicators('600519')
        if indicators is not None and not indicators.empty:
            logger.info(f"✅ 读取技术指标成功: {len(indicators)} 条")
            logger.info(f"  包含指标: {[col for col in indicators.columns if col not in ['date', 'code']][:5]}...")
        else:
            logger.warning("⚠️ 技术指标为空")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 读取失败: {e}")
        return False


def test_data_quality():
    """测试数据质量检查"""
    logger.info("\n" + "="*60)
    logger.info("测试 5: 数据质量检查")
    logger.info("="*60)
    
    try:
        from src.data.layers import CleanedLayer
        
        cleaned = CleanedLayer()
        stats = cleaned.get_stats()
        
        logger.info("✅ 数据质量统计:")
        logger.info(f"  总记录: {stats['daily']['total_records']:,}")
        logger.info(f"  有效记录: {stats['daily']['valid_records']:,}")
        logger.info(f"  停牌记录: {stats['daily']['suspended_records']:,}")
        logger.info(f"  数据质量: {stats['daily']['valid_rate']*100:.1f}%")
        logger.info(f"  股票数: {stats['daily']['total_stocks']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 检查失败: {e}")
        return False


def test_system_stats(fetcher):
    """测试系统统计"""
    logger.info("\n" + "="*60)
    logger.info("测试 6: 系统统计")
    logger.info("="*60)
    
    try:
        stats = fetcher.get_stats()
        
        logger.info("✅ 系统统计:")
        logger.info(f"\n【Raw Layer】")
        logger.info(f"  日线记录: {stats['raw']['daily']['total_records']:,}")
        logger.info(f"  股票数: {stats['raw']['daily']['total_stocks']}")
        
        logger.info(f"\n【Cleaned Layer】")
        logger.info(f"  总记录: {stats['cleaned']['daily']['total_records']:,}")
        logger.info(f"  有效记录: {stats['cleaned']['daily']['valid_records']:,}")
        logger.info(f"  数据质量: {stats['cleaned']['daily']['valid_rate']*100:.1f}%")
        
        logger.info(f"\n【汇总】")
        logger.info(f"  总股票数: {stats['summary']['total_stocks']}")
        logger.info(f"  总记录数: {stats['summary']['total_records']:,}")
        logger.info(f"  有效记录: {stats['summary']['valid_records']:,}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 统计失败: {e}")
        return False


def main():
    """主测试流程"""
    logger.info("\n" + "="*60)
    logger.info("🧪 V2 三层数据架构系统测试")
    logger.info("="*60)
    
    results = []
    
    # 测试 1: 初始化
    fetcher = test_fetcher_v2()
    results.append(('初始化 DataFetcherV2', fetcher is not None))
    
    if fetcher is None:
        logger.error("\n❌ 初始化失败，无法继续测试")
        return
    
    # 测试 2: 获取数据
    df = test_fetch_single_stock(fetcher)
    results.append(('获取单只股票数据', df is not None))
    
    # 测试 3: 保存数据
    if df is not None:
        save_ok = test_save_to_layers(fetcher, df)
        results.append(('保存到三层架构', save_ok))
    
    # 测试 4: 读取数据
    read_ok = test_read_from_adapter()
    results.append(('通过 Adapter 读取', read_ok))
    
    # 测试 5: 数据质量
    quality_ok = test_data_quality()
    results.append(('数据质量检查', quality_ok))
    
    # 测试 6: 系统统计
    stats_ok = test_system_stats(fetcher)
    results.append(('系统统计', stats_ok))
    
    # 汇总结果
    logger.info("\n" + "="*60)
    logger.info("📊 测试结果汇总")
    logger.info("="*60)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"{status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    logger.info("\n" + "="*60)
    logger.info(f"总计: {passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        logger.info("🎉 所有测试通过！V2 系统运行正常")
    else:
        logger.warning(f"⚠️ {total_count - passed_count} 个测试失败")
    
    logger.info("="*60)


if __name__ == "__main__":
    main()
