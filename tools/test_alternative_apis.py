#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare的其他财务数据API
"""
import akshare as ak
import pandas as pd

def test_all_financial_apis():
    """测试所有可能的财务数据API"""
    
    test_code = "600519"  # 贵州茅台，肯定有数据
    
    print("="*60)
    print(f"测试股票: {test_code} (贵州茅台)")
    print("="*60)
    
    # 1. 东方财富财务指标
    print("\n1. stock_financial_analysis_indicator_em (东方财富)")
    try:
        df = ak.stock_financial_analysis_indicator_em(symbol=test_code)
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 2. 同花顺财务摘要
    print("\n2. stock_financial_abstract_ths (同花顺)")
    try:
        df = ak.stock_financial_abstract_ths(symbol=test_code, indicator="按报告期")
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 3. 同花顺财务摘要（新）
    print("\n3. stock_financial_abstract_new_ths (同花顺新)")
    try:
        df = ak.stock_financial_abstract_new_ths(symbol=test_code, indicator="按报告期")
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 4. 同花顺财务受益
    print("\n4. stock_financial_benefit_ths (同花顺)")
    try:
        df = ak.stock_financial_benefit_ths(symbol=test_code, indicator="按报告期")
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 5. 同花顺财务受益（新）
    print("\n5. stock_financial_benefit_new_ths (同花顺新)")
    try:
        df = ak.stock_financial_benefit_new_ths(symbol=test_code, indicator="按报告期")
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 6. 测试东方财富的资产负债表
    print("\n6. stock_balance_sheet_by_report_em (东方财富资产负债表)")
    try:
        df = ak.stock_balance_sheet_by_report_em(symbol=test_code)
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()[:10]}")  # 只显示前10列
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 7. 测试东方财富的利润表
    print("\n7. stock_profit_sheet_by_report_em (东方财富利润表)")
    try:
        df = ak.stock_profit_sheet_by_report_em(symbol=test_code)
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()[:10]}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 8. 测试东方财富的现金流量表
    print("\n8. stock_cash_flow_sheet_by_report_em (东方财富现金流量表)")
    try:
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=test_code)
        print(f"✅ 成功！数据形状: {df.shape}")
        if not df.empty:
            print(f"列名: {df.columns.tolist()[:10]}")
            print(df.head(3))
    except Exception as e:
        print(f"❌ 失败: {e}")


if __name__ == '__main__':
    test_all_financial_apis()
