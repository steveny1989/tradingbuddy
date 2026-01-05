#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试持仓健康检查器

验证红绿灯系统是否正常工作
"""
from src.business.post_market.portfolio_health import check_stock_health, check_portfolio_health


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*80}")
        print(f"{title:^80}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def test_single_stock():
    """测试单只股票"""
    print_separator("测试1: 单只股票健康检查")
    
    # 测试贵州茅台
    code = 'sh.600519'
    cost_price = 1400.0
    
    print(f"股票代码: {code}")
    print(f"成本价格: {cost_price}元\n")
    
    try:
        health = check_stock_health(code, cost_price)
        
        # 显示结果
        print(f"📊 股票名称: {health.name}")
        print(f"💰 当前价格: {health.current_price:.2f}元")
        print(f"📈 涨跌幅: {health.change_rate:+.2f}%")
        
        if health.profit_rate is not None:
            emoji = "📈" if health.profit_rate > 0 else "📉"
            print(f"{emoji} 盈亏比例: {health.profit_rate:+.2f}%")
        
        print(f"\n🔍 技术指标:")
        print(f"   MA20: {health.ma20:.2f}元")
        print(f"   MA20偏离度: {health.ma20_deviation:+.2f}%")
        print(f"   量比: {health.volume_ratio:.2f}")
        
        print(f"\n📊 信号分析:")
        print(f"   均线信号: {health.ma_signal}")
        print(f"   成交量信号: {health.volume_signal}")
        
        # 显示健康状态（红绿灯）
        status_emoji = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }
        
        print(f"\n{status_emoji[health.status]} 健康状态: {health.status_cn}")
        print(f"💡 操作建议: {health.recommendation}")
        
        print_separator()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print_separator()


def test_multiple_stocks():
    """测试多只股票"""
    print_separator("测试2: 批量持仓健康检查")
    
    # 模拟持仓
    holdings = [
        {'code': 'sh.600519', 'cost_price': 1400.0},  # 贵州茅台
        {'code': 'sz.000858', 'cost_price': 150.0},   # 五粮液
        {'code': 'sh.600036', 'cost_price': 40.0},    # 招商银行
    ]
    
    print("持仓列表:")
    for i, h in enumerate(holdings, 1):
        print(f"  {i}. {h['code']} (成本: {h['cost_price']}元)")
    print()
    
    try:
        results = check_portfolio_health(holdings)
        
        # 统计各状态数量
        status_count = {'green': 0, 'yellow': 0, 'red': 0}
        for health in results:
            status_count[health.status] += 1
        
        print(f"📊 持仓健康统计:")
        print(f"   🟢 健康: {status_count['green']}只")
        print(f"   🟡 警示: {status_count['yellow']}只")
        print(f"   🔴 危险: {status_count['red']}只")
        print()
        
        # 显示每只股票的详细信息
        status_emoji = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }
        
        for i, health in enumerate(results, 1):
            print(f"{i}. {status_emoji[health.status]} {health.name} ({health.code})")
            print(f"   当前价: {health.current_price:.2f}元 | 涨跌: {health.change_rate:+.2f}%", end="")
            
            if health.profit_rate is not None:
                emoji = "📈" if health.profit_rate > 0 else "📉"
                print(f" | {emoji} 盈亏: {health.profit_rate:+.2f}%")
            else:
                print()
            
            print(f"   MA20偏离: {health.ma20_deviation:+.2f}% | 量比: {health.volume_ratio:.2f}")
            print(f"   💡 {health.recommendation}")
            print()
        
        print_separator()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print_separator()


def test_edge_cases():
    """测试边界情况"""
    print_separator("测试3: 边界情况测试")
    
    test_cases = [
        {
            'name': '超买股票',
            'code': 'sh.600519',
            'description': '测试RSI>70的超买情况'
        },
        {
            'name': '超卖股票',
            'code': 'sz.000858',
            'description': '测试RSI<30的超卖情况'
        },
    ]
    
    for case in test_cases:
        print(f"测试场景: {case['name']}")
        print(f"说明: {case['description']}")
        print()
        
        try:
            health = check_stock_health(case['code'])
            
            status_emoji = {
                'green': '🟢',
                'yellow': '🟡',
                'red': '🔴'
            }
            
            print(f"   {status_emoji[health.status]} 状态: {health.status_cn}")
            print(f"   💡 建议: {health.recommendation}")
            print()
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}\n")
    
    print_separator()


def main():
    """主函数"""
    print("\n" + "="*80)
    print("持仓健康检查器测试".center(80))
    print("="*80)
    
    # 测试1: 单只股票
    test_single_stock()
    
    # 测试2: 多只股票
    test_multiple_stocks()
    
    # 测试3: 边界情况
    test_edge_cases()
    
    print("✅ 所有测试完成！\n")


if __name__ == '__main__':
    main()
