#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断akshare API问题
"""
import akshare as ak
import pandas as pd
import json

def test_api():
    """测试akshare API"""
    
    print("="*60)
    print("🔍 诊断 akshare API")
    print("="*60)
    
    # 测试股票代码
    test_codes = ["600000", "000001", "600519"]
    
    for code in test_codes:
        print(f"\n{'='*60}")
        print(f"测试股票: {code}")
        print(f"{'='*60}")
        
        # 测试资产负债表
        print("\n1. 测试资产负债表...")
        try:
            df = ak.stock_financial_report_sina(stock=code, symbol="资产负债表")
            print(f"✅ 成功获取，数据形状: {df.shape}")
            print(f"列名: {df.columns.tolist()}")
            if not df.empty:
                print(f"前3行数据:")
                print(df.head(3))
        except Exception as e:
            print(f"❌ 失败: {type(e).__name__}: {e}")
        
        # 测试利润表
        print("\n2. 测试利润表...")
        try:
            df = ak.stock_financial_report_sina(stock=code, symbol="利润表")
            print(f"✅ 成功获取，数据形状: {df.shape}")
            print(f"列名: {df.columns.tolist()}")
            if not df.empty:
                print(f"前3行数据:")
                print(df.head(3))
        except Exception as e:
            print(f"❌ 失败: {type(e).__name__}: {e}")
        
        # 测试现金流量表
        print("\n3. 测试现金流量表...")
        try:
            df = ak.stock_financial_report_sina(stock=code, symbol="现金流量表")
            print(f"✅ 成功获取，数据形状: {df.shape}")
            print(f"列名: {df.columns.tolist()}")
            if not df.empty:
                print(f"前3行数据:")
                print(df.head(3))
        except Exception as e:
            print(f"❌ 失败: {type(e).__name__}: {e}")
    
    # 测试其他可能的API
    print(f"\n{'='*60}")
    print("测试其他可能的财务数据API")
    print(f"{'='*60}")
    
    # 列出akshare中所有包含"financial"的函数
    print("\n查找akshare中的财务相关函数...")
    financial_funcs = [name for name in dir(ak) if 'financial' in name.lower()]
    print(f"找到 {len(financial_funcs)} 个函数:")
    for func in financial_funcs[:10]:  # 只显示前10个
        print(f"  - {func}")
    
    # 测试其他可能的API
    print("\n测试 stock_financial_abstract 接口...")
    try:
        df = ak.stock_financial_abstract(symbol="600000")
        print(f"✅ 成功获取，数据形状: {df.shape}")
        print(f"列名: {df.columns.tolist()}")
        print(df.head())
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")
    
    print("\n测试 stock_financial_analysis_indicator 接口...")
    try:
        df = ak.stock_financial_analysis_indicator(symbol="600000")
        print(f"✅ 成功获取，数据形状: {df.shape}")
        print(f"列名: {df.columns.tolist()}")
        print(df.head())
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")


if __name__ == '__main__':
    test_api()
