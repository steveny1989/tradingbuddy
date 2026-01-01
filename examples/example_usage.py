# -*- coding: utf-8 -*-
"""使用示例"""
from src.data.database import StockDatabase
from src.data.fetcher import DataFetcher
import pandas as pd

def example_basic_usage():
    """基础使用示例"""
    print("="*60)
    print("示例1: 基础数据查询")
    print("="*60)
    
    # 初始化数据库
    db = StockDatabase("data/a_share.db")
    
    # 1. 查看股票列表
    stock_list = db.get_stock_list()
    print(f"\n📊 股票总数: {len(stock_list)}")
    print("\n前5只股票:")
    print(stock_list.head())
    
    # 2. 查看数据库统计
    stats = db.get_statistics()
    print(f"\n📈 数据库统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 3. 查询单只股票数据
    if not stock_list.empty:
        code = stock_list.iloc[0]['full_code']
        df = db.get_daily_data(code, start_date="20240101")
        
        if not df.empty:
            print(f"\n📉 {code} 最近5天数据:")
            print(df.tail())
    
    db.close()


def example_data_analysis():
    """数据分析示例"""
    print("\n" + "="*60)
    print("示例2: 数据分析")
    print("="*60)
    
    db = StockDatabase("data/a_share.db")
    
    # 获取一只股票的数据
    df = db.get_daily_data("sh.600000", start_date="20240101")
    
    if not df.empty:
        # 计算技术指标
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        # 计算涨跌幅
        df['return'] = df['close'].pct_change()
        
        print("\n📊 浦发银行(600000) 技术指标:")
        print(df[['date', 'close', 'ma5', 'ma20', 'return']].tail(10))
        
        # 统计信息
        print(f"\n📈 统计信息:")
        print(f"  最高价: {df['high'].max():.2f}")
        print(f"  最低价: {df['low'].min():.2f}")
        print(f"  平均成交量: {df['volume'].mean():.0f}")
        print(f"  累计涨跌幅: {(df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100:.2f}%")
    
    db.close()


def example_stock_screening():
    """选股示例 - 找出最近3天连续下跌的股票"""
    print("\n" + "="*60)
    print("示例3: 简单选股 - 三连跌股票")
    print("="*60)
    
    db = StockDatabase("data/a_share.db")
    stock_list = db.get_stock_list()
    
    results = []
    
    # 只检查前50只股票作为示例
    for idx, row in stock_list.head(50).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        
        # 获取最近5天数据
        df = db.get_daily_data(code)
        
        if len(df) >= 4:
            # 取最近4天
            recent = df.tail(4)
            prices = recent['close'].values
            
            # 检查是否三连跌
            if (prices[-1] < prices[-2] < prices[-3] < prices[-4]):
                drop_rate = (prices[-1] - prices[-4]) / prices[-4]
                
                results.append({
                    '代码': code,
                    '名称': row['name'],
                    '最新价': prices[-1],
                    '三日跌幅': f"{drop_rate*100:.2f}%"
                })
    
    if results:
        result_df = pd.DataFrame(results)
        print(f"\n找到 {len(result_df)} 只三连跌股票:")
        print(result_df.to_string(index=False))
    else:
        print("\n未找到符合条件的股票")
    
    db.close()


def example_market_overview():
    """市场概览示例"""
    print("\n" + "="*60)
    print("示例4: 市场概览")
    print("="*60)
    
    db = StockDatabase("data/a_share.db")
    
    # 获取最新的市场快照
    try:
        snapshot = pd.read_sql(
            "SELECT * FROM market_snapshot WHERE date = (SELECT MAX(date) FROM market_snapshot)",
            db.conn
        )
        
        if not snapshot.empty:
            print(f"\n📊 市场快照 ({snapshot['date'].iloc[0]}):")
            print(f"  股票数量: {len(snapshot)}")
            print(f"  上涨家数: {len(snapshot[snapshot['pct_chg'] > 0])}")
            print(f"  下跌家数: {len(snapshot[snapshot['pct_chg'] < 0])}")
            print(f"  平均涨跌幅: {snapshot['pct_chg'].mean():.2f}%")
            print(f"  总成交额: {snapshot['amount'].sum() / 1e8:.2f} 亿")
            
            # 涨幅榜
            print("\n📈 涨幅前5:")
            top5 = snapshot.nlargest(5, 'pct_chg')[['code', 'pct_chg', 'price']]
            print(top5.to_string(index=False))
            
            # 跌幅榜
            print("\n📉 跌幅前5:")
            bottom5 = snapshot.nsmallest(5, 'pct_chg')[['code', 'pct_chg', 'price']]
            print(bottom5.to_string(index=False))
        else:
            print("\n暂无市场快照数据")
    except:
        print("\n市场快照表不存在，请先运行 update 命令")
    
    db.close()


if __name__ == "__main__":
    # 运行所有示例
    example_basic_usage()
    example_data_analysis()
    example_stock_screening()
    example_market_overview()
    
    print("\n" + "="*60)
    print("✨ 示例运行完成！")
    print("="*60)
