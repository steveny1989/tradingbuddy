#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据安全性
Test Data Safety

验证：
1. API返回不全时不会丢失历史数据
2. 重复插入不会产生重复记录
3. UPSERT逻辑正确工作
"""
import pandas as pd
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_data_safety():
    """测试数据安全性"""
    
    # 创建临时测试数据库
    test_db = "data/test_safety.db"
    Path(test_db).unlink(missing_ok=True)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_test (
            date TEXT PRIMARY KEY,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL
        )
    """)
    
    logger.info("="*80)
    logger.info("数据安全性测试")
    logger.info("="*80)
    
    # 测试1: 初始数据插入
    logger.info("\n【测试1: 初始数据插入】")
    initial_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'open': [10.0, 10.5, 11.0, 10.8, 11.2],
        'close': [10.5, 11.0, 10.8, 11.2, 11.5],
        'high': [10.6, 11.2, 11.1, 11.3, 11.6],
        'low': [9.9, 10.4, 10.7, 10.7, 11.0],
        'volume': [1000, 1100, 1200, 1300, 1400],
        'amount': [10500, 11550, 13200, 14560, 16100]
    })
    
    for _, row in initial_data.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO daily_test 
            (date, open, close, high, low, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM daily_test")
    count = cursor.fetchone()[0]
    logger.info(f"初始数据: {count} 条记录")
    
    # 测试2: 模拟API返回不全（只返回最新2天）
    logger.info("\n【测试2: API返回不全（只返回最新2天）】")
    partial_data = pd.DataFrame({
        'date': ['2024-01-04', '2024-01-05'],
        'open': [10.8, 11.2],
        'close': [11.2, 11.5],
        'high': [11.3, 11.6],
        'low': [10.7, 11.0],
        'volume': [1300, 1400],
        'amount': [14560, 16100]
    })
    
    # 使用INSERT OR REPLACE（不会删除旧数据）
    for _, row in partial_data.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO daily_test 
            (date, open, close, high, low, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM daily_test")
    count = cursor.fetchone()[0]
    logger.info(f"更新后数据: {count} 条记录")
    
    if count == 5:
        logger.info("✅ 通过: 历史数据未丢失")
    else:
        logger.error(f"❌ 失败: 预期5条，实际{count}条")
    
    # 测试3: 重复插入相同数据
    logger.info("\n【测试3: 重复插入相同数据】")
    duplicate_data = pd.DataFrame({
        'date': ['2024-01-03', '2024-01-04', '2024-01-05'],
        'open': [11.0, 10.8, 11.2],
        'close': [10.8, 11.2, 11.5],
        'high': [11.1, 11.3, 11.6],
        'low': [10.7, 10.7, 11.0],
        'volume': [1200, 1300, 1400],
        'amount': [13200, 14560, 16100]
    })
    
    for _, row in duplicate_data.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO daily_test 
            (date, open, close, high, low, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM daily_test")
    count = cursor.fetchone()[0]
    logger.info(f"重复插入后: {count} 条记录")
    
    if count == 5:
        logger.info("✅ 通过: 没有产生重复记录")
    else:
        logger.error(f"❌ 失败: 预期5条，实际{count}条")
    
    # 测试4: 更新现有数据
    logger.info("\n【测试4: 更新现有数据（价格修正）】")
    
    # 查询更新前的数据
    cursor.execute("SELECT close FROM daily_test WHERE date = '2024-01-03'")
    old_close = cursor.fetchone()[0]
    logger.info(f"更新前 2024-01-03 收盘价: {old_close}")
    
    # 模拟价格修正（前复权调整）
    updated_data = pd.DataFrame({
        'date': ['2024-01-03'],
        'open': [11.1],  # 修正后的价格
        'close': [10.9],
        'high': [11.2],
        'low': [10.8],
        'volume': [1200],
        'amount': [13200]
    })
    
    for _, row in updated_data.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO daily_test 
            (date, open, close, high, low, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
    
    conn.commit()
    
    # 查询更新后的数据
    cursor.execute("SELECT close FROM daily_test WHERE date = '2024-01-03'")
    new_close = cursor.fetchone()[0]
    logger.info(f"更新后 2024-01-03 收盘价: {new_close}")
    
    cursor.execute("SELECT COUNT(*) FROM daily_test")
    count = cursor.fetchone()[0]
    
    if count == 5 and new_close == 10.9:
        logger.info("✅ 通过: 数据正确更新，无重复")
    else:
        logger.error(f"❌ 失败: 预期5条记录且收盘价10.9，实际{count}条记录，收盘价{new_close}")
    
    # 测试5: 对比不安全的方法（if_exists='replace'）
    logger.info("\n【测试5: 对比不安全的方法】")
    
    # 创建另一个测试表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_test_unsafe (
            date TEXT PRIMARY KEY,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL
        )
    """)
    
    # 插入初始数据
    initial_data.to_sql('daily_test_unsafe', conn, if_exists='replace', index=False)
    cursor.execute("SELECT COUNT(*) FROM daily_test_unsafe")
    count1 = cursor.fetchone()[0]
    logger.info(f"不安全方法 - 初始数据: {count1} 条")
    
    # 模拟API返回不全
    partial_data.to_sql('daily_test_unsafe', conn, if_exists='replace', index=False)
    cursor.execute("SELECT COUNT(*) FROM daily_test_unsafe")
    count2 = cursor.fetchone()[0]
    logger.info(f"不安全方法 - API返回不全后: {count2} 条")
    
    if count2 < count1:
        logger.error(f"❌ 不安全方法导致数据丢失: {count1} -> {count2} (丢失{count1-count2}条)")
    
    # 显示最终数据
    logger.info("\n【最终数据验证】")
    df_safe = pd.read_sql("SELECT * FROM daily_test ORDER BY date", conn)
    logger.info(f"\n安全方法最终数据 ({len(df_safe)}条):")
    logger.info(df_safe.to_string(index=False))
    
    df_unsafe = pd.read_sql("SELECT * FROM daily_test_unsafe ORDER BY date", conn)
    logger.info(f"\n不安全方法最终数据 ({len(df_unsafe)}条):")
    logger.info(df_unsafe.to_string(index=False))
    
    # 清理
    conn.close()
    Path(test_db).unlink()
    
    logger.info("\n" + "="*80)
    logger.info("测试完成")
    logger.info("="*80)
    logger.info("\n结论:")
    logger.info("✅ INSERT OR REPLACE 方法安全可靠")
    logger.info("❌ if_exists='replace' 方法存在数据丢失风险")


if __name__ == "__main__":
    test_data_safety()
