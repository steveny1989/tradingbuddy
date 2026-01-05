#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本面分析器使用示例

演示如何使用基本面分析器分析股票
"""
import sys
sys.path.insert(0, '.')

from src.business.diagnosis.fundamental_analyzer import FundamentalAnalyzer


def example_basic_usage():
    """示例1: 基本使用"""
    print("=" * 80)
    print("示例 1: 基本使用")
    print("=" * 80)
    print()
    
    # 创建分析器
    analyzer = FundamentalAnalyzer()
    
    # 分析股票
    code = '600519'
    print(f"分析股票: {code}")
    
    result = analyzer.analyze(code)
    
    print(f"评分: {result['score']}")
    print(f"状态: {result['status']}")
    print(f"描述: {result['message']}")
    print()


def example_with_details():
    """示例2: 查看详细数据"""
    print("=" * 80)
    print("示例 2: 查看详细数据")
    print("=" * 80)
    print()
    
    analyzer = FundamentalAnalyzer()
    result = analyzer.analyze('600519')
    
    details = result['details']
    
    print("财务指标:")
    print(f"  PE: {details.get('pe', 'N/A')}")
    print(f"  PB: {details.get('pb', 'N/A')}")
    print(f"  ROE: {details.get('roe', 'N/A')}")
    print(f"  ROA: {details.get('roa', 'N/A')}")
    print(f"  净利率: {details.get('net_margin', 'N/A')}")
    print(f"  资产负债率: {details.get('debt_ratio', 'N/A')}")
    print(f"  流动比率: {details.get('current_ratio', 'N/A')}")
    print()
    
    print("增长指标:")
    print(f"  净利润同比增长: {details.get('profit_growth_yoy', 'N/A')}")
    print(f"  营收同比增长: {details.get('revenue_growth_yoy', 'N/A')}")
    print()
    
    if details.get('industry'):
        print(f"行业: {details['industry']}")
        
        industry_comp = details.get('industry_comparison', {})
        if industry_comp:
            print("行业对比:")
            print(f"  ROE百分位: {industry_comp.get('roe_percentile', 'N/A')}")
            print(f"  PE百分位: {industry_comp.get('pe_percentile', 'N/A')}")
    print()


def example_scoring_explanation():
    """示例3: 评分规则说明"""
    print("=" * 80)
    print("示例 3: 评分规则说明")
    print("=" * 80)
    print()
    
    print("基本面评分规则 (总分100分):")
    print()
    
    print("1. ROE评分 (30分):")
    print("   - ROE >= 15%: 30分")
    print("   - ROE >= 10%: 25分")
    print("   - ROE >= 5%: 15分")
    print("   - ROE >= 0%: 5分")
    print("   - ROE < 0%: 0分")
    print()
    
    print("2. 盈利增长评分 (25分):")
    print("   - 增长 >= 20%: 25分")
    print("   - 增长 >= 10%: 20分")
    print("   - 增长 >= 5%: 15分")
    print("   - 增长 >= 0%: 10分")
    print("   - 增长 >= -10%: 5分")
    print("   - 增长 < -10%: 0分")
    print()
    
    print("3. PE合理性评分 (20分):")
    print("   - 与行业对比，PE在30-60百分位: 20分")
    print("   - 或绝对值在10-30之间: 20分")
    print()
    
    print("4. 财务健康评分 (25分):")
    print("   a) 负债率评分 (12.5分):")
    print("      - 负债率 <= 30%: 12.5分")
    print("      - 负债率 <= 50%: 10分")
    print("      - 负债率 <= 70%: 6分")
    print("      - 负债率 > 70%: 2分")
    print()
    print("   b) 流动比率评分 (12.5分):")
    print("      - 流动比率 >= 2.0: 12.5分")
    print("      - 流动比率 >= 1.5: 10分")
    print("      - 流动比率 >= 1.0: 6分")
    print("      - 流动比率 < 1.0: 2分")
    print()
    
    print("状态判断:")
    print("  - 评分 >= 70: green (优秀)")
    print("  - 评分 >= 50: yellow (一般)")
    print("  - 评分 < 50: red (较弱)")
    print()


def example_mock_data():
    """示例4: 模拟数据演示"""
    print("=" * 80)
    print("示例 4: 模拟数据演示")
    print("=" * 80)
    print()
    
    print("假设某股票的财务数据如下:")
    print("  ROE: 18% (高盈利能力)")
    print("  净利润增长: 15% (良好增长)")
    print("  PE: 25 (合理估值)")
    print("  资产负债率: 25% (财务稳健)")
    print("  流动比率: 2.5 (流动性充足)")
    print()
    
    print("评分计算:")
    print("  ROE评分: 30分 (ROE >= 15%)")
    print("  盈利增长评分: 20分 (增长 >= 10%)")
    print("  PE合理性评分: 20分 (PE在10-30之间)")
    print("  负债率评分: 12.5分 (负债率 <= 30%)")
    print("  流动比率评分: 12.5分 (流动比率 >= 2.0)")
    print()
    print("  总分: 95分")
    print("  状态: green (优秀)")
    print("  描述: 基本面优秀；盈利能力强(ROE 18.0%)；利润增长良好(15.0%)；财务稳健")
    print()


if __name__ == '__main__':
    print("\n基本面分析器使用示例\n")
    
    example_basic_usage()
    example_with_details()
    example_scoring_explanation()
    example_mock_data()
    
    print("=" * 80)
    print("所有示例完成")
    print("=" * 80)
    print()
    print("注意: 如果数据库中没有财务数据，分析器会返回'基本面数据不足'的结果。")
    print("      这是正常的容错处理。实际使用时需要先使用 tools/fetch_financial_data.py")
    print("      获取财务数据。")
    print()
