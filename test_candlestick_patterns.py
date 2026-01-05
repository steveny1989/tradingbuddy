#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试K线形态识别

验证各种K线形态是否能正确识别
"""
from src.data.database import StockDatabase
from src.business.post_market.candlestick_patterns import analyze_candlestick_pattern


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*80}")
        print(f"{title:^80}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def test_stock_pattern(code: str, name: str = ""):
    """测试单只股票的K线形态"""
    print_separator(f"测试: {name} ({code})")
    
    # 获取数据
    db = StockDatabase()
    df = db.get_daily_data(code)
    
    if df.empty:
        print(f"❌ 无法获取 {code} 的数据\n")
        return
    
    # 按日期排序，取最近30天
    df = df.sort_values('date').tail(30).copy()
    
    print(f"✅ 数据加载成功: {len(df)} 天")
    print(f"   日期范围: {df['date'].min()} 至 {df['date'].max()}")
    
    # 分析K线形态
    result = analyze_candlestick_pattern(df)
    
    # 显示结果
    print(f"\n📊 K线形态分析:")
    print(f"   分析日期: {result['date']}")
    print(f"   趋势判断: {result['trend']}")
    
    if result['pattern']:
        pattern = result['pattern']
        print(f"\n{pattern.emoji} 识别到形态: {pattern.pattern_name_cn} ({pattern.pattern_name})")
        print(f"   信号: {pattern.signal_cn} ({pattern.signal})")
        print(f"   置信度: {pattern.confidence}")
        print(f"   💡 {pattern.description}")
    else:
        print(f"\n⚪ 未识别到特殊形态")
    
    # 显示最近5天的K线数据
    print(f"\n📈 最近5天K线数据:")
    print(f"{'─'*80}")
    
    recent = df.tail(5)
    for _, row in recent.iterrows():
        date = row['date']
        open_p = row['open']
        high = row['high']
        low = row['low']
        close = row['close']
        pct_chg = row.get('pct_chg', 0.0)
        
        # 判断阴阳
        if close > open_p:
            candle_type = "🟢 阳线"
        elif close < open_p:
            candle_type = "🔴 阴线"
        else:
            candle_type = "⚪ 平盘"
        
        print(f"{date} {candle_type}")
        print(f"  开: {open_p:.2f}  高: {high:.2f}  低: {low:.2f}  收: {close:.2f}  涨跌: {pct_chg:+.2f}%")
    
    print_separator()


def test_multiple_stocks():
    """测试多只股票"""
    print("\n" + "="*80)
    print("K线形态识别测试".center(80))
    print("="*80)
    
    # 测试股票列表
    test_stocks = [
        ('sh.600519', '贵州茅台'),
        ('sz.000858', '五粮液'),
        ('sh.600036', '招商银行'),
        ('sz.000001', '平安银行'),
        ('sz.300750', '宁德时代'),
    ]
    
    for code, name in test_stocks:
        try:
            test_stock_pattern(code, name)
        except Exception as e:
            print(f"❌ 测试 {name} ({code}) 失败: {e}\n")
            print_separator()
    
    print("✅ 所有测试完成！\n")


def test_pattern_examples():
    """测试特定形态示例"""
    print_separator("形态示例测试")
    
    from src.business.post_market.candlestick_patterns import PatternRecognizer
    
    print("测试1: 锤子线")
    print("  开: 100  高: 105  低: 95  收: 104")
    pattern = PatternRecognizer.recognize_single_candle(
        open_price=100,
        high=105,
        low=95,
        close=104,
        pct_chg=4.0,
        trend='down'
    )
    if pattern:
        print(f"  ✅ 识别到: {pattern.pattern_name_cn}")
        print(f"     {pattern.description}")
    else:
        print(f"  ⚪ 未识别到形态")
    
    print("\n测试2: 十字星")
    print("  开: 100  高: 102  低: 98  收: 100.5")
    pattern = PatternRecognizer.recognize_single_candle(
        open_price=100,
        high=102,
        low=98,
        close=100.5,
        pct_chg=0.5,
        trend='neutral'
    )
    if pattern:
        print(f"  ✅ 识别到: {pattern.pattern_name_cn}")
        print(f"     {pattern.description}")
    else:
        print(f"  ⚪ 未识别到形态")
    
    print("\n测试3: 大阳线")
    print("  开: 100  高: 108  低: 99  收: 107")
    pattern = PatternRecognizer.recognize_single_candle(
        open_price=100,
        high=108,
        low=99,
        close=107,
        pct_chg=7.0,
        trend='up'
    )
    if pattern:
        print(f"  ✅ 识别到: {pattern.pattern_name_cn}")
        print(f"     {pattern.description}")
    else:
        print(f"  ⚪ 未识别到形态")
    
    print("\n测试4: 看涨吞没")
    print("  Day1: 开100 高102 低98 收99 (阴线)")
    print("  Day2: 开98 高105 低97 收104 (阳线)")
    pattern = PatternRecognizer.recognize_two_candles(
        prev_open=100, prev_high=102, prev_low=98, prev_close=99,
        curr_open=98, curr_high=105, curr_low=97, curr_close=104
    )
    if pattern:
        print(f"  ✅ 识别到: {pattern.pattern_name_cn}")
        print(f"     {pattern.description}")
    else:
        print(f"  ⚪ 未识别到形态")
    
    print_separator()


def main():
    """主函数"""
    # 测试形态示例
    test_pattern_examples()
    
    # 测试真实股票
    test_multiple_stocks()


if __name__ == '__main__':
    main()
