#!/usr/bin/env python3
"""
测试资金流向数据获取功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.data.capital_flow_fetcher import CapitalFlowFetcher
from datetime import datetime, timedelta
import sqlite3
import pandas as pd


def test_database_tables():
    """测试数据表是否创建成功"""
    print("=" * 60)
    print("测试1: 检查数据表")
    print("=" * 60)
    
    conn = sqlite3.connect('data/a_share.db')
    cursor = conn.cursor()
    
    tables = ['northbound_capital', 'capital_flow', 'dragon_tiger_list', 'dragon_tiger_seats']
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        result = cursor.fetchone()
        if result:
            print(f"✅ {table} 表已创建")
            
            # 显示表结构
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"   字段数: {len(columns)}")
            print(f"   字段: {', '.join([col[1] for col in columns[:5]])}...")
        else:
            print(f"❌ {table} 表不存在")
    
    conn.close()
    print()


def test_fetch_northbound():
    """测试获取北向资金数据"""
    print("=" * 60)
    print("测试2: 获取北向资金数据")
    print("=" * 60)
    
    fetcher = CapitalFlowFetcher()
    
    # 测试贵州茅台
    test_stocks = ['600519', '000001', '300750']
    
    for symbol in test_stocks:
        print(f"\n测试股票: {symbol}")
        df = fetcher.fetch_northbound_capital(symbol)
        
        if df is not None and len(df) > 0:
            print(f"✅ 获取成功，共 {len(df)} 条数据")
            print("\n最新数据:")
            print(df.head(3).to_string())
            
            # 保存到数据库
            count = fetcher.save_northbound_capital(df)
            print(f"\n保存了 {count} 条数据到数据库")
        else:
            print(f"⚠️ 该股票无北向资金数据")
    
    print()


def test_fetch_capital_flow():
    """测试获取资金流向数据"""
    print("=" * 60)
    print("测试3: 获取资金流向排名")
    print("=" * 60)
    
    fetcher = CapitalFlowFetcher()
    
    df = fetcher.fetch_capital_flow_rank(indicator="今日")
    
    if df is not None and len(df) > 0:
        print(f"✅ 获取成功，共 {len(df)} 只股票")
        
        # 转换数据类型
        numeric_cols = ['main_net_inflow', 'main_net_inflow_ratio', 'pct_chg']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print("\n主力净流入前10:")
        top10 = df.nlargest(10, 'main_net_inflow')[['code', 'name', 'pct_chg', 'main_net_inflow', 'main_net_inflow_ratio']]
        print(top10.to_string())
        
        # 保存到数据库
        count = fetcher.save_capital_flow(df)
        print(f"\n保存了 {count} 条数据到数据库")
    else:
        print("❌ 获取失败")
    
    print()


def test_fetch_dragon_tiger():
    """测试获取龙虎榜数据"""
    print("=" * 60)
    print("测试4: 获取龙虎榜数据")
    print("=" * 60)
    
    fetcher = CapitalFlowFetcher()
    
    # 测试最近几天
    for i in range(1, 4):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        print(f"\n测试日期: {date}")
        
        df = fetcher.fetch_dragon_tiger_list(date)
        
        if df is not None and len(df) > 0:
            print(f"✅ 获取成功，共 {len(df)} 只股票上榜")
            print("\n上榜股票:")
            print(df[['code', 'name', 'pct_chg', 'reason', 'net_amount']].head(5).to_string())
            
            # 保存到数据库
            count = fetcher.save_dragon_tiger_list(df)
            print(f"\n保存了 {count} 条数据到数据库")
            break  # 找到数据就停止
        else:
            print(f"⚠️ {date} 无龙虎榜数据（可能是周末或节假日）")
    
    print()


def test_query_data():
    """测试查询数据库中的数据"""
    print("=" * 60)
    print("测试5: 查询数据库数据")
    print("=" * 60)
    
    conn = sqlite3.connect('data/a_share.db')
    
    # 查询北向资金
    print("\n北向资金数据:")
    df = pd.read_sql("SELECT * FROM northbound_capital ORDER BY date DESC LIMIT 5", conn)
    if len(df) > 0:
        print(df.to_string())
    else:
        print("暂无数据")
    
    # 查询资金流向
    print("\n\n资金流向数据:")
    df = pd.read_sql("SELECT code, name, pct_chg, main_net_inflow, main_net_inflow_ratio FROM capital_flow ORDER BY main_net_inflow DESC LIMIT 5", conn)
    if len(df) > 0:
        print(df.to_string())
    else:
        print("暂无数据")
    
    # 查询龙虎榜
    print("\n\n龙虎榜数据:")
    df = pd.read_sql("SELECT code, name, date, pct_chg, reason FROM dragon_tiger_list ORDER BY date DESC LIMIT 5", conn)
    if len(df) > 0:
        print(df.to_string())
    else:
        print("暂无数据")
    
    conn.close()
    print()


def test_analysis_example():
    """测试分析示例"""
    print("=" * 60)
    print("测试6: 分析示例 - 贵州茅台")
    print("=" * 60)
    
    conn = sqlite3.connect('data/a_share.db')
    
    # 查询贵州茅台的北向资金趋势
    print("\n北向资金持股趋势:")
    query = """
    SELECT date, hold_ratio, change_ratio_5d
    FROM northbound_capital
    WHERE code = '600519'
    ORDER BY date DESC
    LIMIT 10
    """
    df = pd.read_sql(query, conn)
    if len(df) > 0:
        print(df.to_string())
        
        # 分析连续买入天数
        consecutive_days = 0
        for _, row in df.iterrows():
            if row['change_ratio_5d'] > 0:
                consecutive_days += 1
            else:
                break
        
        if consecutive_days >= 3:
            print(f"\n🟢 外资连续 {consecutive_days} 天加仓，机构正在'抱团'")
        elif consecutive_days <= -3:
            print(f"\n🔴 外资连续 {abs(consecutive_days)} 天减仓，主力资金撤退")
        else:
            print(f"\n🟡 外资持仓稳定，暂无明显动作")
    else:
        print("暂无数据")
    
    # 查询今日资金流向
    print("\n\n今日资金流向:")
    query = """
    SELECT name, pct_chg, main_net_inflow, main_net_inflow_ratio
    FROM capital_flow
    WHERE code = '600519'
    ORDER BY date DESC
    LIMIT 1
    """
    df = pd.read_sql(query, conn)
    if len(df) > 0:
        print(df.to_string())
        
        row = df.iloc[0]
        if row['main_net_inflow'] > 0 and row['main_net_inflow_ratio'] > 10:
            print(f"\n🟢 主力资金大幅流入，有大资金在建仓")
            print(f"   主力净流入: {row['main_net_inflow']/1e8:.2f}亿 (占成交额{row['main_net_inflow_ratio']:.1f}%)")
        elif row['main_net_inflow'] < 0 and row['main_net_inflow_ratio'] < -10:
            print(f"\n🔴 主力资金大幅流出，机构在出货")
            print(f"   主力净流出: {row['main_net_inflow']/1e8:.2f}亿 (占成交额{row['main_net_inflow_ratio']:.1f}%)")
        else:
            print(f"\n🟡 资金流向正常")
    else:
        print("暂无数据")
    
    conn.close()
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("资金流向数据获取功能测试")
    print("=" * 60 + "\n")
    
    try:
        # 测试1: 检查数据表
        test_database_tables()
        
        # 测试2: 获取北向资金数据
        test_fetch_northbound()
        
        # 测试3: 获取资金流向数据
        test_fetch_capital_flow()
        
        # 测试4: 获取龙虎榜数据
        test_fetch_dragon_tiger()
        
        # 测试5: 查询数据库数据
        test_query_data()
        
        # 测试6: 分析示例
        test_analysis_example()
        
        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
