#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能分析器

对比新旧分析器的差异
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.post_market.smart_analyzer import smart_analyze


def print_analysis(code: str, cost_price: float = None):
    """打印分析结果"""
    print('='*80)
    print(f'智能分析: {code}')
    print('='*80)
    
    result = smart_analyze(code, cost_price)
    
    data = result['data']
    analysis = result['analysis']
    industry_profile = result['industry_profile']
    
    # 基本信息
    print(f'\n【基本信息】')
    print(f'  股票: {data.name} ({data.code})')
    if data.industry:
        print(f'  行业: {data.industry}')
        if industry_profile:
            print(f'  行业特性: {industry_profile["description"]}')
    if data.is_st:
        print(f'  ⚠️  ST股票')
    
    # 数据汇总
    print(f'\n【数据汇总】')
    print(f'\n  技术面:')
    print(f'    当前价: {data.current_price:.2f}')
    if data.cost_price:
        profit_rate = (data.current_price - data.cost_price) / data.cost_price * 100
        print(f'    成本价: {data.cost_price:.2f}')
        print(f'    盈亏: {profit_rate:+.2f}%')
    print(f'    MA20偏离: {data.ma20_deviation:+.2f}%')
    print(f'    RSI: {data.rsi:.0f}')
    print(f'    量比: {data.volume_ratio:.2f}')
    print(f'    布林线: 上轨{data.boll_upper:.2f} 中轨{data.boll_middle:.2f} 下轨{data.boll_lower:.2f}')
    print(f'    布林位置: {data.boll_position*100:.1f}% (0%=下轨, 100%=上轨)')
    print(f'    布林带宽: {data.boll_width:.1f}%')
    print(f'    MACD: DIF={data.macd_dif:.3f} DEA={data.macd_dea:.3f} MACD={data.macd_macd:.3f}')
    print(f'    MACD信号: {data.macd_signal}')
    print(f'    KDJ: K={data.kdj_k:.1f} D={data.kdj_d:.1f} J={data.kdj_j:.1f}')
    print(f'    KDJ信号: {data.kdj_signal}')
    
    print(f'\n  情绪面:')
    print(f'    股性: {data.stock_character}')
    print(f'    涨停次数: {data.limit_up_days}次(近30天)')
    print(f'    平均振幅: {data.avg_amplitude:.2f}%')
    print(f'    波动评分: {data.volatility_score:.1f}/100')
    
    print(f'\n  财务面:')
    if data.report_date:
        print(f'    报告期: {data.report_date}')
    if data.roe is not None:
        print(f'    ROE: {data.roe:.2f}% ({data.roe_level})')
        if data.industry_avg_roe:
            print(f'    行业平均ROE: {data.industry_avg_roe:.2f}%')
    if data.net_margin is not None:
        print(f'    净利率: {data.net_margin:.2f}%')
    if data.eps is not None:
        print(f'    EPS: {data.eps:.2f}')
    if data.debt_ratio is not None:
        print(f'    负债率: {data.debt_ratio:.2f}% ({data.debt_level})')
        if data.industry_avg_debt:
            print(f'    行业平均负债率: {data.industry_avg_debt:.2f}%')
        if industry_profile:
            normal_min, normal_max = industry_profile['normal_debt_ratio']
            print(f'    行业正常范围: {normal_min}-{normal_max}%')
    if data.current_ratio is not None:
        print(f'    流动比率: {data.current_ratio:.2f}')
    
    # 分析结果
    print(f'\n【分析结果】')
    
    tech = analysis['technical']
    print(f'\n  技术面: {tech["status"]}')
    print(f'    {tech["message"]}')
    
    sent = analysis['sentiment']
    print(f'\n  情绪面: {sent["status"]}')
    print(f'    {sent["message"]}')
    
    fin = analysis['financial']
    print(f'\n  财务面: {fin["status"]}')
    print(f'    {fin["message"]}')
    
    kline = analysis['kline']
    print(f'\n  K线形态: {kline["status"]}')
    if data.kline_pattern:
        print(f'    形态: {data.kline_pattern_cn} ({data.kline_signal})')
    print(f'    {kline["message"]}')
    
    overall = analysis['overall']
    status_icon = '🟢' if overall['status'] == 'green' else '🟡' if overall['status'] == 'yellow' else '🔴'
    print(f'\n  {status_icon} 综合判断: {overall["status"]}')
    print(f'    {overall["message"]}')
    
    print('\n' + '='*80 + '\n')


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试智能分析器')
    parser.add_argument('--code', help='股票代码')
    parser.add_argument('--price', type=float, help='成本价格')
    
    args = parser.parse_args()
    
    if args.code:
        print_analysis(args.code, args.price)
    else:
        # 默认测试几只典型股票
        print('\n测试典型股票...\n')
        
        print('\n1. 贵州茅台 - 白酒行业（低负债高ROE）')
        print_analysis('600519', 1400)
        
        print('\n2. 建设银行 - 银行业（高负债是正常的）')
        print_analysis('601939', 9.5)
        
        print('\n3. 工商银行 - 银行业（高负债是正常的）')
        print_analysis('601398', 7.5)


if __name__ == "__main__":
    main()
