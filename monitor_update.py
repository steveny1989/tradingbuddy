#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""监控更新进度"""
import sqlite3
import time
from datetime import datetime

def monitor():
    """持续监控更新进度"""
    print("="*60)
    print("📊 实时监控数据更新")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n按 Ctrl+C 停止监控\n")
    
    last_count = 0
    
    try:
        while True:
            conn = sqlite3.connect('data/raw/daily_raw.db')
            cursor = conn.cursor()
            
            # 查询今天的数据量
            cursor.execute("""
                SELECT COUNT(*) 
                FROM daily_raw 
                WHERE date = '2026-01-05'
            """)
            current_count = cursor.fetchone()[0]
            conn.close()
            
            # 计算增量
            delta = current_count - last_count
            
            # 显示进度
            timestamp = datetime.now().strftime('%H:%M:%S')
            if delta > 0:
                print(f"[{timestamp}] 📈 2026-01-05: {current_count:,} 条 (+{delta})")
            else:
                print(f"[{timestamp}] ⏸️  2026-01-05: {current_count:,} 条 (无变化)")
            
            last_count = current_count
            
            # 等待 10 秒
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("✅ 监控已停止")
        print(f"最终数据量: {last_count:,} 条")
        print("="*60)

if __name__ == "__main__":
    monitor()
