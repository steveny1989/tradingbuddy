#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的CLI工具功能
"""
import sys
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


def test_single_stock():
    """测试单只股票下载"""
    print("\n" + "="*60)
    print("测试1: 单只股票下载")
    print("="*60)
    
    db = StockDatabase()
    fetcher = FinancialDataFetcher(db)
    
    try:
        code = "600000"
        print(f"\n🚀 测试下载 {code} 的财务数据...")
        result = fetcher.fetch_all_financial_data(code, save_to_db=True)
        
        print(f"\n结果:")
        print(f"  - 成功: {result.success}")
        print(f"  - 有数据: {result.has_data}")
        print(f"  - 资产负债表: {result.balance_sheet_status.value}")
        print(f"  - 利润表: {result.income_statement_status.value}")
        print(f"  - 现金流量表: {result.cash_flow_status.value}")
        print(f"  - 财务指标: {result.indicators_status.value}")
        
        if result.error_type:
            print(f"  - 错误类型: {result.error_type.value}")
        if result.error_details:
            print(f"  - 错误详情: {result.error_details}")
        
        # 测试get_last_update_time
        last_update = db.get_last_update_time(code)
        print(f"\n最后更新时间: {last_update}")
        
    finally:
        db.close()


def test_batch_download():
    """测试批量下载（小样本）"""
    print("\n" + "="*60)
    print("测试2: 批量下载（3只股票）")
    print("="*60)
    
    db = StockDatabase()
    fetcher = FinancialDataFetcher(db)
    
    try:
        codes = ["600000", "000001", "600519"]
        print(f"\n🚀 测试批量下载 {len(codes)} 只股票...")
        
        result = fetcher.batch_fetch_financial_data(
            codes=codes,
            force_update=True
        )
        
        print(f"\n结果:")
        print(f"  - 总数: {result.total}")
        print(f"  - 成功: {result.success}")
        print(f"  - 失败: {result.failed}")
        print(f"  - 成功率: {result.success_rate}%")
        print(f"  - 耗时: {result.elapsed_seconds}秒")
        print(f"  - 平均速度: {result.avg_speed}股票/秒")
        
        if result.error_stats:
            print(f"\n错误统计:")
            for error_type, count in result.error_stats.items():
                print(f"  - {error_type}: {count}")
        
        if result.report_file:
            print(f"\n报告文件: {result.report_file}")
        if result.failed_list_file:
            print(f"失败列表: {result.failed_list_file}")
        
    finally:
        db.close()


def test_force_update_check():
    """测试force_update检查逻辑"""
    print("\n" + "="*60)
    print("测试3: force_update检查逻辑")
    print("="*60)
    
    db = StockDatabase()
    fetcher = FinancialDataFetcher(db)
    
    try:
        codes = ["600000"]
        
        # 第一次下载（强制更新）
        print(f"\n第一次下载（force_update=True）...")
        result1 = fetcher.batch_fetch_financial_data(
            codes=codes,
            force_update=True
        )
        print(f"成功: {result1.success}, 失败: {result1.failed}")
        
        # 第二次下载（不强制更新，应该跳过）
        print(f"\n第二次下载（force_update=False，应该跳过）...")
        result2 = fetcher.batch_fetch_financial_data(
            codes=codes,
            force_update=False
        )
        print(f"成功: {result2.success}, 失败: {result2.failed}")
        print(f"总数: {result2.total}（应该为0，因为被跳过）")
        
    finally:
        db.close()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 财务数据采集系统测试")
    print("="*60)
    
    try:
        test_single_stock()
        test_batch_download()
        test_force_update_check()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
