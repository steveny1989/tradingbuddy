#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库迁移脚本
验证新表是否正确创建
"""
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.db_migrations import run_migrations


def verify_tables(db_path: str = "data/a_share.db"):
    """验证表是否创建成功"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("验证数据库迁移结果")
    print("=" * 80)
    
    # 检查迁移记录表
    cursor.execute("SELECT * FROM db_migrations ORDER BY version")
    migrations = cursor.fetchall()
    
    print("\n已应用的迁移:")
    for migration in migrations:
        print(f"  版本 {migration[0]}: {migration[1]} (应用于 {migration[2]})")
        print(f"    描述: {migration[3]}")
    
    # 检查新表
    expected_tables = [
        'strategy_signals',
        'scan_results',
        'scan_tasks'
    ]
    
    print("\n检查新表:")
    for table_name in expected_tables:
        cursor.execute(f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        if cursor.fetchone():
            print(f"  ✅ {table_name} 表已创建")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"     列数: {len(columns)}")
            
            # 获取索引
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name=?
            """, (table_name,))
            indexes = cursor.fetchall()
            print(f"     索引数: {len(indexes)}")
        else:
            print(f"  ❌ {table_name} 表未创建")
    
    # 检查 market_cap_data 表的 industry 列
    print("\n检查 market_cap_data 表扩展:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_cap_data'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(market_cap_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'industry' in columns:
            print("  ✅ industry 列已添加")
        else:
            print("  ❌ industry 列未添加")
    else:
        print("  ⚠️  market_cap_data 表不存在（可能尚未创建）")
    
    # 检查索引
    print("\n检查索引:")
    expected_indexes = [
        ('strategy_signals', 'idx_signals_code_date'),
        ('strategy_signals', 'idx_signals_strategy_date'),
        ('strategy_signals', 'idx_signals_score'),
        ('scan_results', 'idx_scan_strategy_date'),
        ('scan_tasks', 'idx_tasks_status'),
    ]
    
    for table_name, index_name in expected_indexes:
        cursor.execute(f"""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name=? AND tbl_name=?
        """, (index_name, table_name))
        
        if cursor.fetchone():
            print(f"  ✅ {index_name} 索引已创建")
        else:
            print(f"  ❌ {index_name} 索引未创建")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("验证完成")
    print("=" * 80)


if __name__ == "__main__":
    print("开始运行数据库迁移...")
    run_migrations()
    
    print("\n验证迁移结果...")
    verify_tables()
