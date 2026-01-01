#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务数据下载工具
用于批量下载上市公司财务报表和财务指标
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import StockDatabase
from src.data.financial_fetcher import FinancialDataFetcher
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='财务数据下载工具')
    parser.add_argument('--code', type=str, help='单只股票代码（如 600000）')
    parser.add_argument('--batch', action='store_true', help='批量下载全市场')
    parser.add_argument('--max', type=int, help='最大下载数量（用于测试）')
    parser.add_argument('--stats', action='store_true', help='显示财务数据统计')
    
    args = parser.parse_args()
    
    # 初始化数据库和采集器
    db = StockDatabase()
    fetcher = FinancialDataFetcher(db)
    
    try:
        if args.stats:
            # 显示统计信息
            print("\n" + "="*60)
            print("📊 财务数据统计")
            print("="*60)
            
            stats = db.get_financial_statistics()
            
            for table_name, table_stats in stats.items():
                print(f"\n{table_name}:")
                print(f"  - 股票数量: {table_stats['stock_count']}")
                print(f"  - 记录总数: {table_stats['record_count']}")
                if table_stats['stock_count'] > 0:
                    avg = table_stats['record_count'] / table_stats['stock_count']
                    print(f"  - 平均记录数: {avg:.1f}")
            
            print("\n" + "="*60)
        
        elif args.code:
            # 下载单只股票
            print(f"\n🚀 开始下载 {args.code} 的财务数据...")
            result = fetcher.fetch_all_financial_data(args.code, save_to_db=True)
            
            if result['success']:
                print(f"\n✅ {args.code} 财务数据下载完成！")
                
                # 显示数据概览
                if result['balance_sheet'] is not None:
                    print(f"  - 资产负债表: {len(result['balance_sheet'])} 期")
                if result['income_statement'] is not None:
                    print(f"  - 利润表: {len(result['income_statement'])} 期")
                if result['cash_flow'] is not None:
                    print(f"  - 现金流量表: {len(result['cash_flow'])} 期")
                if result['financial_indicators'] is not None:
                    print(f"  - 财务指标: {len(result['financial_indicators'])} 期")
            else:
                print(f"\n❌ {args.code} 财务数据下载失败")
        
        elif args.batch:
            # 批量下载
            print("\n🚀 开始批量下载财务数据...")
            
            if args.max:
                print(f"⚠️ 测试模式：仅下载前 {args.max} 只股票")
            
            result = fetcher.batch_fetch_financial_data(max_stocks=args.max)
            
            print(f"\n✅ 批量下载完成！")
            print(f"  - 总数: {result['total']}")
            print(f"  - 成功: {result['success']}")
            print(f"  - 失败: {result['failed']}")
            print(f"  - 成功率: {result['success']/result['total']*100:.1f}%")
        
        else:
            parser.print_help()
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
