#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看下载的股票数据"""
import sys
from src.data.database import StockDatabase
import pandas as pd

def view_downloaded_data():
    """查看下载的数据详情"""
    
    print("="*80)
    print("📊 已下载股票数据详情")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    
    # 1. 总体统计
    print("\n【1. 总体统计】")
    print("-"*80)
    stats = db.get_statistics()
    print(f"总股票数: {stats['total_stocks']}")
    print(f"已下载: {stats['downloaded_stocks']}")
    print(f"完成度: {stats['completion_rate']}")
    print(f"总记录数: {stats['total_records']:,}")
    print(f"平均每只: {stats['avg_records_per_stock']} 条")
    
    # 2. 按市场分类
    print("\n【2. 按市场分类】")
    print("-"*80)
    stock_list = db.get_stock_list()
    market_counts = stock_list['market'].value_counts()
    for market, count in market_counts.items():
        market_name = {
            'sh': '上海证券交易所',
            'sz': '深圳证券交易所',
            'bj': '北京证券交易所',
            'unknown': '未知市场'
        }.get(market, market)
        
        # 统计已下载的
        downloaded = 0
        for _, row in stock_list[stock_list['market'] == market].iterrows():
            code = row.get('full_code', f"{row['market']}.{row['code']}")
            if db.table_exists(code):
                downloaded += 1
        
        print(f"{market_name:20s}: {downloaded:4d} / {count:4d} ({downloaded/count*100:.1f}%)")
    
    # 3. 随机查看10只股票的数据
    print("\n【3. 数据样本（随机10只股票）】")
    print("-"*80)
    
    import random
    sample_stocks = []
    
    for _, row in stock_list.sample(min(100, len(stock_list))).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        if db.table_exists(code):
            df = db.get_daily_data(code)
            if not df.empty:
                sample_stocks.append({
                    'code': code,
                    'name': row['name'],
                    'records': len(df),
                    'start_date': df['date'].min(),
                    'end_date': df['date'].max(),
                    'latest_price': df['close'].iloc[-1]
                })
                if len(sample_stocks) >= 10:
                    break
    
    if sample_stocks:
        sample_df = pd.DataFrame(sample_stocks)
        print(sample_df.to_string(index=False))
    
    # 4. 查看一只完整的股票数据
    print("\n【4. 完整股票数据示例】")
    print("-"*80)
    
    # 找一只有完整数据的股票
    for _, row in stock_list.head(50).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        if db.table_exists(code):
            df = db.get_daily_data(code)
            if len(df) > 400:  # 找一只数据完整的
                print(f"\n股票: {row['name']} ({code})")
                print(f"数据条数: {len(df)} 条")
                print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
                print(f"\n数据字段: {', '.join(df.columns.tolist())}")
                
                print("\n最早5天数据:")
                print(df.head().to_string(index=False))
                
                print("\n最近5天数据:")
                print(df.tail().to_string(index=False))
                
                # 统计信息
                print(f"\n价格统计:")
                print(f"  最高价: {df['high'].max():.2f}")
                print(f"  最低价: {df['low'].min():.2f}")
                print(f"  最新价: {df['close'].iloc[-1]:.2f}")
                print(f"  平均价: {df['close'].mean():.2f}")
                
                print(f"\n成交量统计:")
                print(f"  最大成交量: {df['volume'].max():,.0f}")
                print(f"  平均成交量: {df['volume'].mean():,.0f}")
                
                # 计算收益率
                if len(df) > 1:
                    total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
                    print(f"\n期间涨跌幅: {total_return:.2f}%")
                
                break
    
    # 5. 数据质量检查
    print("\n【5. 数据质量检查】")
    print("-"*80)
    
    # 检查数据完整性
    issues = []
    checked = 0
    
    for _, row in stock_list.sample(min(100, len(stock_list))).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        if not db.table_exists(code):
            continue
        
        df = db.get_daily_data(code)
        if df.empty:
            issues.append(f"{code}: 表存在但无数据")
            continue
        
        # 检查数据量
        if len(df) < 100:
            issues.append(f"{code} ({row['name']}): 数据量偏少 ({len(df)} 条)")
        
        checked += 1
        if checked >= 50:
            break
    
    print(f"检查了 {checked} 只股票")
    if issues:
        print(f"发现 {len(issues)} 个问题:")
        for issue in issues[:10]:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ 数据质量良好")
    
    # 6. 数据库大小
    print("\n【6. 存储信息】")
    print("-"*80)
    import os
    db_size = os.path.getsize("data/a_share.db") / (1024 * 1024)
    print(f"数据库大小: {db_size:.2f} MB")
    print(f"平均每只股票: {db_size/stats['downloaded_stocks']:.3f} MB")
    
    print("\n" + "="*80)
    print("✨ 查看完成！")
    print("="*80)
    
    db.close()


if __name__ == "__main__":
    view_downloaded_data()
