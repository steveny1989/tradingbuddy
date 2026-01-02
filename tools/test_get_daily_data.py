#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 get_daily_data 方法
Test get_daily_data method
"""
from src.data.database import StockDatabase

def test_get_daily_data():
    """测试获取日线数据"""
    db = StockDatabase()
    
    # 测试股票代码
    test_codes = [
        'sz.301042',  # 完整格式
        'sz.002548',
        'sh.600000',
        'sz.000001'
    ]
    
    print("=" * 80)
    print("测试 get_daily_data() 方法")
    print("=" * 80)
    
    for code in test_codes:
        print(f"\n测试股票: {code}")
        print("-" * 80)
        
        # 测试完整代码格式
        df = db.get_daily_data(code)
        print(f"  完整代码 '{code}': {len(df)} 条记录")
        
        if not df.empty:
            print(f"  日期范围: {df['date'].min()} ~ {df['date'].max()}")
            print(f"  最新数据:")
            latest = df.iloc[-1]
            print(f"    日期: {latest['date']}")
            print(f"    收盘价: {latest['close']:.2f}")
            print(f"    成交量: {latest['volume']:.0f}")
        
        # 测试不带前缀的代码（应该失败）
        code_without_prefix = code.split('.')[1]
        df2 = db.get_daily_data(code_without_prefix)
        print(f"  不带前缀 '{code_without_prefix}': {len(df2)} 条记录 {'❌ 错误' if df2.empty else '✅ 正确'}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    
    db.close()


if __name__ == '__main__':
    test_get_daily_data()
