#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试全球指数数据获取
"""
import akshare as ak
import pandas as pd

# 测试不同的指数名称
test_symbols = [
    '道琼斯',
    '标普500', 
    '纳斯达克',
    '日经225',
    '英国富时100',
]

print("测试 akshare 全球指数数据获取\n")
print("=" * 80)

for symbol in test_symbols:
    print(f"\n测试指数: {symbol}")
    print("-" * 80)
    
    try:
        df = ak.index_global_hist_em(symbol=symbol)
        
        if df.empty:
            print(f"❌ {symbol} 返回数据为空")
        else:
            print(f"✅ {symbol} 获取成功")
            print(f"数据行数: {len(df)}")
            print(f"列名: {df.columns.tolist()}")
            print(f"\n最新5条数据:")
            print(df.head())
            
            # 检查数据是否有效
            if '收盘' in df.columns:
                latest_close = df.iloc[0]['收盘']
                print(f"\n最新收盘价: {latest_close}")
                if latest_close == 0:
                    print("⚠️  警告: 收盘价为0")
            
    except Exception as e:
        print(f"❌ {symbol} 获取失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
