# -*- coding: utf-8 -*-
"""数据库内容检查工具"""
import sqlite3
import pandas as pd
from src.data.database import StockDatabase

def inspect_database():
    """详细检查数据库内容"""
    
    print("="*70)
    print("📊 A股数据库内容详细检查")
    print("="*70)
    
    db = StockDatabase("data/a_share.db")
    
    # 1. 查看所有表
    print("\n【1. 数据库表结构】")
    print("-"*70)
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"共有 {len(tables)} 张表:\n")
    
    for i, (table_name,) in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        count = cursor.fetchone()[0]
        
        if table_name.startswith('daily_'):
            table_type = "📈 日线数据表"
        elif table_name == 'stock_basic':
            table_type = "📋 股票列表"
        elif table_name == 'market_snapshot':
            table_type = "📸 市场快照"
        elif table_name == 'sync_status':
            table_type = "🔄 同步状态"
        else:
            table_type = "❓ 其他"
        
        print(f"{i:3d}. {table_type:12s} | {table_name:30s} | {count:6d} 条记录")
    
    # 2. 股票基本信息表
    print("\n" + "="*70)
    print("【2. 股票基本信息表 (stock_basic)】")
    print("-"*70)
    
    stock_list = db.get_stock_list()
    print(f"\n总共 {len(stock_list)} 只股票\n")
    
    # 按市场分类统计
    print("按市场分类:")
    market_counts = stock_list['market'].value_counts()
    for market, count in market_counts.items():
        market_name = {
            'sh': '上海证券交易所',
            'sz': '深圳证券交易所',
            'bj': '北京证券交易所',
            'unknown': '未知市场'
        }.get(market, market)
        print(f"  {market_name:20s}: {count:5d} 只")
    
    print("\n前10只股票:")
    print(stock_list[['code', 'name', 'market', 'full_code']].head(10).to_string(index=False))
    
    # 3. 查看一只股票的详细数据
    print("\n" + "="*70)
    print("【3. 单只股票数据示例】")
    print("-"*70)
    
    # 找一只有数据的股票
    sample_stock = None
    for _, row in stock_list.head(20).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        if db.table_exists(code):
            sample_stock = row
            break
    
    if sample_stock is not None:
        code = sample_stock.get('full_code', f"{sample_stock['market']}.{sample_stock['code']}")
        name = sample_stock['name']
        
        print(f"\n以 {name} ({code}) 为例:\n")
        
        df = db.get_daily_data(code)
        
        if not df.empty:
            print(f"数据条数: {len(df)} 条")
            print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
            print(f"\n数据字段: {', '.join(df.columns.tolist())}")
            
            print("\n最近5天数据:")
            print(df.tail().to_string(index=False))
            
            print("\n数据统计:")
            print(f"  最高价: {df['high'].max():.2f}")
            print(f"  最低价: {df['low'].min():.2f}")
            print(f"  平均收盘价: {df['close'].mean():.2f}")
            print(f"  平均成交量: {df['volume'].mean():.0f}")
            
            # 计算涨跌幅
            if len(df) > 1:
                total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
                print(f"  期间涨跌幅: {total_return:.2f}%")
    
    # 4. 同步状态
    print("\n" + "="*70)
    print("【4. 数据同步状态】")
    print("-"*70)
    
    sync_status = db.get_sync_status()
    if not sync_status.empty:
        print(f"\n已同步 {len(sync_status)} 只股票")
        
        success = sync_status[sync_status['status'] == 'success']
        print(f"成功: {len(success)} 只")
        
        if len(sync_status) > 0:
            print("\n最近同步的5只股票:")
            recent = sync_status.head(5)
            print(recent[['code', 'total_records', 'last_sync_date', 'status']].to_string(index=False))
    
    # 5. 数据存储分析
    print("\n" + "="*70)
    print("【5. 数据存储分析】")
    print("-"*70)
    
    stats = db.get_statistics()
    
    print(f"\n存储统计:")
    print(f"  总股票数: {stats['total_stocks']}")
    print(f"  已下载: {stats['downloaded_stocks']}")
    print(f"  完成度: {stats['completion_rate']}")
    print(f"  总记录数: {stats['total_records']:,}")
    print(f"  平均每只: {stats['avg_records_per_stock']} 条")
    
    # 计算数据库大小
    import os
    db_size = os.path.getsize("data/a_share.db") / (1024 * 1024)
    print(f"  数据库大小: {db_size:.2f} MB")
    
    if stats['downloaded_stocks'] > 0:
        avg_size_per_stock = db_size / stats['downloaded_stocks']
        print(f"  平均每只股票: {avg_size_per_stock:.2f} MB")
        
        # 预估全市场大小
        estimated_full_size = avg_size_per_stock * stats['total_stocks']
        print(f"  预估全市场: {estimated_full_size:.2f} MB ({estimated_full_size/1024:.2f} GB)")
    
    # 6. 数据质量检查
    print("\n" + "="*70)
    print("【6. 数据质量检查】")
    print("-"*70)
    
    print("\n检查前10只已下载股票的数据质量:")
    
    quality_issues = []
    checked = 0
    
    for _, row in stock_list.head(50).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        
        if not db.table_exists(code):
            continue
        
        df = db.get_daily_data(code)
        
        if df.empty:
            quality_issues.append(f"{code}: 表存在但无数据")
            continue
        
        # 检查空值
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            quality_issues.append(f"{code}: 存在空值 {null_counts[null_counts > 0].to_dict()}")
        
        # 检查日期连续性（简单检查）
        if len(df) < 200:  # 少于200条可能数据不完整
            quality_issues.append(f"{code}: 数据量偏少 ({len(df)} 条)")
        
        checked += 1
        if checked >= 10:
            break
    
    if quality_issues:
        print(f"\n发现 {len(quality_issues)} 个问题:")
        for issue in quality_issues[:5]:
            print(f"  ⚠️  {issue}")
    else:
        print("\n✅ 数据质量良好，未发现明显问题")
    
    # 7. 存储结构说明
    print("\n" + "="*70)
    print("【7. 存储结构说明】")
    print("-"*70)
    
    print("""
数据库采用 SQLite 格式，包含以下表：

1. stock_basic (股票基本信息)
   - code: 股票代码 (如: 600000)
   - name: 股票名称
   - market: 市场 (sh/sz/bj)
   - full_code: 完整代码 (如: sh.600000)
   
2. daily_XXX (日线数据，每只股票一张表)
   - date: 日期
   - open/high/low/close: 开高低收
   - volume: 成交量
   - amount: 成交额
   - pct_chg: 涨跌幅
   - turnover: 换手率
   
3. sync_status (同步状态)
   - 记录每只股票的下载状态和时间
   
4. market_snapshot (市场快照，可选)
   - 每日全市场实时数据快照
    """)
    
    print("="*70)
    print("✨ 检查完成！")
    print("="*70)
    
    db.close()


if __name__ == "__main__":
    inspect_database()
