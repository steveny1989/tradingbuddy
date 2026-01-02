#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断日线数据问题
Diagnose daily data issues
"""
import sqlite3
from pathlib import Path

def diagnose_daily_data():
    """诊断日线数据问题"""
    db_path = Path("data/a_share.db")
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("日线数据诊断报告")
    print("=" * 80)
    
    # 1. 检查有多少个daily_表
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'daily_%'
        ORDER BY name
    """)
    daily_tables = cursor.fetchall()
    
    print(f"\n1. 找到 {len(daily_tables)} 个日线数据表")
    
    # 2. 随机检查几个表的数据量
    print("\n2. 检查前10个表的数据量:")
    print("-" * 80)
    print(f"{'表名':<30} {'记录数':>10} {'最早日期':<12} {'最晚日期':<12}")
    print("-" * 80)
    
    for table_name, in daily_tables[:10]:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT MIN(date), MAX(date) FROM {table_name}")
        min_date, max_date = cursor.fetchone()
        
        print(f"{table_name:<30} {count:>10} {min_date or 'N/A':<12} {max_date or 'N/A':<12}")
    
    # 3. 检查特定股票（从今日精选中出现的）
    test_codes = ['sz.301042', 'sz.002548', 'sh.600000', 'sz.000001']
    
    print("\n3. 检查特定股票的数据:")
    print("-" * 80)
    print(f"{'股票代码':<15} {'表名':<30} {'表是否存在':<12} {'记录数':>10}")
    print("-" * 80)
    
    for code in test_codes:
        # 转换为表名
        table_name = f"daily_{code.replace('.', '_')}"
        
        # 检查表是否存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        exists = cursor.fetchone() is not None
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{code:<15} {table_name:<30} {'是':<12} {count:>10}")
        else:
            print(f"{code:<15} {table_name:<30} {'否':<12} {0:>10}")
    
    # 4. 检查统一表 daily_data
    print("\n4. 检查统一表 daily_data:")
    print("-" * 80)
    
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='daily_data'"
    )
    unified_exists = cursor.fetchone() is not None
    
    if unified_exists:
        cursor.execute("SELECT COUNT(*) FROM daily_data")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT code) FROM daily_data")
        total_stocks = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(date), MAX(date) FROM daily_data")
        min_date, max_date = cursor.fetchone()
        
        print(f"统一表存在: 是")
        print(f"总记录数: {total_records:,}")
        print(f"股票数量: {total_stocks:,}")
        print(f"日期范围: {min_date} ~ {max_date}")
        
        # 检查特定股票在统一表中的数据
        print("\n   特定股票在统一表中的数据:")
        print("   " + "-" * 76)
        print(f"   {'股票代码':<15} {'记录数':>10} {'最早日期':<12} {'最晚日期':<12}")
        print("   " + "-" * 76)
        
        for code in test_codes:
            # 移除市场前缀
            code_without_prefix = code.split('.')[1] if '.' in code else code
            
            cursor.execute(
                "SELECT COUNT(*), MIN(date), MAX(date) FROM daily_data WHERE code = ?",
                (code_without_prefix,)
            )
            count, min_d, max_d = cursor.fetchone()
            print(f"   {code:<15} {count:>10} {min_d or 'N/A':<12} {max_d or 'N/A':<12}")
    else:
        print(f"统一表存在: 否")
    
    # 5. 检查stock_basic表
    print("\n5. 检查stock_basic表:")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM stock_basic")
    total_stocks = cursor.fetchone()[0]
    print(f"股票列表总数: {total_stocks:,}")
    
    # 检查特定股票是否在stock_basic中
    print("\n   特定股票在stock_basic中:")
    print("   " + "-" * 76)
    print(f"   {'股票代码':<15} {'股票名称':<20} {'市场':<10}")
    print("   " + "-" * 76)
    
    for code in test_codes:
        code_without_prefix = code.split('.')[1] if '.' in code else code
        
        cursor.execute(
            "SELECT name, market FROM stock_basic WHERE code = ?",
            (code_without_prefix,)
        )
        result = cursor.fetchone()
        
        if result:
            name, market = result
            print(f"   {code:<15} {name:<20} {market:<10}")
        else:
            print(f"   {code:<15} {'不存在':<20} {'':<10}")
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)
    
    conn.close()


if __name__ == '__main__':
    diagnose_daily_data()
