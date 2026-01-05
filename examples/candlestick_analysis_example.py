#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K线形态分析示例 - 分析师口吻版

展示如何用"讲故事"的方式分析股票K线
"""
from src.data.database import StockDatabase
from src.business.post_market.candlestick_patterns import analyze_candlestick_pattern


def analyze_stock_like_analyst(code: str, name: str):
    """像分析师一样分析股票"""
    print(f"\n{'='*80}")
    print(f"📊 {name} ({code}) - K线形态分析")
    print(f"{'='*80}\n")
    
    # 获取数据
    db = StockDatabase()
    df = db.get_daily_data(code)
    
    if df.empty:
        print(f"❌ 暂时无法获取数据\n")
        return
    
    # 取最近30天
    df = df.sort_values('date').tail(30).copy()
    
    # 获取最新数据
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else None
    
    # 基本信息
    print(f"📅 分析日期: {latest['date']}")
    print(f"💰 最新价格: {latest['close']:.2f}元")
    print(f"📈 今日涨跌: {latest.get('pct_chg', 0):+.2f}%")
    print()
    
    # K线形态分析
    result = analyze_candlestick_pattern(df)
    
    # 趋势判断
    print(f"🔍 趋势判断:")
    if result['trend'] == 'up':
        print(f"   目前处于上涨趋势中，价格在均线上方运行")
    elif result['trend'] == 'down':
        print(f"   目前处于下跌趋势中，价格在均线下方运行")
    else:
        print(f"   目前处于震荡整理中，没有明确方向")
    print()
    
    # K线形态
    if result['pattern']:
        pattern = result['pattern']
        print(f"{pattern.emoji} K线形态分析:")
        print(f"{'─'*80}")
        print(f"\n{pattern.description}\n")
        print(f"{'─'*80}")
        
        # 给出操作建议
        print(f"\n💡 操作建议:")
        if pattern.signal == 'bullish':
            if result['trend'] == 'down':
                print(f"   虽然目前还在下跌趋势中，但出现了{pattern.pattern_name_cn}，")
                print(f"   说明可能要见底了。可以先观察，如果明天继续上涨，")
                print(f"   可以考虑小仓位试探。")
            else:
                print(f"   出现了{pattern.pattern_name_cn}，而且趋势也向上，")
                print(f"   这是比较好的信号。如果你还没买，可以考虑买入；")
                print(f"   如果已经持有，可以继续拿着。")
        
        elif pattern.signal == 'bearish':
            if result['trend'] == 'up':
                print(f"   虽然目前还在上涨趋势中，但出现了{pattern.pattern_name_cn}，")
                print(f"   这是一个警示信号。建议先减仓一部分，")
                print(f"   落袋为安，剩下的看情况再说。")
            else:
                print(f"   出现了{pattern.pattern_name_cn}，而且趋势也向下，")
                print(f"   这是比较危险的信号。如果你持有，建议考虑止损；")
                print(f"   如果还没买，那就先别买了。")
        
        else:  # neutral
            print(f"   出现了{pattern.pattern_name_cn}，说明多空双方在争夺，")
            print(f"   方向还不明确。这种时候最好的策略就是观望，")
            print(f"   等方向明确了再做决定。")
    
    else:
        print(f"⚪ K线形态分析:")
        print(f"{'─'*80}")
        print(f"\n今天的K线没有特别明显的形态，属于正常波动。")
        print(f"建议结合其他指标（如均线、成交量）综合判断。\n")
        print(f"{'─'*80}")
    
    # 显示最近3天的K线
    print(f"\n📈 最近3天走势:")
    print(f"{'─'*80}")
    
    recent = df.tail(3)
    for i, (_, row) in enumerate(recent.iterrows(), 1):
        date = row['date']
        open_p = row['open']
        close = row['close']
        pct_chg = row.get('pct_chg', 0.0)
        
        if close > open_p:
            candle = "🟢 阳线"
        elif close < open_p:
            candle = "🔴 阴线"
        else:
            candle = "⚪ 平盘"
        
        if i == len(recent):
            print(f"→ {date} {candle} 收{close:.2f}元 ({pct_chg:+.2f}%) ← 今天")
        else:
            print(f"  {date} {candle} 收{close:.2f}元 ({pct_chg:+.2f}%)")
    
    print(f"{'─'*80}\n")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("K线形态分析 - 分析师口吻版".center(80))
    print("="*80)
    print("\n像分析师一样，用讲故事的方式分析股票K线\n")
    
    # 分析几只股票
    stocks = [
        ('sh.600519', '贵州茅台'),
        ('sz.000858', '五粮液'),
        ('sh.600036', '招商银行'),
    ]
    
    for code, name in stocks:
        try:
            analyze_stock_like_analyst(code, name)
        except Exception as e:
            print(f"❌ 分析 {name} 失败: {e}\n")
    
    print("="*80)
    print("✅ 分析完成！")
    print("="*80 + "\n")
    
    print("💡 使用提示:")
    print("   这种分析方式更像是一个老师在给你讲解，")
    print("   而不是冷冰冰的技术指标。")
    print("   希望能帮你更好地理解K线形态的含义。\n")


if __name__ == '__main__':
    main()
