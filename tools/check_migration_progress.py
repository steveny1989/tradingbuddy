#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查迁移进度
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.layers import RawLayer, CleanedLayer
import sqlite3

def main():
    print("\n" + "="*60)
    print("  迁移进度检查")
    print("="*60)
    
    # 检查旧数据库
    old_db = 'data/a_share.db'
    if os.path.exists(old_db):
        with sqlite3.connect(old_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) as total, COUNT(DISTINCT code) as stocks FROM daily_data")
            row = cursor.fetchone()
            old_total = row[0]
            old_stocks = row[1]
            print(f"\n旧数据库 (a_share.db):")
            print(f"  总记录: {old_total:,}")
            print(f"  股票数: {old_stocks}")
    
    # 检查新数据库
    raw = RawLayer()
    cleaned = CleanedLayer()
    
    raw_stats = raw.get_stats()
    cleaned_stats = cleaned.get_stats()
    
    print(f"\nRaw Layer:")
    print(f"  总记录: {raw_stats['daily']['total_records']:,}")
    print(f"  股票数: {raw_stats['daily']['total_stocks']}")
    
    print(f"\nCleaned Layer:")
    print(f"  总记录: {cleaned_stats['daily']['total_records']:,}")
    print(f"  有效记录: {cleaned_stats['daily']['valid_records']:,}")
    print(f"  有效率: {cleaned_stats['daily']['valid_rate']*100:.2f}%")
    print(f"  股票数: {cleaned_stats['daily']['total_stocks']}")
    
    # 计算进度
    if old_stocks > 0:
        progress = cleaned_stats['daily']['total_stocks'] / old_stocks * 100
        print(f"\n迁移进度: {progress:.1f}% ({cleaned_stats['daily']['total_stocks']}/{old_stocks} 只股票)")
        
        if progress < 100:
            remaining = old_stocks - cleaned_stats['daily']['total_stocks']
            print(f"剩余: {remaining} 只股票")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
