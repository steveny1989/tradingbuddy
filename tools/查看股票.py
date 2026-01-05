#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票查询工具

快速查看股票的基本信息和技术指标
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.database_adapter import DatabaseAdapter
import argparse


def format_number(num):
    """格式化数字"""
    if num >= 1e8:
        return f'{num/1e8:.2f}亿'
    elif num >= 1e4:
        return f'{num/1e4:.2f}万'
    else:
        return f'{num:.0f}'


def show_stock(code: str, days: int = 10):
    """显示股票信息"""
    print('='*70)
    print(f'股票查询: {code}')
    print('='*70)
    
    db = DatabaseAdapter()
    
    # 获取数据
    df = db.get_daily_data(code)
    
    if df is None or df.empty:
        print(f'\n❌ 没有找到股票 {code} 的数据')
        print('\n提示: 请使用6位数字代码，如 601398（工商银行）')
        return
    
    print(f'\n✅ 找到数据: {len(df)} 条记录')
    print(f'日期范围: {df["date"].min()} ~ {df["date"].max()}')
    
    # 最新数据
    latest = df.iloc[-1]
    print(f'\n【最新行情】({latest["date"]})')
    print(f'  开盘: {latest["open"]:.2f}')
    print(f'  最高: {latest["high"]:.2f}')
    print(f'  最低: {latest["low"]:.2f}')
    print(f'  收盘: {latest["close"]:.2f}')
    
    if latest["open"] > 0:
        change = (latest["close"] - latest["open"]) / latest["open"] * 100
        print(f'  涨跌: {change:+.2f}%')
    
    print(f'  成交量: {format_number(latest["volume"])}')
    if "amount" in latest and latest["amount"] > 0:
        print(f'  成交额: {format_number(latest["amount"])}')
    
    # 历史数据
    print(f'\n【最近{days}个交易日】')
    recent = df.sort_values('date', ascending=False).head(days)
    print(f'{"日期":<12} {"开盘":>8} {"收盘":>8} {"涨跌":>8} {"成交量":>12}')
    print('-'*70)
    
    for _, row in recent.iterrows():
        change = ((row['close'] - row['open']) / row['open'] * 100) if row['open'] > 0 else 0
        change_str = f'{change:+.2f}%'
        volume_str = format_number(row['volume'])
        print(f'{row["date"]:<12} {row["open"]:>8.2f} {row["close"]:>8.2f} {change_str:>8} {volume_str:>12}')
    
    # 技术指标
    print(f'\n【技术指标】')
    indicators = db.get_indicators(code)
    
    if indicators is not None and not indicators.empty:
        latest_ind = indicators.iloc[-1]
        print(f'  日期: {latest_ind["date"]}')
        print(f'\n  均线系统:')
        print(f'    MA5:   {latest_ind["ma5"]:.2f}')
        print(f'    MA10:  {latest_ind["ma10"]:.2f}')
        print(f'    MA20:  {latest_ind["ma20"]:.2f}')
        print(f'    MA50:  {latest_ind["ma50"]:.2f}')
        
        print(f'\n  技术指标:')
        print(f'    RSI:   {latest_ind["rsi"]:.2f}')
        print(f'    MACD:  {latest_ind["macd"]:.4f}')
        print(f'    KDJ_K: {latest_ind["kdj_k"]:.2f}')
        print(f'    KDJ_D: {latest_ind["kdj_d"]:.2f}')
        
        # 简单分析
        print(f'\n  简单分析:')
        
        # RSI 分析
        if latest_ind["rsi"] > 70:
            print(f'    • RSI超买（{latest_ind["rsi"]:.1f} > 70），可能回调')
        elif latest_ind["rsi"] < 30:
            print(f'    • RSI超卖（{latest_ind["rsi"]:.1f} < 30），可能反弹')
        else:
            print(f'    • RSI正常区间（{latest_ind["rsi"]:.1f}）')
        
        # 均线分析
        if latest["close"] > latest_ind["ma20"]:
            print(f'    • 股价在MA20上方，趋势向上')
        else:
            print(f'    • 股价在MA20下方，趋势向下')
        
        # MACD 分析
        if latest_ind["macd"] > 0:
            print(f'    • MACD金叉，多头信号')
        else:
            print(f'    • MACD死叉，空头信号')
    else:
        print('  暂无技术指标数据')
    
    print('\n' + '='*70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票查询工具')
    parser.add_argument('code', help='股票代码（如 601398）')
    parser.add_argument('--days', type=int, default=10, help='显示最近N天数据（默认10天）')
    
    args = parser.parse_args()
    
    show_stock(args.code, args.days)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 没有参数，显示示例
        print('股票查询工具')
        print('\n用法:')
        print('  python3 tools/查看股票.py 601398')
        print('  python3 tools/查看股票.py 600519 --days 20')
        print('\n示例:')
        print('  601398 - 中国工商银行')
        print('  600519 - 贵州茅台')
        print('  000858 - 五粮液')
    else:
        main()
