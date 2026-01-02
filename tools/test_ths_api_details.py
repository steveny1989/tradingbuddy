#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试同花顺API，了解数据结构
"""
import akshare as ak
import pandas as pd

def test_ths_apis():
    """详细测试同花顺API"""
    
    test_code = "600519"
    
    print("="*60)
    print("详细测试同花顺API数据结构")
    print("="*60)
    
    # 1. 财务摘要（按报告期）
    print("\n1. stock_financial_abstract_ths - 按报告期")
    try:
        df = ak.stock_financial_abstract_ths(symbol=test_code, indicator="按报告期")
        print(f"✅ 数据形状: {df.shape}")
        print(f"\n所有列名:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        print(f"\n最近3期数据:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 2. 财务摘要（按年度）
    print("\n\n2. stock_financial_abstract_ths - 按年度")
    try:
        df = ak.stock_financial_abstract_ths(symbol=test_code, indicator="按年度")
        print(f"✅ 数据形状: {df.shape}")
        print(f"\n最近3年数据:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 3. 利润表（按报告期）
    print("\n\n3. stock_financial_benefit_ths - 按报告期")
    try:
        df = ak.stock_financial_benefit_ths(symbol=test_code, indicator="按报告期")
        print(f"✅ 数据形状: {df.shape}")
        print(f"\n所有列名:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        print(f"\n最近3期数据（部分列）:")
        key_cols = ['报告期', '*净利润', '*营业总收入', '*营业总成本', '基本每股收益']
        if all(col in df.columns for col in key_cols):
            print(df[key_cols].head(3).to_string())
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 4. 测试其他股票
    print("\n\n4. 测试其他股票")
    test_codes = ["000001", "600000", "002594"]
    for code in test_codes:
        print(f"\n  测试 {code}:")
        try:
            df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")
            print(f"    ✅ 成功，{df.shape[0]} 期数据")
        except Exception as e:
            print(f"    ❌ 失败: {e}")


if __name__ == '__main__':
    test_ths_apis()
