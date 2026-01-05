# -*- coding: utf-8 -*-
"""
主程序 V2 - 使用三层数据架构

使用新的 DataFetcherV2，将数据写入三层架构：
- Raw Layer: 原始数据
- Cleaned Layer: 清洗后的数据  
- Aggregated Layer: 技术指标
"""
import logging
import argparse
from datetime import datetime
import os

from src.data.fetcher_v2 import DataFetcherV2
from src.config.settings import START_DATE

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/data_sync_v2_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def init_fetcher():
    """初始化数据采集器"""
    logger.info("="*60)
    logger.info("🚀 A股数据采集系统 V2 启动")
    logger.info("📦 使用三层数据架构 (Raw → Cleaned → Aggregated)")
    logger.info("="*60)
    
    fetcher = DataFetcherV2()
    return fetcher


def download_all(start_date: str = START_DATE, force: bool = False):
    """下载全市场数据"""
    fetcher = init_fetcher()
    
    try:
        logger.info(f"\n📊 开始全量下载")
        logger.info(f"数据范围: {start_date} ~ {datetime.now().strftime('%Y%m%d')}")
        
        fetcher.batch_fetch_all(start_date=start_date, force_update=force)
        
        logger.info("\n✨ 全市场数据下载完成！")
        
    except Exception as e:
        logger.error(f"❌ 下载过程出错: {e}")
        raise


def update_daily(date: str = None):
    """每日增量更新"""
    fetcher = init_fetcher()
    
    try:
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        fetcher.update_daily(date)
        
    except Exception as e:
        logger.error(f"❌ 更新过程出错: {e}")
        raise


def show_status():
    """显示数据库状态"""
    fetcher = DataFetcherV2()
    
    try:
        logger.info("\n" + "="*60)
        logger.info("📊 三层数据架构状态报告")
        logger.info("="*60)
        
        stats = fetcher.get_stats()
        
        # Raw Layer 统计
        logger.info(f"\n【Raw Layer - 原始数据层】")
        logger.info(f"  日线数据:")
        logger.info(f"    - 总记录: {stats['raw']['daily']['total_records']:,}")
        logger.info(f"    - 股票数: {stats['raw']['daily']['total_stocks']}")
        
        if 'financial' in stats['raw']:
            logger.info(f"  财务数据:")
            logger.info(f"    - 总记录: {stats['raw']['financial']['total_records']:,}")
            logger.info(f"    - 股票数: {stats['raw']['financial']['total_stocks']}")
        
        # Cleaned Layer 统计
        logger.info(f"\n【Cleaned Layer - 清洗数据层】")
        logger.info(f"  日线数据:")
        logger.info(f"    - 总记录: {stats['cleaned']['daily']['total_records']:,}")
        logger.info(f"    - 有效记录: {stats['cleaned']['daily']['valid_records']:,}")
        logger.info(f"    - 停牌记录: {stats['cleaned']['daily']['suspended_records']:,}")
        logger.info(f"    - 数据质量: {stats['cleaned']['daily']['valid_rate']*100:.1f}%")
        logger.info(f"    - 股票数: {stats['cleaned']['daily']['total_stocks']}")
        
        if 'financial' in stats['cleaned']:
            logger.info(f"  财务数据:")
            logger.info(f"    - 总记录: {stats['cleaned']['financial']['total_records']:,}")
            logger.info(f"    - 有效记录: {stats['cleaned']['financial']['valid_records']:,}")
            logger.info(f"    - 平均完整度: {stats['cleaned']['financial']['avg_completeness']*100:.1f}%")
        
        # 汇总
        logger.info(f"\n【汇总】")
        logger.info(f"  总股票数: {stats['summary']['total_stocks']}")
        logger.info(f"  总记录数: {stats['summary']['total_records']:,}")
        logger.info(f"  有效记录: {stats['summary']['valid_records']:,}")
        logger.info(f"  数据质量: {stats['summary']['valid_rate']*100:.1f}%")
        
        logger.info("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {e}")
        raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='A股数据采集系统 V2 (三层架构)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 全量下载（从2023年开始）
  python -m src.app.main_v2 download
  
  # 全量下载（指定开始日期）
  python -m src.app.main_v2 download --start-date 20240101
  
  # 强制重新下载
  python -m src.app.main_v2 download --force
  
  # 每日增量更新（今天）
  python -m src.app.main_v2 update
  
  # 更新指定日期
  python -m src.app.main_v2 update --date 20260105
  
  # 查看数据状态
  python -m src.app.main_v2 status
        """
    )
    
    parser.add_argument(
        'action', 
        choices=['download', 'update', 'status'], 
        help='操作类型: download(全量下载) | update(增量更新) | status(查看状态)'
    )
    parser.add_argument(
        '--start-date', 
        default=START_DATE, 
        help='开始日期 (格式: YYYYMMDD，默认: 20230101)'
    )
    parser.add_argument(
        '--date', 
        help='指定日期 (格式: YYYYMMDD，默认: 今天)'
    )
    parser.add_argument(
        '--force', 
        action='store_true', 
        help='强制重新下载（忽略已有数据）'
    )
    
    args = parser.parse_args()
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/cleaned', exist_ok=True)
    os.makedirs('data/aggregated', exist_ok=True)
    
    # 执行操作
    if args.action == 'download':
        download_all(start_date=args.start_date, force=args.force)
    elif args.action == 'update':
        update_daily(date=args.date)
    elif args.action == 'status':
        show_status()


if __name__ == "__main__":
    main()
