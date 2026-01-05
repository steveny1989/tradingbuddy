#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析工具

计算ATR、分析市场波动、给出止损建议
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.database_adapter import DatabaseAdapter
from src.data.layers.feature_engine import FeatureEngine
import argparse


def analyze_risk(code: str, buy_price: float = None):
    """
    分析股票风险并给出止损建议
    
    Args:
        code: 股票代码
        buy_price: 买入价格（如果为None，使用最新收盘价）
    """
    print('='*70)
    print(f'风险分析报告: {code}')
    print('='*70)
    
    db = DatabaseAdapter()
    
    # 获取数据
    df = db.get_daily_data(code)
    
    if df is None or df.empty:
        print(f'\n❌ 没有找到股票 {code} 的数据')
        return
    
    # 计算ATR和波动率
    engine = FeatureEngine()
    df = engine.calculate_atr(df, period=14)
    df = engine.calculate_volatility(df, period=20)
    
    # 获取最新数据
    latest = df.iloc[-1]
    
    # 如果没有指定买入价，使用最新收盘价
    if buy_price is None:
        buy_price = latest['close']
    
    print(f'\n【基本信息】')
    print(f'  最新日期: {latest["date"]}')
    print(f'  最新收盘: {latest["close"]:.2f}')
    print(f'  买入价格: {buy_price:.2f}')
    
    # ATR分析
    print(f'\n【波动性分析】')
    print(f'  ATR (14日): {latest["atr"]:.4f}')
    print(f'  ATR百分比: {latest["atr_percent"]:.2f}%')
    print(f'  历史波动率: {latest["volatility"]:.2f}%')
    
    # 波动性评级
    atr_pct = latest["atr_percent"]
    if atr_pct < 1.5:
        volatility_level = "极低"
        volatility_desc = "市场非常平静"
        risk_level = "🟢 低风险"
    elif atr_pct < 2.5:
        volatility_level = "低"
        volatility_desc = "市场相对平静"
        risk_level = "🟢 低风险"
    elif atr_pct < 3.5:
        volatility_level = "中等"
        volatility_desc = "市场正常波动"
        risk_level = "🟡 中等风险"
    elif atr_pct < 5.0:
        volatility_level = "高"
        volatility_desc = "市场波动较大"
        risk_level = "🟠 高风险"
    else:
        volatility_level = "极高"
        volatility_desc = "市场剧烈波动"
        risk_level = "🔴 极高风险"
    
    print(f'\n  波动性等级: {volatility_level}')
    print(f'  市场状态: {volatility_desc}')
    print(f'  风险等级: {risk_level}')
    
    # ATR趋势分析
    print(f'\n【ATR趋势】')
    recent_atr = df.tail(20)['atr']
    atr_change = ((latest['atr'] - recent_atr.iloc[0]) / recent_atr.iloc[0]) * 100
    
    if atr_change > 20:
        trend = "📈 快速上升"
        trend_desc = "市场波动正在加剧，需要提高警惕"
    elif atr_change > 10:
        trend = "↗️ 上升"
        trend_desc = "市场波动有所增加"
    elif atr_change > -10:
        trend = "→ 平稳"
        trend_desc = "市场波动保持稳定"
    elif atr_change > -20:
        trend = "↘️ 下降"
        trend_desc = "市场波动有所减少"
    else:
        trend = "📉 快速下降"
        trend_desc = "市场波动正在减弱"
    
    print(f'  20日ATR变化: {atr_change:+.1f}%')
    print(f'  趋势: {trend}')
    print(f'  说明: {trend_desc}')
    
    # 止损建议
    print(f'\n【止损建议】')
    
    # 基于ATR的止损
    atr_value = latest['atr']
    
    # 保守止损：1倍ATR
    conservative_stop = buy_price - atr_value
    conservative_pct = ((buy_price - conservative_stop) / buy_price) * 100
    
    # 标准止损：1.5倍ATR
    standard_stop = buy_price - (atr_value * 1.5)
    standard_pct = ((buy_price - standard_stop) / buy_price) * 100
    
    # 宽松止损：2倍ATR
    loose_stop = buy_price - (atr_value * 2)
    loose_pct = ((buy_price - loose_stop) / buy_price) * 100
    
    print(f'\n  1️⃣ 保守止损（1倍ATR）')
    print(f'     止损价: {conservative_stop:.2f}')
    print(f'     止损幅度: {conservative_pct:.2f}%')
    print(f'     适用: 短线交易、低风险偏好')
    
    print(f'\n  2️⃣ 标准止损（1.5倍ATR）⭐ 推荐')
    print(f'     止损价: {standard_stop:.2f}')
    print(f'     止损幅度: {standard_pct:.2f}%')
    print(f'     适用: 中线持有、平衡风险收益')
    
    print(f'\n  3️⃣ 宽松止损（2倍ATR）')
    print(f'     止损价: {loose_stop:.2f}')
    print(f'     止损幅度: {loose_pct:.2f}%')
    print(f'     适用: 长线投资、高波动市场')
    
    # 根据波动性给出建议
    print(f'\n【个性化建议】')
    
    if atr_pct < 2.5:
        print(f'  • 当前波动性较低，可以使用较紧的止损（保守或标准）')
        print(f'  • 建议止损: {standard_stop:.2f} ({standard_pct:.1f}%)')
    elif atr_pct < 4.0:
        print(f'  • 当前波动性中等，建议使用标准止损')
        print(f'  • 建议止损: {standard_stop:.2f} ({standard_pct:.1f}%)')
    else:
        print(f'  • ⚠️  当前波动性较高，建议使用宽松止损')
        print(f'  • 建议止损: {loose_stop:.2f} ({loose_pct:.1f}%)')
        print(f'  • 或者等待波动降低后再入场')
    
    if atr_change > 20:
        print(f'  • ⚠️  ATR快速上升，市场波动加剧')
        print(f'  • 建议: 放宽止损范围或减少仓位')
    
    # 风险提示
    print(f'\n【风险提示】')
    print(f'  • 止损是风险管理的重要工具，但不是万能的')
    print(f'  • 在极端行情下，可能出现跳空缺口，无法按设定价格止损')
    print(f'  • 建议结合其他技术指标和基本面分析综合判断')
    print(f'  • 止损设置后要严格执行，不要因为情绪而改变计划')
    
    print('\n' + '='*70)


def compare_stocks(codes: list):
    """对比多只股票的波动性"""
    print('='*70)
    print('股票波动性对比')
    print('='*70)
    
    db = DatabaseAdapter()
    engine = FeatureEngine()
    
    results = []
    
    for code in codes:
        df = db.get_daily_data(code)
        if df is not None and not df.empty:
            df = engine.calculate_atr(df, period=14)
            latest = df.iloc[-1]
            
            results.append({
                'code': code,
                'close': latest['close'],
                'atr': latest['atr'],
                'atr_percent': latest['atr_percent'],
                'volatility': latest.get('volatility', 0)
            })
    
    if not results:
        print('\n❌ 没有找到任何股票数据')
        return
    
    # 排序（按ATR百分比）
    results.sort(key=lambda x: x['atr_percent'], reverse=True)
    
    print(f'\n{"股票代码":<10} {"最新价":<10} {"ATR":<10} {"ATR%":<10} {"波动性"}')
    print('-'*70)
    
    for r in results:
        volatility_icon = "🔴" if r['atr_percent'] > 4 else "🟡" if r['atr_percent'] > 2.5 else "🟢"
        print(f'{r["code"]:<10} {r["close"]:<10.2f} {r["atr"]:<10.4f} {r["atr_percent"]:<10.2f} {volatility_icon}')
    
    print('\n说明: 🟢 低波动  🟡 中波动  🔴 高波动')
    print('='*70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='风险分析工具')
    parser.add_argument('code', nargs='?', help='股票代码')
    parser.add_argument('--price', type=float, help='买入价格（默认使用最新收盘价）')
    parser.add_argument('--compare', nargs='+', help='对比多只股票的波动性')
    
    args = parser.parse_args()
    
    if args.compare:
        # 对比模式
        compare_stocks(args.compare)
    elif args.code:
        # 单只股票分析
        analyze_risk(args.code, args.price)
    else:
        # 显示帮助
        print('风险分析工具')
        print('\n用法:')
        print('  python3 tools/风险分析.py 601398')
        print('  python3 tools/风险分析.py 601398 --price 7.50')
        print('  python3 tools/风险分析.py --compare 601398 601939 601288')
        print('\n示例:')
        print('  601398 - 工商银行')
        print('  601939 - 建设银行')
        print('  601288 - 农业银行')


if __name__ == "__main__":
    main()
