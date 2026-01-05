#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版持仓健康检查器

测试新增的情绪面和财务面分析功能
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.post_market.portfolio_health import PortfolioHealthChecker


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f'\n{"="*70}')
        print(f'{title:^70}')
        print(f'{"="*70}\n')
    else:
        print(f'{"="*70}\n')


def test_single_stock(code: str, cost_price: float = None):
    """测试单只股票的完整分析"""
    print_separator(f"测试股票: {code}")
    
    checker = PortfolioHealthChecker()
    
    try:
        result = checker.check_stock(
            code=code,
            cost_price=cost_price,
            include_sentiment=True,
            include_financial=True,
            include_sector=False,  # 暂时关闭行业面
            include_capital=False  # 暂时关闭资金面
        )
        
        # 打印综合判断
        print(f'【综合判断】')
        status_icon = '🟢' if result['overall_status'] == 'green' else '🟡' if result['overall_status'] == 'yellow' else '🔴'
        print(f'  {status_icon} {result["name"]} ({result["code"]})')
        print(f'  状态: {result["overall_status"]}')
        print(f'  建议: {result["overall_message"]}')
        
        # 打印技术面
        technical = result['technical']
        print(f'\n【技术面分析】')
        print(f'  当前价格: {technical.current_price:.2f}')
        if technical.cost_price:
            print(f'  成本价格: {technical.cost_price:.2f}')
            print(f'  盈亏比例: {technical.profit_rate:+.2f}%')
        print(f'  涨跌幅: {technical.change_rate:+.2f}%')
        print(f'  MA20偏离: {technical.ma20_deviation:+.2f}%')
        print(f'  量比: {technical.volume_ratio:.2f}')
        print(f'  状态: {technical.status_cn}')
        print(f'  建议: {technical.recommendation}')
        
        # 打印情绪面
        if result['sentiment']:
            sentiment = result['sentiment']
            print(f'\n【情绪面分析】')
            print(f'  股性: {sentiment["character"]}')
            
            limit = sentiment['limit_analysis']
            print(f'  涨停次数: {limit["limit_up_days"]}次（近{sentiment["analysis_days"]}天）')
            if limit['max_consecutive_up'] > 0:
                print(f'  最高连板: {limit["max_consecutive_up"]}板')
            if limit['yesterday_limit_up']:
                print(f'  ⚠️  昨日涨停')
            
            vol = sentiment['volatility_analysis']
            print(f'  平均振幅: {vol["avg_amplitude"]:.2f}%')
            print(f'  波动评分: {vol["volatility_score"]:.1f}/100')
            
            print(f'  状态: {sentiment["status"]}')
            print(f'  建议: {sentiment["message"]}')
        
        # 打印财务面
        if result['financial']:
            financial = result['financial']
            print(f'\n【财务面分析】')
            
            if financial.get('is_st'):
                print(f'  ⚠️  ST股票')
            
            if financial.get('report_date'):
                print(f'  报告期: {financial["report_date"]}')
            
            prof = financial.get('profitability', {})
            if prof.get('roe') is not None:
                print(f'  ROE: {prof["roe"]:.2f}% ({prof["roe_level"]})')
            if prof.get('net_margin') is not None:
                print(f'  净利率: {prof["net_margin"]:.2f}%')
            if prof.get('eps') is not None:
                print(f'  EPS: {prof["eps"]:.2f}')
            
            solv = financial.get('solvency', {})
            if solv.get('debt_ratio') is not None:
                print(f'  资产负债率: {solv["debt_ratio"]:.2f}% ({solv["debt_level"]})')
            if solv.get('current_ratio') is not None:
                print(f'  流动比率: {solv["current_ratio"]:.2f}')
            
            print(f'  风险评分: {financial["risk_score"]:.1f}/100')
            print(f'  状态: {financial["status"]}')
            print(f'  建议: {financial["message"]}')
        
        print_separator()
        
        return result
        
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()
        return None


def test_multiple_stocks():
    """测试多只股票"""
    print_separator("批量测试多只股票")
    
    test_stocks = [
        {'code': '600519', 'name': '贵州茅台', 'cost_price': 1400},
        {'code': '601398', 'name': '工商银行', 'cost_price': 7.5},
        {'code': '601939', 'name': '建设银行', 'cost_price': 9.5},
    ]
    
    for stock in test_stocks:
        print(f'\n测试 {stock["name"]} ({stock["code"]})...')
        result = test_single_stock(stock['code'], stock['cost_price'])
        if result:
            print(f'✅ {stock["name"]} 测试完成')
        else:
            print(f'❌ {stock["name"]} 测试失败')


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试增强版持仓健康检查器')
    parser.add_argument('--code', help='股票代码')
    parser.add_argument('--price', type=float, help='成本价格')
    parser.add_argument('--batch', action='store_true', help='批量测试')
    
    args = parser.parse_args()
    
    if args.batch:
        test_multiple_stocks()
    elif args.code:
        test_single_stock(args.code, args.price)
    else:
        # 默认测试贵州茅台
        print('默认测试贵州茅台...\n')
        test_single_stock('600519', 1400)
        
        print('\n\n提示: 使用 --code 指定股票代码，--batch 批量测试')


if __name__ == "__main__":
    main()
