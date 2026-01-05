#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版持仓健康检查器 - 使用示例

展示如何使用新增的情绪面和财务面分析功能
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.post_market.portfolio_health import check_stock_health, check_portfolio_health


def example_1_single_stock():
    """示例1: 单只股票完整分析"""
    print('='*70)
    print('示例1: 单只股票完整分析')
    print('='*70)
    
    # 分析贵州茅台
    result = check_stock_health(
        code='600519',
        cost_price=1400,
        include_sentiment=True,    # 启用情绪面分析
        include_financial=True,    # 启用财务面分析
        include_sector=False,      # 暂时关闭行业面
        include_capital=False      # 暂时关闭资金面
    )
    
    # 打印综合判断
    print(f'\n【{result["name"]}】')
    print(f'综合状态: {result["overall_status"]}')
    print(f'综合建议: {result["overall_message"]}')
    
    # 打印各维度详情
    if result['sentiment']:
        sentiment = result['sentiment']
        print(f'\n情绪面:')
        print(f'  股性: {sentiment["character"]}')
        print(f'  平均振幅: {sentiment["volatility_analysis"]["avg_amplitude"]}%')
        print(f'  建议: {sentiment["message"]}')
    
    if result['financial']:
        financial = result['financial']
        print(f'\n财务面:')
        print(f'  ROE: {financial["profitability"]["roe"]}%')
        print(f'  负债率: {financial["solvency"]["debt_ratio"]}%')
        print(f'  风险评分: {financial["risk_score"]}/100')
        print(f'  建议: {financial["message"]}')


def example_2_portfolio():
    """示例2: 批量持仓检查"""
    print('\n\n' + '='*70)
    print('示例2: 批量持仓检查')
    print('='*70)
    
    # 模拟持仓
    holdings = [
        {'code': '600519', 'cost_price': 1400},  # 贵州茅台
        {'code': '601398', 'cost_price': 7.5},   # 工商银行
        {'code': '601939', 'cost_price': 9.5},   # 建设银行
    ]
    
    # 批量检查
    results = check_portfolio_health(
        holdings,
        include_sentiment=True,
        include_financial=True,
        include_sector=False,
        include_capital=False
    )
    
    # 打印结果
    print(f'\n持仓健康报告:')
    print(f'{"股票":<10} {"状态":<10} {"盈亏":<10} {"股性":<10} {"ROE":<10} {"负债率":<10}')
    print('-'*70)
    
    for r in results:
        technical = r['technical']
        sentiment = r.get('sentiment', {})
        financial = r.get('financial', {})
        
        status_icon = '🟢' if r['overall_status'] == 'green' else '🟡' if r['overall_status'] == 'yellow' else '🔴'
        profit = f"{technical.profit_rate:+.1f}%" if technical.profit_rate else 'N/A'
        character = sentiment.get('character', 'N/A')
        roe = f"{financial.get('profitability', {}).get('roe', 0):.1f}%"
        debt = f"{financial.get('solvency', {}).get('debt_ratio', 0):.1f}%"
        
        print(f'{r["name"]:<10} {status_icon:<10} {profit:<10} {character:<10} {roe:<10} {debt:<10}')


def example_3_sentiment_only():
    """示例3: 只分析情绪面"""
    print('\n\n' + '='*70)
    print('示例3: 只分析情绪面（识别妖股）')
    print('='*70)
    
    from src.business.post_market.sentiment_analysis import analyze_stock_sentiment
    
    # 分析几只不同股性的股票
    test_stocks = ['600519', '601398', '000001']
    
    for code in test_stocks:
        try:
            result = analyze_stock_sentiment(code, days=30)
            
            print(f'\n{code}:')
            print(f'  股性: {result["character"]}')
            print(f'  涨停次数: {result["limit_analysis"]["limit_up_days"]}次')
            print(f'  平均振幅: {result["volatility_analysis"]["avg_amplitude"]}%')
            print(f'  波动评分: {result["volatility_analysis"]["volatility_score"]}/100')
            print(f'  建议: {result["message"]}')
        except Exception as e:
            print(f'\n{code}: 分析失败 - {e}')


def example_4_financial_only():
    """示例4: 只分析财务面"""
    print('\n\n' + '='*70)
    print('示例4: 只分析财务面（财务风险评估）')
    print('='*70)
    
    from src.business.post_market.financial_risk import analyze_financial_risk
    
    # 分析几只不同财务状况的股票
    test_stocks = ['600519', '601398', '000001']
    
    for code in test_stocks:
        try:
            result = analyze_financial_risk(code)
            
            print(f'\n{code} - {result["name"]}:')
            
            if result.get('is_st'):
                print(f'  ⚠️  ST股票')
            
            prof = result.get('profitability', {})
            if prof.get('roe') is not None:
                print(f'  ROE: {prof["roe"]}% ({prof["roe_level"]})')
            
            solv = result.get('solvency', {})
            if solv.get('debt_ratio') is not None:
                print(f'  负债率: {solv["debt_ratio"]}% ({solv["debt_level"]})')
            
            print(f'  风险评分: {result["risk_score"]}/100')
            print(f'  建议: {result["message"]}')
        except Exception as e:
            print(f'\n{code}: 分析失败 - {e}')


def main():
    """主函数"""
    print('\n增强版持仓健康检查器 - 使用示例\n')
    
    # 运行所有示例
    example_1_single_stock()
    example_2_portfolio()
    example_3_sentiment_only()
    example_4_financial_only()
    
    print('\n\n' + '='*70)
    print('所有示例运行完成！')
    print('='*70)


if __name__ == "__main__":
    main()
