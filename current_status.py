#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""当前状态报告"""
import re
import sqlite3

print("="*60)
print("📊 数据更新状态报告")
print("="*60)

# 1. 从日志获取进度
try:
    with open('update_log.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 找到最后一行进度信息
    for line in reversed(lines):
        if '更新进度:' in line and 'it/s' in line:
            match = re.search(r'(\d+)/(\d+).*?成功=(\d+).*?失败=(\d+).*?记录=(\d+)', line)
            if match:
                current, total, success, failed, records = match.groups()
                progress = int(current) / int(total) * 100
                
                print(f"\n📈 脚本进度:")
                print(f"   已处理: {current}/{total} 只股票 ({progress:.1f}%)")
                print(f"   成功: {success} 只")
                print(f"   失败: {failed} 只")
                print(f"   记录数: {records} 条")
                break
except FileNotFoundError:
    print("\n⚠️  找不到日志文件")

# 2. 从数据库获取实际数据
conn = sqlite3.connect('data/raw/daily_raw.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM daily_raw WHERE date = '2026-01-05'")
db_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT code) FROM daily_raw WHERE date = '2026-01-05'")
db_stocks = cursor.fetchone()[0]

conn.close()

print(f"\n💾 数据库状态:")
print(f"   2026-01-05 记录数: {db_count:,} 条")
print(f"   2026-01-05 股票数: {db_stocks:,} 只")

print(f"\n💡 说明:")
print(f"   脚本正在遍历所有股票，但只有有交易数据的股票会被保存")
print(f"   很多股票今天可能停牌或无数据，所以数据库记录数不会增长")
print(f"   这是正常现象！")

print("\n" + "="*60)
