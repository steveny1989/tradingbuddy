# -*- coding: utf-8 -*-
"""展示单只股票的完整数据"""
import sys
from src.data.database import StockDatabase
import pandas as pd

def show_stock_data(code=None):
    """展示股票数据"""
    
    db = StockDatabase("data/a_share.db")
    
    # 如果没有指定代码，找一只有完整数据的股票
    if code is None:
        print("正在查找有完整数据的股票...")
        stock_list = db.get_stock_list()
        
        for _, row in stock_list.iterrows():
            test_code = row.get('full_code', f"{row['market']}.{row['code']}")
            if db.table_exists(test_code):
                df = db.get_daily_data(test_code)
                if len(df) > 400:  # 找一只有完整数据的
                    code = test_code
                    stock_name = row['name']
                    break
    else:
        # 查找股票名称
        stock_list = db.get_stock_list()
        stock_info = stock_list[stock_list['code'] == code.split('.')[-1]]
        if not stock_info.empty:
            stock_name = stock_info.iloc[0]['name']
            if '.' not in code:
                market = stock_info.iloc[0]['market']
                code = f"{market}.{code}"
        else:
            stock_name = "未知"
    
    if code is None:
        print("❌ 未找到有完整数据的股票")
        db.close()
        return
    
    print("="*80)
    print(f"📊 股票数据详细展示: {stock_name} ({code})")
    print("="*80)
    
    # 获取数据
    df = db.get_daily_data(code)
    
    if df.empty:
        print("❌ 该股票暂无数据")
        db.close()
        return
    
    # 1. 基本信息
    print("\n【1. 基本信息】")
    print("-"*80)
    print(f"股票代码: {code}")
    print(f"股票名称: {stock_name}")
    print(f"数据条数: {len(df)} 条")
    print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
    print(f"数据字段: {', '.join(df.columns.tolist())}")
    
    # 2. 数据样本
    print("\n【2. 数据样本】")
    print("-"*80)
    print("\n最早5天数据:")
    print(df.head().to_string(index=False))
    
    print("\n最近5天数据:")
    print(df.tail().to_string(index=False))
    
    # 3. 统计分析
    print("\n【3. 统计分析】")
    print("-"*80)
    
    print(f"\n价格统计:")
    print(f"  历史最高价: {df['high'].max():.2f} 元 ({df[df['high'] == df['high'].max()]['date'].iloc[0]})")
    print(f"  历史最低价: {df['low'].min():.2f} 元 ({df[df['low'] == df['low'].min()]['date'].iloc[0]})")
    print(f"  最新收盘价: {df['close'].iloc[-1]:.2f} 元")
    print(f"  平均收盘价: {df['close'].mean():.2f} 元")
    print(f"  价格标准差: {df['close'].std():.2f} 元")
    
    print(f"\n成交量统计:")
    print(f"  最大成交量: {df['volume'].max():,.0f} 手")
    print(f"  最小成交量: {df['volume'].min():,.0f} 手")
    print(f"  平均成交量: {df['volume'].mean():,.0f} 手")
    
    print(f"\n涨跌幅统计:")
    if 'pct_chg' in df.columns:
        print(f"  最大单日涨幅: {df['pct_chg'].max():.2f}%")
        print(f"  最大单日跌幅: {df['pct_chg'].min():.2f}%")
        print(f"  平均日涨跌幅: {df['pct_chg'].mean():.2f}%")
    
    # 计算期间涨跌幅
    if len(df) > 1:
        period_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        print(f"\n期间总涨跌幅: {period_return:.2f}%")
        
        # 年化收益率
        days = (pd.to_datetime(df['date'].iloc[-1]) - pd.to_datetime(df['date'].iloc[0])).days
        if days > 0:
            annual_return = (pow(df['close'].iloc[-1] / df['close'].iloc[0], 365/days) - 1) * 100
            print(f"年化收益率: {annual_return:.2f}%")
    
    # 4. 技术指标
    print("\n【4. 技术指标计算示例】")
    print("-"*80)
    
    # 计算均线
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma60'] = df['close'].rolling(60).mean()
    
    print("\n最近10天的价格和均线:")
    recent = df[['date', 'close', 'ma5', 'ma10', 'ma20', 'ma60']].tail(10)
    print(recent.to_string(index=False))
    
    # 当前均线状态
    latest = df.iloc[-1]
    print(f"\n当前均线状态:")
    print(f"  收盘价: {latest['close']:.2f}")
    print(f"  MA5:   {latest['ma5']:.2f} {'✅ 上方' if latest['close'] > latest['ma5'] else '❌ 下方'}")
    print(f"  MA10:  {latest['ma10']:.2f} {'✅ 上方' if latest['close'] > latest['ma10'] else '❌ 下方'}")
    print(f"  MA20:  {latest['ma20']:.2f} {'✅ 上方' if latest['close'] > latest['ma20'] else '❌ 下方'}")
    print(f"  MA60:  {latest['ma60']:.2f} {'✅ 上方' if latest['close'] > latest['ma60'] else '❌ 下方'}")
    
    # 5. 数据存储格式
    print("\n【5. 数据存储格式】")
    print("-"*80)
    
    print(f"\n表名: daily_{code.replace('.', '_')}")
    print(f"存储格式: SQLite")
    print(f"数据类型:")
    for col in df.columns:
        dtype = df[col].dtype
        print(f"  {col:12s}: {dtype}")
    
    # 6. 使用示例
    print("\n【6. Python 使用示例】")
    print("-"*80)
    
    print(f"""
# 查询这只股票的数据
from database import StockDatabase

db = StockDatabase("data/a_share.db")
df = db.get_daily_data("{code}")

# 查询指定日期范围
df = db.get_daily_data("{code}", 
                       start_date="2024-01-01",
                       end_date="2024-12-31")

# 计算技术指标
df['ma20'] = df['close'].rolling(20).mean()

# 查看最近数据
print(df.tail())
    """)
    
    print("="*80)
    print("✨ 展示完成！")
    print("="*80)
    
    db.close()


if __name__ == "__main__":
    # 可以通过命令行参数指定股票代码
    code = sys.argv[1] if len(sys.argv) > 1 else None
    show_stock_data(code)
