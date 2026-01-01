#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据查询工具 - 快速查看数据库内容"""
import sys
import pandas as pd
from src.data.database import StockDatabase

def show_menu():
    """显示菜单"""
    print("\n" + "="*80)
    print("📊 A股数据查询工具")
    print("="*80)
    print("1. 数据库总览")
    print("2. 查看中盘股列表（50-200亿）")
    print("3. 查看行业分布")
    print("4. 查看特定股票数据")
    print("5. 按行业筛选股票")
    print("6. 按市值筛选股票")
    print("7. 查看最新市场快照")
    print("0. 退出")
    print("="*80)

def show_overview(db):
    """显示数据库总览"""
    print("\n" + "="*80)
    print("📊 数据库总览")
    print("="*80)
    
    # 基本统计
    stats = db.get_statistics()
    print(f"\n【基本统计】")
    print(f"总股票数: {stats['total_stocks']}")
    print(f"已下载: {stats['downloaded_stocks']} ({stats['completion_rate']})")
    print(f"总记录数: {stats['total_records']:,}")
    print(f"平均每只: {stats['avg_records_per_stock']} 条")
    
    # 市值分类
    try:
        cap_stats = pd.read_sql("""
            SELECT cap_category, COUNT(*) as count
            FROM market_cap_data
            GROUP BY cap_category
            ORDER BY count DESC
        """, db.conn)
        
        print(f"\n【市值分类】")
        for _, row in cap_stats.iterrows():
            print(f"{row['cap_category']:10s}: {row['count']:5d} 只")
    except:
        print("\n⚠️ 市值数据未加载")
    
    # 行业统计
    try:
        industry_count = pd.read_sql("""
            SELECT COUNT(DISTINCT industry) as count
            FROM industry_data
        """, db.conn)
        
        print(f"\n【行业数据】")
        print(f"行业数量: {industry_count['count'].iloc[0]} 个")
    except:
        print("\n⚠️ 行业数据未加载")

def show_mid_cap_stocks(db):
    """显示中盘股列表"""
    print("\n" + "="*80)
    print("📊 中盘股列表（50-200亿）")
    print("="*80)
    
    try:
        df = pd.read_sql("""
            SELECT 
                m.code,
                m.name,
                m.total_cap/100000000 as cap_yi,
                m.pe_ttm,
                m.pb,
                i.industry
            FROM market_cap_data m
            LEFT JOIN industry_data i ON m.code = i.code
            WHERE m.total_cap >= 5000000000 
              AND m.total_cap <= 20000000000
            ORDER BY m.total_cap DESC
            LIMIT 50
        """, db.conn)
        
        print(f"\n找到 {len(df)} 只中盘股（显示前50只）\n")
        
        # 格式化显示
        df['cap_yi'] = df['cap_yi'].apply(lambda x: f"{x:.2f}")
        df['pe_ttm'] = df['pe_ttm'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
        df['pb'] = df['pb'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
        df['industry'] = df['industry'].fillna("-")
        
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def show_industries(db):
    """显示行业分布"""
    print("\n" + "="*80)
    print("📊 行业分布")
    print("="*80)
    
    try:
        df = pd.read_sql("""
            SELECT industry, COUNT(*) as count
            FROM industry_data
            GROUP BY industry
            ORDER BY count DESC
            LIMIT 30
        """, db.conn)
        
        print(f"\n共 {len(df)} 个行业（显示前30个）\n")
        
        for idx, row in df.iterrows():
            print(f"{idx+1:2d}. {row['industry']:30s}: {row['count']:4d} 只")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def show_stock_data(db, code):
    """显示特定股票数据"""
    print("\n" + "="*80)
    print(f"📊 股票数据: {code}")
    print("="*80)
    
    # 基本信息
    try:
        basic = pd.read_sql(f"""
            SELECT * FROM stock_basic WHERE code = '{code.split('.')[1]}'
        """, db.conn)
        
        if not basic.empty:
            print(f"\n【基本信息】")
            print(f"代码: {basic['code'].iloc[0]}")
            print(f"名称: {basic['name'].iloc[0]}")
            print(f"市场: {basic['market'].iloc[0]}")
            print(f"上市日期: {basic['list_date'].iloc[0]}")
    except:
        pass
    
    # 市值信息
    try:
        cap = pd.read_sql(f"""
            SELECT * FROM market_cap_data WHERE full_code = '{code}'
        """, db.conn)
        
        if not cap.empty:
            print(f"\n【市值信息】")
            print(f"最新价: {cap['price'].iloc[0]:.2f}")
            print(f"总市值: {cap['total_cap'].iloc[0]/1e8:.2f} 亿")
            print(f"流通市值: {cap['float_cap'].iloc[0]/1e8:.2f} 亿")
            print(f"市盈率: {cap['pe_ttm'].iloc[0]:.2f}" if pd.notna(cap['pe_ttm'].iloc[0]) else "市盈率: -")
            print(f"市净率: {cap['pb'].iloc[0]:.2f}" if pd.notna(cap['pb'].iloc[0]) else "市净率: -")
            print(f"市值分类: {cap['cap_category'].iloc[0]}")
    except:
        pass
    
    # 行业信息
    try:
        industry = pd.read_sql(f"""
            SELECT * FROM industry_data WHERE full_code = '{code}'
        """, db.conn)
        
        if not industry.empty:
            print(f"\n【行业信息】")
            print(f"行业: {industry['industry'].iloc[0]}")
    except:
        pass
    
    # 历史数据
    df = db.get_daily_data(code)
    
    if not df.empty:
        print(f"\n【历史数据】")
        print(f"数据条数: {len(df)} 条")
        print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
        
        print(f"\n最近5天数据:")
        print(df.tail().to_string(index=False))
        
        # 统计
        print(f"\n【价格统计】")
        print(f"最高价: {df['high'].max():.2f}")
        print(f"最低价: {df['low'].min():.2f}")
        print(f"最新价: {df['close'].iloc[-1]:.2f}")
        print(f"平均价: {df['close'].mean():.2f}")
        
        if len(df) > 1:
            total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
            print(f"期间涨跌: {total_return:+.2f}%")
    else:
        print(f"\n⚠️ 未找到历史数据")

def filter_by_industry(db, industry):
    """按行业筛选股票"""
    print("\n" + "="*80)
    print(f"📊 行业筛选: {industry}")
    print("="*80)
    
    try:
        df = pd.read_sql(f"""
            SELECT 
                i.code,
                i.name,
                m.total_cap/100000000 as cap_yi,
                m.pe_ttm,
                m.pb
            FROM industry_data i
            LEFT JOIN market_cap_data m ON i.code = m.code
            WHERE i.industry = '{industry}'
            ORDER BY m.total_cap DESC
            LIMIT 50
        """, db.conn)
        
        print(f"\n找到 {len(df)} 只股票（显示前50只）\n")
        
        if not df.empty:
            df['cap_yi'] = df['cap_yi'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
            df['pe_ttm'] = df['pe_ttm'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
            df['pb'] = df['pb'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
            
            print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def filter_by_cap(db, min_cap, max_cap):
    """按市值筛选股票"""
    print("\n" + "="*80)
    print(f"📊 市值筛选: {min_cap}-{max_cap}亿")
    print("="*80)
    
    try:
        df = pd.read_sql(f"""
            SELECT 
                m.code,
                m.name,
                m.total_cap/100000000 as cap_yi,
                m.pe_ttm,
                m.pb,
                i.industry
            FROM market_cap_data m
            LEFT JOIN industry_data i ON m.code = i.code
            WHERE m.total_cap >= {min_cap * 1e8}
              AND m.total_cap <= {max_cap * 1e8}
            ORDER BY m.total_cap DESC
            LIMIT 50
        """, db.conn)
        
        print(f"\n找到 {len(df)} 只股票（显示前50只）\n")
        
        if not df.empty:
            df['cap_yi'] = df['cap_yi'].apply(lambda x: f"{x:.2f}")
            df['pe_ttm'] = df['pe_ttm'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
            df['pb'] = df['pb'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
            df['industry'] = df['industry'].fillna("-")
            
            print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def show_market_snapshot(db):
    """显示最新市场快照"""
    print("\n" + "="*80)
    print("📊 市场快照")
    print("="*80)
    
    try:
        # 涨幅榜
        print("\n【涨幅榜 Top 20】")
        df = pd.read_sql("""
            SELECT code, name, price, total_cap/100000000 as cap_yi
            FROM market_cap_data
            WHERE total_cap >= 5000000000 
              AND total_cap <= 20000000000
            ORDER BY price DESC
            LIMIT 20
        """, db.conn)
        
        if not df.empty:
            df['cap_yi'] = df['cap_yi'].apply(lambda x: f"{x:.2f}")
            print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def main():
    """主函数"""
    db = StockDatabase("data/a_share.db")
    
    while True:
        show_menu()
        choice = input("\n请选择功能 (0-7): ").strip()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        elif choice == '1':
            show_overview(db)
        elif choice == '2':
            show_mid_cap_stocks(db)
        elif choice == '3':
            show_industries(db)
        elif choice == '4':
            code = input("请输入股票代码（如 sh.600000）: ").strip()
            show_stock_data(db, code)
        elif choice == '5':
            industry = input("请输入行业名称（如 软件开发）: ").strip()
            filter_by_industry(db, industry)
        elif choice == '6':
            min_cap = float(input("最小市值（亿）: ").strip())
            max_cap = float(input("最大市值（亿）: ").strip())
            filter_by_cap(db, min_cap, max_cap)
        elif choice == '7':
            show_market_snapshot(db)
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按回车继续...")
    
    db.close()

if __name__ == "__main__":
    main()
