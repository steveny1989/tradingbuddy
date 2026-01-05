#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据更新进度"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.layers import RawLayer, CleanedLayer, AggregatedLayer
import sqlite3

def check_progress():
    """检查三层架构的数据进度"""
    print("="*60)
    print("📊 数据更新进度检查")
    print("="*60)
    
    # 检查 Raw Layer
    print("\n1️⃣ Raw Layer (data/raw/daily_raw.db)")
    raw = RawLayer()
    raw_stats = raw.get_stats()
    print(f"   总记录数: {raw_stats['daily']['total_records']:,}")
    print(f"   股票数量: {raw_stats['daily']['total_stocks']}")
    
    # 检查最新日期的数据
    conn = sqlite3.connect('data/raw/daily_raw.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, COUNT(*) as count 
        FROM daily_raw 
        WHERE date >= '2026-01-04'
        GROUP BY date 
        ORDER BY date DESC
    """)
    print("\n   最近日期统计:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]:,} 条记录")
    conn.close()
    
    # 检查 Cleaned Layer
    print("\n2️⃣ Cleaned Layer (data/cleaned/daily_cleaned.db)")
    cleaned = CleanedLayer()
    cleaned_stats = cleaned.get_stats()
    print(f"   有效记录: {cleaned_stats['daily']['valid_records']:,}")
    print(f"   停牌记录: {cleaned_stats['daily']['suspended_records']:,}")
    print(f"   数据质量: {cleaned_stats['daily']['valid_rate']*100:.1f}%")
    
    conn = sqlite3.connect('data/cleaned/daily_cleaned.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, COUNT(*) as count 
        FROM daily_cleaned 
        WHERE date >= '2026-01-04'
        GROUP BY date 
        ORDER BY date DESC
    """)
    print("\n   最近日期统计:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]:,} 条记录")
    conn.close()
    
    # 检查 Aggregated Layer
    print("\n3️⃣ Aggregated Layer (data/aggregated/indicators.db)")
    agg = AggregatedLayer()
    
    conn = sqlite3.connect('data/aggregated/indicators.db')
    cursor = conn.cursor()
    
    # 检查总记录数
    cursor.execute("SELECT COUNT(*) FROM technical_indicators")
    total = cursor.fetchone()[0]
    print(f"   总指标记录: {total:,}")
    
    # 检查最新日期
    cursor.execute("""
        SELECT date, COUNT(*) as count 
        FROM technical_indicators 
        WHERE date >= '2026-01-04'
        GROUP BY date 
        ORDER BY date DESC
    """)
    print("\n   最近日期统计:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]:,} 条记录")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ 进度检查完成")
    print("="*60)

if __name__ == "__main__":
    check_progress()
