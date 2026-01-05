#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基本面分析器

快速测试基本面分析器的功能
"""
import sys
sys.path.insert(0, '.')

from src.business.diagnosis.fundamental_analyzer import FundamentalAnalyzer


def test_fundamental_analyzer():
    """测试基本面分析器"""
    print("=" * 80)
    print("测试基本面分析器")
    print("=" * 80)
    print()
    
    # 创建分析器
    analyzer = FundamentalAnalyzer()
    
    # 测试几只股票
    test_stocks = [
        ('600519', '贵州茅台'),
        ('000858', '五粮液'),
        ('600036', '招商银行'),
    ]
    
    for code, name in test_stocks:
        print(f"\n{'='*80}")
        print(f"分析股票: {code} - {name}")
        print('='*80)
        
        try:
            result = analyzer.analyze(code)
            
            print(f"\n评分: {result['score']}")
            print(f"状态: {result['status']}")
            print(f"描述: {result['message']}")
            print(f"\n详细数据:")
            
            details = result['details']
            if details.get('pe'):
                print(f"  PE: {details['pe']:.2f}")
            if details.get('pb'):
                print(f"  PB: {details['pb']:.2f}")
            if details.get('roe'):
                print(f"  ROE: {details['roe']:.2f}%")
            if details.get('roa'):
                print(f"  ROA: {details['roa']:.2f}%")
            if details.get('net_margin'):
                print(f"  净利率: {details['net_margin']:.2f}%")
            if details.get('debt_ratio'):
                print(f"  资产负债率: {details['debt_ratio']:.2f}%")
            if details.get('current_ratio'):
                print(f"  流动比率: {details['current_ratio']:.2f}")
            
            if details.get('profit_growth_yoy'):
                print(f"  净利润同比增长: {details['profit_growth_yoy']:.2f}%")
            if details.get('revenue_growth_yoy'):
                print(f"  营收同比增长: {details['revenue_growth_yoy']:.2f}%")
            
            if details.get('industry'):
                print(f"\n行业: {details['industry']}")
                
                industry_comp = details.get('industry_comparison', {})
                if industry_comp:
                    print(f"行业对比:")
                    if 'roe_percentile' in industry_comp:
                        print(f"  ROE百分位: {industry_comp['roe_percentile']}%")
                    if 'pe_percentile' in industry_comp:
                        print(f"  PE百分位: {industry_comp['pe_percentile']}%")
                    if 'industry_stock_count' in industry_comp:
                        print(f"  行业股票数: {industry_comp['industry_stock_count']}")
            
        except Exception as e:
            print(f"分析失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("测试完成")
    print('='*80)


if __name__ == '__main__':
    test_fundamental_analyzer()
