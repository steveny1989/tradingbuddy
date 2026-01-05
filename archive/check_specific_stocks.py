#!/usr/bin/env python3
"""
Check the specific stocks from the CSV to see their current status
"""

import sqlite3

def check_stock(code):
    """Check a specific stock's current data"""
    conn = sqlite3.connect('data/a_share.db')
    cursor = conn.cursor()
    
    # Convert code format to table name
    table_name = f"daily_{code}"
    
    print(f"\n检查 {code} (表名: {table_name})")
    print("-" * 60)
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name = ?
        """, (table_name,))
        
        if not cursor.fetchone():
            print(f"❌ 表不存在")
            return
        
        # Get latest price
        cursor.execute(f"""
            SELECT close, high, trade_date 
            FROM {table_name} 
            ORDER BY trade_date DESC 
            LIMIT 1
        """)
        latest = cursor.fetchone()
        
        if latest:
            print(f"最新收盘价: ¥{latest[0]:.2f}")
            print(f"最新日期: {latest[2]}")
        else:
            print("❌ 无最新数据")
            return
        
        # Get historical high
        cursor.execute(f"""
            SELECT MAX(high) as max_high, 
                   (SELECT trade_date FROM {table_name} WHERE high = MAX(high) LIMIT 1) as high_date
            FROM {table_name}
        """)
        high_data = cursor.fetchone()
        
        if high_data[0]:
            print(f"历史最高: ¥{high_data[0]:.2f} (日期: {high_data[1]})")
            drop_pct = ((latest[0] - high_data[0]) / high_data[0]) * 100
            print(f"跌幅: {drop_pct:.1f}%")
            
            # Check criteria
            print()
            print(f"现价 < 10? {latest[0] < 10} (现价: {latest[0]:.2f})")
            print(f"历史最高 > 30? {high_data[0] > 30} (最高: {high_data[0]:.2f})")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        conn.close()

# Check all stocks from the CSV
stocks_to_check = [
    'sz.300379',  # 东通退
    'sz.002693',  # *ST双成
    'sh.600818',  # 中路股份
    'sh.688184',  # ST帕瓦
    'sh.600199',  # 金种子酒
    'sz.002129',  # TCL中环
    'sh.603398',  # *ST沐邦
    'unknown.920575',  # 康乐卫士
    'unknown.920680',  # 广道退
    'sz.300799',  # 左江退
    'sz.300630',  # 普利退
    'sz.300280',  # 紫天退
]

print("=" * 80)
print("检查CSV中的12只股票当前状态")
print("=" * 80)

for stock_code in stocks_to_check:
    check_stock(stock_code)

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
