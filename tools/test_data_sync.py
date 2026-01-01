#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据同步功能
Test Data Synchronization
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import StockDatabase
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def test_data_sync():
    """测试数据同步到统一表"""
    
    db = StockDatabase()
    
    print("\n" + "="*80)
    print("数据同步功能测试")
    print("="*80)
    
    # 测试股票
    test_code = 'sh.600000'
    
    # 1. 查询统一表中该股票的记录数
    print(f"\n【步骤1: 查询统一表现有数据】")
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM daily_data WHERE code = ?", (test_code,))
    count_before = cursor.fetchone()[0]
    print(f"统一表中 {test_code} 的记录数: {count_before}")
    
    # 2. 查询分表中该股票的记录数
    print(f"\n【步骤2: 查询分表数据】")
    df_original = db.get_daily_data(test_code)
    print(f"分表中 {test_code} 的记录数: {len(df_original)}")
    
    # 3. 模拟新增数据（添加一条测试数据）
    print(f"\n【步骤3: 写入新数据】")
    test_data = pd.DataFrame([{
        'date': '2025-01-01',
        'open': 10.0,
        'close': 10.5,
        'high': 10.8,
        'low': 9.9,
        'volume': 1000000,
        'amount': 10500000,
        'pct_chg': 5.0,
        'turnover': 1.5
    }])
    
    # 写入数据（会自动同步到统一表）
    db.save_daily_data(test_code, test_data, sync_to_unified=True)
    print(f"✅ 写入1条测试数据到分表和统一表")
    
    # 4. 验证分表数据
    print(f"\n【步骤4: 验证分表数据】")
    df_after = db.get_daily_data(test_code)
    print(f"分表中 {test_code} 的记录数: {len(df_after)}")
    
    # 5. 验证统一表数据
    print(f"\n【步骤5: 验证统一表数据】")
    cursor.execute("SELECT COUNT(*) FROM daily_data WHERE code = ?", (test_code,))
    count_after = cursor.fetchone()[0]
    print(f"统一表中 {test_code} 的记录数: {count_after}")
    
    # 6. 验证同步是否成功
    print(f"\n【步骤6: 验证同步结果】")
    if count_after == count_before + 1:
        print(f"✅ 同步成功！统一表新增1条记录")
    elif count_after == count_before:
        print(f"⚠️  统一表记录数未变化（可能是重复数据）")
    else:
        print(f"❌ 同步异常！预期 {count_before + 1}，实际 {count_after}")
    
    # 7. 查询统一表中的测试数据
    print(f"\n【步骤7: 查询统一表中的测试数据】")
    cursor.execute("""
        SELECT * FROM daily_data 
        WHERE code = ? AND date = '2025-01-01'
    """, (test_code,))
    result = cursor.fetchone()
    
    if result:
        print(f"✅ 在统一表中找到测试数据:")
        print(f"   日期: {result[1]}, 收盘价: {result[3]}")
    else:
        print(f"❌ 未在统一表中找到测试数据")
    
    # 8. 清理测试数据
    print(f"\n【步骤8: 清理测试数据】")
    cursor.execute(f"DELETE FROM daily_{test_code.replace('.', '_')} WHERE date = '2025-01-01'")
    cursor.execute("DELETE FROM daily_data WHERE code = ? AND date = '2025-01-01'", (test_code,))
    db.conn.commit()
    print(f"✅ 测试数据已清理")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
    
    db.close()


def test_batch_sync():
    """测试批量数据同步"""
    
    db = StockDatabase()
    
    print("\n" + "="*80)
    print("批量数据同步测试")
    print("="*80)
    
    # 测试股票列表
    test_codes = ['sh.600000', 'sz.000001', 'sz.000002']
    
    for code in test_codes:
        print(f"\n测试 {code}...")
        
        # 从分表读取数据
        df = db.get_daily_data(code)
        
        if df.empty:
            print(f"  ⚠️  {code} 无数据")
            continue
        
        # 取最近5条数据进行同步测试
        df_test = df.tail(5)
        
        # 同步到统一表
        db._sync_to_unified_table(code, df_test)
        
        # 验证
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM daily_data WHERE code = ?", (code,))
        count = cursor.fetchone()[0]
        
        print(f"  ✅ {code}: 分表 {len(df)} 条, 统一表 {count} 条")
    
    db.conn.commit()
    
    print("\n" + "="*80)
    print("批量同步测试完成")
    print("="*80)
    
    db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试数据同步功能')
    parser.add_argument('--batch', action='store_true', help='批量同步测试')
    
    args = parser.parse_args()
    
    if args.batch:
        test_batch_sync()
    else:
        test_data_sync()
