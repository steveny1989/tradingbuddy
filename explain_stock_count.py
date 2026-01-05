#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解释股票数量差异"""
import sqlite3

print("="*60)
print("📊 股票数量分析")
print("="*60)

# 1. 历史累计股票数（包括已退市的）
conn = sqlite3.connect('data/raw/daily_raw.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(DISTINCT code) FROM daily_raw")
total_historical = cursor.fetchone()[0]
print(f"\n1️⃣ 历史累计股票数: {total_historical}")
print("   （包括所有曾经存在过的股票，含已退市）")

# 2. 当前活跃股票数（有最新数据的）
cursor.execute("""
    SELECT COUNT(DISTINCT code) 
    FROM daily_raw 
    WHERE date = '2026-01-05'
""")
active_today = cursor.fetchone()[0]
print(f"\n2️⃣ 2026-01-05 有数据的股票: {active_today}")
print("   （今天实际交易/有数据的股票）")

# 3. 最近一周有数据的股票
cursor.execute("""
    SELECT COUNT(DISTINCT code) 
    FROM daily_raw 
    WHERE date >= '2025-12-30'
""")
recent_active = cursor.fetchone()[0]
print(f"\n3️⃣ 最近一周有数据的股票: {recent_active}")
print("   （最近活跃的股票，包括停牌的）")

# 4. 按日期统计
print("\n4️⃣ 最近几天的股票数量:")
cursor.execute("""
    SELECT date, COUNT(DISTINCT code) as count
    FROM daily_raw
    WHERE date >= '2025-12-30'
    GROUP BY date
    ORDER BY date DESC
""")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]} 只")

conn.close()

print("\n" + "="*60)
print("💡 结论:")
print("="*60)
print(f"• 8460 = 历史上所有股票（含退市）")
print(f"• {active_today} = 今天实际更新的股票")
print(f"• 5793 = AKShare 今天返回的股票列表")
print("\n差异原因：")
print("  - 部分股票停牌/退市")
print("  - 部分股票今天无交易数据")
print("  - 新股上市还未纳入历史数据")
print("="*60)
