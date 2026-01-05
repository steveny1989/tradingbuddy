# -*- coding: utf-8 -*-
"""主程序 - A股数据采集系统"""
import logging
import argparse
from datetime import datetime
from src.data.database import StockDatabase
from src.data.fetcher import DataFetcher
from src.config.settings import DB_PATH, START_DATE

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/data_sync_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库"""
    logger.info("="*60)
    logger.info("🚀 A股数据采集系统启动")
    logger.info("="*60)
    
    db = StockDatabase(DB_PATH)
    fetcher = DataFetcher(db)
    
    return db, fetcher


def download_all(start_date: str = START_DATE, force: bool = False):
    """下载全市场数据"""
    db, fetcher = init_database()
    
    try:
        # 第一步：获取股票列表
        logger.info("\n📋 第一步：获取股票列表")
        stock_list = fetcher.fetch_stock_list()
        logger.info(f"✅ 股票列表获取完成: {len(stock_list)} 只")
        
        # 第二步：批量下载历史数据
        logger.info(f"\n📊 第二步：批量下载历史数据")
        logger.info(f"数据范围: {start_date} ~ {datetime.now().strftime('%Y%m%d')}")
        
        result = fetcher.batch_fetch_all(start_date=start_date, force_update=force)
        
        # 第三步：显示统计信息
        logger.info("\n📈 第三步：数据库统计")
        stats = db.get_statistics()
        logger.info(f"总股票数: {stats['total_stocks']}")
        logger.info(f"已下载: {stats['downloaded_stocks']}")
        logger.info(f"完成度: {stats['completion_rate']}")
        logger.info(f"总记录数: {stats['total_records']}")
        logger.info(f"平均每只股票: {stats['avg_records_per_stock']} 条记录")
        
        logger.info("\n✨ 全市场数据下载完成！")
        
    except Exception as e:
        logger.error(f"❌ 下载过程出错: {e}")
        raise
    finally:
        db.close()


def update_daily(date: str = None):
    """每日增量更新"""
    db, fetcher = init_database()
    
    try:
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"\n🔄 开始每日增量更新: {date}")
        fetcher.update_daily(date)
        
        # 显示统计信息
        stats = db.get_statistics()
        logger.info(f"\n📊 更新后统计:")
        logger.info(f"总记录数: {stats['total_records']}")
        
        logger.info("\n✅ 每日更新完成！")
        
    except Exception as e:
        logger.error(f"❌ 更新过程出错: {e}")
        raise
    finally:
        db.close()


def show_status():
    """显示数据库状态"""
    db = StockDatabase(DB_PATH)
    
    try:
        logger.info("\n" + "="*60)
        logger.info("📊 数据库状态报告")
        logger.info("="*60)
        
        # 基本统计
        stats = db.get_statistics()
        logger.info(f"\n【基本信息】")
        logger.info(f"  总股票数: {stats['total_stocks']}")
        logger.info(f"  已下载: {stats['downloaded_stocks']}")
        logger.info(f"  完成度: {stats['completion_rate']}")
        logger.info(f"  总记录数: {stats['total_records']:,}")
        logger.info(f"  平均每只: {stats['avg_records_per_stock']} 条")
        
        # 同步状态
        sync_status = db.get_sync_status()
        if not sync_status.empty:
            logger.info(f"\n【同步状态】")
            success_count = len(sync_status[sync_status['status'] == 'success'])
            logger.info(f"  成功: {success_count}")
            logger.info(f"  失败: {len(sync_status) - success_count}")
            
            # 显示最近更新
            recent = sync_status.head(5)
            logger.info(f"\n【最近更新】")
            for _, row in recent.iterrows():
                logger.info(f"  {row['code']}: {row['total_records']} 条 | {row['last_sync_date']}")
        
        logger.info("\n" + "="*60)
        
    finally:
        db.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='A股数据采集系统')
    parser.add_argument('action', choices=['download', 'update', 'status'], 
                       help='操作类型: download(全量下载) | update(增量更新) | status(查看状态)')
    parser.add_argument('--start-date', default=START_DATE, 
                       help='开始日期 (格式: YYYYMMDD)')
    parser.add_argument('--date', help='指定日期 (格式: YYYYMMDD)')
    parser.add_argument('--force', action='store_true', 
                       help='强制重新下载')
    
    args = parser.parse_args()
    
    # 创建日志目录
    import os
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    if args.action == 'download':
        download_all(start_date=args.start_date, force=args.force)
    elif args.action == 'update':
        update_daily(date=args.date)
    elif args.action == 'status':
        show_status()


if __name__ == "__main__":
    main()
