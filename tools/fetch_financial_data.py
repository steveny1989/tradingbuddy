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
    parser.add_argument('--force', action='store_true', help='强制更新（忽略已有数据）')
    parser.add_argument('--resume-from', type=str, help='从指定股票代码继续（断点续传）')
    parser.add_argument('--retry-failed', type=str, help='从失败列表文件重试')
    parser.add_argument('--codes', type=str, help='指定股票代码列表（逗号分隔，如 600000,000001）')
    
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
            
            if result.success:
                print(f"\n✅ {args.code} 财务数据下载完成！")
                
                # 显示状态概览
                print(f"  - 资产负债表: {result.balance_sheet_status.value}")
                print(f"  - 利润表: {result.income_statement_status.value}")
                print(f"  - 现金流量表: {result.cash_flow_status.value}")
                print(f"  - 财务指标: {result.indicators_status.value}")
            else:
                print(f"\n❌ {args.code} 财务数据下载失败")
                if result.error_type:
                    print(f"  - 错误类型: {result.error_type.value}")
                if result.error_details:
                    print(f"  - 错误详情: {result.error_details}")
        
        elif args.retry_failed:
            # 从失败列表重试
            print(f"\n🔄 从失败列表重试: {args.retry_failed}")
            result = fetcher.retry_failed_stocks(args.retry_failed)
            
            print(f"\n✅ 重试完成！")
            print(f"  - 总数: {result.total}")
            print(f"  - 成功: {result.success}")
            print(f"  - 失败: {result.failed}")
            print(f"  - 成功率: {result.success_rate}%")
            
            if result.report_file:
                print(f"\n📄 报告文件: {result.report_file}")
            if result.failed_list_file:
                print(f"📄 失败列表: {result.failed_list_file}")
        
        elif args.batch:
            # 批量下载
            print("\n🚀 开始批量下载财务数据...")
            
            if args.max:
                print(f"⚠️ 测试模式：仅下载前 {args.max} 只股票")
            
            if args.force:
                print("⚡ 强制更新模式：将更新所有股票")
            
            if args.resume_from:
                print(f"🔄 断点续传：从 {args.resume_from} 继续")
            
            # 处理自定义股票列表
            codes = None
            if args.codes:
                codes = [c.strip() for c in args.codes.split(',')]
                print(f"📋 自定义股票列表：{len(codes)} 只股票")
            
            result = fetcher.batch_fetch_financial_data(
                codes=codes,
                max_stocks=args.max,
                force_update=args.force,
                resume_from=args.resume_from
            )
            
            print(f"\n✅ 批量下载完成！")
            print(f"  - 总数: {result.total}")
            print(f"  - 成功: {result.success}")
            print(f"  - 失败: {result.failed}")
            print(f"  - 成功率: {result.success_rate}%")
            print(f"  - 耗时: {result.elapsed_seconds}秒")
            print(f"  - 平均速度: {result.avg_speed}股票/秒")
            
            if result.error_stats:
                print(f"\n📋 错误统计:")
                for error_type, count in result.error_stats.items():
                    # 如果是ErrorType对象，获取其value
                    error_name = error_type.value if hasattr(error_type, 'value') else str(error_type)
                    print(f"  - {error_name}: {count}")
            
            if result.report_file:
                print(f"\n📄 报告文件: {result.report_file}")
            if result.failed_list_file:
                print(f"📄 失败列表: {result.failed_list_file}")
        
        else:
            parser.print_help()
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
