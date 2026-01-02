#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查新创建的表结构
"""
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def inspect_table(cursor, table_name):
    """检查表结构"""
    print(f"\n{'=' * 80}")
    print(f"表: {table_name}")
    print('=' * 80)
    
    # 获取列信息
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("\n列信息:")
    print(f"{'序号':<6} {'列名':<30} {'类型':<15} {'非空':<6} {'默认值':<15} {'主键':<6}")
    print('-' * 80)
    for col in columns:
        cid, name, type_, notnull, dflt_value, pk = col
        print(f"{cid:<6} {name:<30} {type_:<15} {'是' if notnull else '否':<6} {str(dflt_value or ''):<15} {'是' if pk else '否':<6}")
    
    # 获取索引信息
    cursor.execute(f"""
        SELECT name, sql FROM sqlite_master 
        WHERE type='index' AND tbl_name=?
    """, (table_name,))
    indexes = cursor.fetchall()
    
    if indexes:
        print("\n索引信息:")
        for idx_name, idx_sql in indexes:
            if idx_sql:  # 跳过自动创建的索引
                print(f"  - {idx_name}")
                print(f"    {idx_sql}")


def main():
    db_path = "data/a_share.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("数据库新表结构检查")
    print("=" * 80)
    
    # 检查新表
    tables = ['strategy_signals', 'scan_results', 'scan_tasks']
    
    for table in tables:
        inspect_table(cursor, table)
    
    # 检查 market_cap_data 表
    print(f"\n{'=' * 80}")
    print("market_cap_data 表扩展检查")
    print('=' * 80)
    
    cursor.execute("PRAGMA table_info(market_cap_data)")
    columns = cursor.fetchall()
    
    print("\n列信息:")
    for col in columns:
        cid, name, type_, notnull, dflt_value, pk = col
        if name == 'industry':
            print(f"  ✅ {name} ({type_}) - 新增列")
        else:
            print(f"     {name} ({type_})")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
