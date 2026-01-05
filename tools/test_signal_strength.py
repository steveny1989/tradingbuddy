#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试信号强度分级系统

展示不同信号强度的分析效果
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.post_market.smart_analyzer import smart_analyze


def print_signal_analysis(code: str, name: str, cost_price: float = None):
    """打印信号分析"""
    print('='*80)
    print(f'{name} ({code})')
    print('='*80)
    
    result = smart_analyze(code, cost_price)
    
    data = result['data']
    analysis = result['analysis']
    
    # 技术面信号
    tech = analysis['technical']
    print(f'\n技术面: {tech["status"]}')
    print(f'  {tech["message"]}')
    
    # 关键指标
    print(f'\n关键指标:')
    print(f'  MACD: {data.macd_signal}')
    print(f'  KDJ: {data.kdj_signal}')
    print(f'  布林位置: {data.boll_position*100:.1f}%')
    print(f'  RSI: {data.rsi:.0f}')
    print(f'  量比: {data.volume_ratio:.2f}')
    
    # K线形态
    kline = analysis['kline']
    if data.kline_signal:
        print(f'  K线信号: {data.kline_signal}')
    
    # 综合判断
    overall = analysis['overall']
    status_icon = '🟢' if overall['status'] == 'green' else '🟡' if overall['status'] == 'yellow' else '🔴'
    print(f'\n{status_icon} 综合判断: {overall["message"]}')
    
    print('\n')


def main():
    """主函数"""
    print('\n' + '='*80)
    print('信号强度分级系统测试')
    print('='*80 + '\n')
    
    print('测试不同信号强度的股票...\n')
    
    # 测试1: 中性信号
    print('\n【案例1: 中性信号】')
    print_signal_analysis('601939', '建设银行', 9.5)
    
    # 测试2: 偏多信号（KDJ金叉）
    print('\n【案例2: 偏多信号（KDJ金叉）】')
    print_signal_analysis('601398', '工商银行', 7.5)
    
    # 测试3: 看涨信号（K线+指标共振）
    print('\n【案例3: 看涨信号（K线形态）】')
    print_signal_analysis('600519', '贵州茅台', 1400)
    
    # 测试4: 活跃股
    print('\n【案例4: 活跃股】')
    print_signal_analysis('000425', '徐工机械')
    
    print('\n' + '='*80)
    print('信号强度说明:')
    print('='*80)
    print('''
强烈看涨 🟢🟢🟢 (5分+):
  - MACD金叉 + KDJ金叉 + 触及布林下轨 + RSI超卖
  - 多个强信号共振，准确率最高

看涨 🟢🟢 (3-4分):
  - MACD金叉 + KDJ金叉
  - 或 MACD多头 + KDJ金叉 + 放量
  
偏多 🟢 (1-2分):
  - KDJ金叉
  - 或 MACD多头 + 站稳MA20

中性 🟡 (0分):
  - 信号矛盾或不明显
  - 观望为主

偏空 🔴 (-1~-2分):
  - KDJ死叉
  - 或 MACD空头 + 跌破MA20

看跌 🔴🔴 (-3~-4分):
  - MACD死叉 + KDJ死叉
  - 或 MACD死叉 + 突破布林上轨

强烈看跌 🔴🔴🔴 (-5分以下):
  - MACD死叉 + KDJ死叉 + 突破布林上轨 + RSI超买
  - 多个强信号共振，风险极高
''')


if __name__ == "__main__":
    main()
