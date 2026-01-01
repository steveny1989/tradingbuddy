#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动数据更新服务
在每个交易日后自动更新数据

使用方法：
1. 命令行运行：python3 src/app/auto_update.py
2. 作为服务运行：使用 systemd 或 cron
3. 定时任务：每天收盘后自动运行
"""
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.database import StockDatabase
from src.data.fetcher import DataFetcher
from src.config.settings import DB_PATH

# 配置日志
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'auto_update_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def is_trading_day(date_str: str = None, db: StockDatabase = None) -> bool:
    """
    检查指定日期是否是交易日
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD 或 YYYYMMDD)，None表示今天
        db: 数据库实例（用于查询指数数据）
    
    Returns:
        True表示是交易日，False表示不是
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 统一日期格式为 YYYY-MM-DD
    if len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    
    # 转换为datetime对象
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        logger.error(f"日期格式错误: {date_str}")
        return False
    
    # 检查是否是周末
    weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
    if weekday >= 5:  # 周六(5)或周日(6)
        logger.info(f"{date_str} 是周末，不是交易日")
        return False
    
    # 如果有数据库，检查是否有交易数据
    if db:
        try:
            # 查询上证指数是否有该日数据
            df = db.get_daily_data('sh.000001', start_date=date_str, end_date=date_str)
            if not df.empty:
                logger.info(f"{date_str} 是交易日（上证指数有数据）")
                return True
            else:
                logger.info(f"{date_str} 不是交易日（上证指数无数据，可能是节假日）")
                return False
        except Exception as e:
            logger.warning(f"检查交易日失败: {e}，默认返回False")
            return False
    
    # 如果没有数据库，仅根据周末判断
    return True


def run_auto_update(date: str = None, check_trading_day: bool = True):
    """
    运行自动更新
    
    Args:
        date: 更新日期（YYYYMMDD格式），None表示今天
        check_trading_day: 是否检查是否是交易日
    """
    logger.info("="*80)
    logger.info("🚀 自动数据更新服务启动")
    logger.info("="*80)
    
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    
    date_display = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    logger.info(f"更新日期: {date_display}")
    
    db = StockDatabase(DB_PATH)
    fetcher = DataFetcher(db)
    
    try:
        # 检查是否是交易日
        if check_trading_day:
            if not is_trading_day(date_display, db):
                logger.info(f"⚠️  {date_display} 不是交易日，跳过更新")
                return {
                    'success': False,
                    'reason': 'not_trading_day',
                    'message': f'{date_display} 不是交易日'
                }
        
        # 执行更新
        logger.info(f"开始增量更新...")
        fetcher.update_daily(date=date, check_adjustment=True)
        
        logger.info("="*80)
        logger.info("✅ 自动更新完成")
        logger.info("="*80)
        
        return {
            'success': True,
            'date': date,
            'message': '更新成功'
        }
        
    except Exception as e:
        logger.error(f"❌ 自动更新失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'message': '更新失败'
        }
    finally:
        db.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动数据更新服务')
    parser.add_argument('--date', help='指定日期 (格式: YYYYMMDD)，默认今天')
    parser.add_argument('--force', action='store_true', help='强制更新（不检查是否是交易日）')
    parser.add_argument('--check-trading-day', action='store_true', default=True,
                       help='检查是否是交易日（默认启用）')
    parser.add_argument('--no-check-trading-day', dest='check_trading_day', 
                       action='store_false', help='不检查是否是交易日')
    
    args = parser.parse_args()
    
    result = run_auto_update(
        date=args.date,
        check_trading_day=args.check_trading_day and not args.force
    )
    
    # 返回退出码（0=成功，1=失败）
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()

