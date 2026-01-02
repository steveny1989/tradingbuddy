#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的财务数据采集器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from src.data.database import StockDatabase
from src.data.financial_fetcher import FinancialDataFetcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """测试新的采集器"""
    print("=" * 60)
    print("测试新的财务数据采集器")
    print("=" * 60)
    
    # 初始化数据库和采集器
    db = StockDatabase('data/a_share.db')
    fetcher = FinancialDataFetcher(db)
    
    # 测试单只股票
    print("\n【测试1】单只股票获取 - 600519（茅台）")
    print("-" * 60)
    result = fetcher.fetch_all_financial_data('600519', save_to_db=False)
    
    print(f"\n结果:")
    print(f"  代码: {result.code}")
    print(f"  成功: {result.success}")
    print(f"  有数据: {result.has_data}")
    print(f"  错误类型: {result.error_type}")
    print(f"  错误详情: {result.error_details}")
    print(f"  资产负债表状态: {result.balance_sheet_status.value}")
    print(f"  利润表状态: {result.income_statement_status.value}")
    print(f"  现金流量表状态: {result.cash_flow_status.value}")
    print(f"  财务指标状态: {result.indicators_status.value}")
    
    # 测试批量获取（小样本）
    print("\n【测试2】批量获取 - 前5只股票")
    print("-" * 60)
    batch_result = fetcher.batch_fetch_financial_data(max_stocks=5)
    
    print(f"\n批量结果:")
    print(f"  总计: {batch_result.total}")
    print(f"  成功: {batch_result.success}")
    print(f"  失败: {batch_result.failed}")
    print(f"  成功率: {batch_result.success / batch_result.total * 100:.2f}%")
    print(f"  平均速度: {batch_result.avg_speed:.3f} 股票/秒")
    print(f"  耗时: {(batch_result.end_time - batch_result.start_time).total_seconds():.2f} 秒")
    
    if batch_result.error_stats:
        print(f"\n  错误统计:")
        for error_type, count in batch_result.error_stats.items():
            print(f"    - {error_type.value}: {count}")
    
    if batch_result.failed_stocks:
        print(f"\n  失败股票:")
        for error_type, codes in batch_result.failed_stocks.items():
            print(f"    - {error_type.value}: {codes}")
    
    print(f"\n  报告文件: {batch_result.report_file}")
    print(f"  失败列表: {batch_result.failed_list_file}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
