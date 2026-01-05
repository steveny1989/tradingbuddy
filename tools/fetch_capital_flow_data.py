#!/usr/bin/env python3
"""
资金流向数据获取工具
用于定期更新北向资金、主力资金流向、龙虎榜数据
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.capital_flow_fetcher import CapitalFlowFetcher
from datetime import datetime, timedelta
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_all_data(fetcher: CapitalFlowFetcher):
    """更新所有资金流向数据"""
    logger.info("=" * 60)
    logger.info("开始更新资金流向数据")
    logger.info("=" * 60)
    
    # 1. 更新今日资金流向排名
    logger.info("\n[1/2] 更新今日资金流向排名...")
    success = fetcher.update_daily_capital_flow()
    if success:
        logger.info("✅ 资金流向数据更新成功")
    else:
        logger.warning("⚠️ 资金流向数据更新失败")
    
    # 2. 更新龙虎榜数据（昨日）
    logger.info("\n[2/2] 更新龙虎榜数据...")
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    success = fetcher.update_daily_dragon_tiger(yesterday)
    if success:
        logger.info("✅ 龙虎榜数据更新成功")
    else:
        logger.warning("⚠️ 龙虎榜数据更新失败（可能是周末或节假日）")
    
    logger.info("\n" + "=" * 60)
    logger.info("数据更新完成！")
    logger.info("=" * 60)


def update_northbound_for_stocks(fetcher: CapitalFlowFetcher, symbols: list):
    """更新指定股票的北向资金数据"""
    logger.info("=" * 60)
    logger.info(f"开始更新 {len(symbols)} 只股票的北向资金数据")
    logger.info("=" * 60)
    
    results = fetcher.batch_update_northbound(symbols)
    
    logger.info("\n更新结果:")
    logger.info(f"  成功: {results['success']} 只")
    logger.info(f"  无数据: {results['no_data']} 只")
    logger.info(f"  失败: {results['failed']} 只")


def update_top_stocks_northbound(fetcher: CapitalFlowFetcher, top_n: int = 100):
    """更新市值前N的股票的北向资金数据"""
    import sqlite3
    
    logger.info(f"获取市值前 {top_n} 的股票...")
    
    conn = sqlite3.connect(fetcher.db_path)
    cursor = conn.cursor()
    
    # 获取市值最大的N只股票
    query = """
    SELECT code FROM market_cap_data 
    WHERE total_cap IS NOT NULL 
    ORDER BY total_cap DESC 
    LIMIT ?
    """
    cursor.execute(query, (top_n,))
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    logger.info(f"找到 {len(symbols)} 只股票")
    
    if symbols:
        update_northbound_for_stocks(fetcher, symbols)


def main():
    parser = argparse.ArgumentParser(description='资金流向数据获取工具')
    parser.add_argument('--mode', type=str, default='all',
                        choices=['all', 'flow', 'dragon', 'northbound'],
                        help='更新模式: all=全部, flow=资金流向, dragon=龙虎榜, northbound=北向资金')
    parser.add_argument('--stocks', type=str, nargs='+',
                        help='指定股票代码（用于北向资金更新）')
    parser.add_argument('--top', type=int, default=100,
                        help='更新市值前N的股票的北向资金（默认100）')
    parser.add_argument('--date', type=str,
                        help='指定日期（YYYY-MM-DD，用于龙虎榜）')
    
    args = parser.parse_args()
    
    fetcher = CapitalFlowFetcher()
    
    if args.mode == 'all':
        # 更新所有数据
        update_all_data(fetcher)
        
    elif args.mode == 'flow':
        # 只更新资金流向
        logger.info("更新今日资金流向...")
        success = fetcher.update_daily_capital_flow()
        if success:
            logger.info("✅ 更新成功")
        else:
            logger.error("❌ 更新失败")
            
    elif args.mode == 'dragon':
        # 只更新龙虎榜
        date = args.date or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        logger.info(f"更新 {date} 的龙虎榜数据...")
        success = fetcher.update_daily_dragon_tiger(date)
        if success:
            logger.info("✅ 更新成功")
        else:
            logger.error("❌ 更新失败")
            
    elif args.mode == 'northbound':
        # 更新北向资金
        if args.stocks:
            # 更新指定股票
            update_northbound_for_stocks(fetcher, args.stocks)
        else:
            # 更新市值前N的股票
            update_top_stocks_northbound(fetcher, args.top)


if __name__ == "__main__":
    main()
