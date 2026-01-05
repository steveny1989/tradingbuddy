#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓健康检查示例

展示如何使用持仓健康检查器来分析你的股票
"""
from src.business.post_market.portfolio_health import check_stock_health, check_portfolio_health


def example_1_single_stock():
    """示例1: 检查单只股票"""
    print("\n" + "="*80)
    print("示例1: 检查单只股票的健康状态")
    print("="*80 + "\n")
    
    # 假设你持有贵州茅台，成本价1400元
    code = 'sh.600519'
    cost_price = 1400.0
    
    print(f"我持有: {code}")
    print(f"成本价: {cost_price}元\n")
    
    # 检查健康状态
    health = check_stock_health(code, cost_price)
    
    # 显示结果
    print(f"📊 {health.name} ({health.code})")
    print(f"{'─'*80}")
    
    # 价格信息
    print(f"\n💰 价格信息:")
    print(f"   当前价: {health.current_price:.2f}元")
    print(f"   成本价: {cost_price:.2f}元")
    
    if health.profit_rate is not None:
        if health.profit_rate > 0:
            print(f"   📈 盈利: +{health.profit_rate:.2f}% (赚了 {(health.current_price - cost_price) * 100:.2f}元/100股)")
        else:
            print(f"   📉 亏损: {health.profit_rate:.2f}% (亏了 {abs(health.current_price - cost_price) * 100:.2f}元/100股)")
    
    print(f"   今日涨跌: {health.change_rate:+.2f}%")
    
    # 技术分析（用人话说）
    print(f"\n🔍 技术分析 (小白版):")
    
    # 1. 均线分析
    print(f"\n   1️⃣ 趋势分析 (看20日均线)")
    print(f"      当前价: {health.current_price:.2f}元")
    print(f"      MA20: {health.ma20:.2f}元 (最近20天的平均价)")
    
    if health.ma20_deviation > 0:
        print(f"      ✅ 价格在均线上方 {health.ma20_deviation:.1f}% - 短期趋势向上")
    elif health.ma20_deviation < -5:
        print(f"      ⚠️ 价格在均线下方 {abs(health.ma20_deviation):.1f}% - 跌得有点多了")
    else:
        print(f"      ⚪ 价格接近均线 ({health.ma20_deviation:+.1f}%) - 在均线附近震荡")
    
    # 2. 量比分析
    print(f"\n   2️⃣ 资金分析 (看量比)")
    print(f"      量比: {health.volume_ratio:.2f}")
    
    if health.volume_ratio > 1.5:
        print(f"      🔥 放量 - 今天成交量是平时的{health.volume_ratio:.1f}倍，有人在买")
    elif health.volume_ratio < 0.7:
        print(f"      🧊 缩量 - 今天成交量只有平时的{health.volume_ratio:.1f}倍，没人买")
    else:
        print(f"      ⚪ 正常 - 成交量正常，不多不少")
    
    # 健康状态
    status_emoji = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    }
    
    status_desc = {
        'green': '健康 - 可以继续持有',
        'yellow': '警示 - 需要注意风险',
        'red': '危险 - 考虑止损'
    }
    
    print(f"\n{status_emoji[health.status]} 健康状态: {status_desc[health.status]}")
    print(f"{'─'*80}")
    print(f"💡 操作建议: {health.recommendation}")
    print(f"{'─'*80}\n")


def example_2_portfolio():
    """示例2: 检查整个持仓"""
    print("\n" + "="*80)
    print("示例2: 检查整个持仓的健康状态")
    print("="*80 + "\n")
    
    # 假设你的持仓
    my_holdings = [
        {'code': 'sh.600519', 'cost_price': 1400.0},  # 贵州茅台
        {'code': 'sz.000858', 'cost_price': 150.0},   # 五粮液
        {'code': 'sh.600036', 'cost_price': 40.0},    # 招商银行
    ]
    
    print("我的持仓:")
    for i, h in enumerate(my_holdings, 1):
        print(f"  {i}. {h['code']} (成本: {h['cost_price']}元)")
    print()
    
    # 批量检查
    results = check_portfolio_health(my_holdings)
    
    # 统计
    status_count = {'green': 0, 'yellow': 0, 'red': 0}
    total_profit = 0
    
    for health in results:
        status_count[health.status] += 1
        if health.profit_rate:
            total_profit += health.profit_rate
    
    # 显示统计
    print("="*80)
    print("持仓健康报告")
    print("="*80 + "\n")
    
    print(f"📊 整体情况:")
    print(f"   总持仓: {len(results)}只")
    print(f"   🟢 健康: {status_count['green']}只")
    print(f"   🟡 警示: {status_count['yellow']}只")
    print(f"   🔴 危险: {status_count['red']}只")
    
    if len(results) > 0:
        avg_profit = total_profit / len(results)
        print(f"   平均盈亏: {avg_profit:+.2f}%")
    
    print(f"\n{'─'*80}\n")
    
    # 显示每只股票
    status_emoji = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    }
    
    for i, health in enumerate(results, 1):
        print(f"{i}. {status_emoji[health.status]} {health.name} ({health.code})")
        print(f"   {'─'*76}")
        
        # 价格和盈亏
        print(f"   当前价: {health.current_price:.2f}元", end="")
        if health.profit_rate is not None:
            if health.profit_rate > 0:
                print(f" | 📈 盈利 {health.profit_rate:+.2f}%", end="")
            else:
                print(f" | 📉 亏损 {health.profit_rate:.2f}%", end="")
        print(f" | 今日 {health.change_rate:+.2f}%")
        
        # 技术指标
        print(f"   MA20偏离: {health.ma20_deviation:+.2f}% | 量比: {health.volume_ratio:.2f}")
        
        # 建议
        print(f"   💡 {health.recommendation}")
        print()
    
    # 总结建议
    print("="*80)
    print("📝 总结建议:")
    print("="*80 + "\n")
    
    if status_count['red'] > 0:
        print(f"⚠️ 你有 {status_count['red']} 只股票处于危险状态，建议优先处理：")
        for health in results:
            if health.status == 'red':
                print(f"   • {health.name}: {health.recommendation}")
        print()
    
    if status_count['green'] > 0:
        print(f"✅ 你有 {status_count['green']} 只股票状态健康，可以继续持有")
        print()
    
    if status_count['yellow'] > 0:
        print(f"⚠️ 你有 {status_count['yellow']} 只股票需要观察，密切关注")
        print()


def example_3_explain_indicators():
    """示例3: 解释技术指标（给小白看的）"""
    print("\n" + "="*80)
    print("示例3: 技术指标解释 (小白版)")
    print("="*80 + "\n")
    
    print("我们用3个简单的指标来判断股票健康：\n")
    
    print("1️⃣ MA20 (20日均线) - 看趋势")
    print("   ├─ 什么是MA20？")
    print("   │  最近20天的平均价格")
    print("   │")
    print("   ├─ 怎么看？")
    print("   │  • 价格在MA20上方 → 趋势向上 ✅")
    print("   │  • 价格在MA20下方 → 趋势向下 ⚠️")
    print("   │")
    print("   └─ 偏离度是什么？")
    print("      (当前价 - MA20) / MA20 × 100%")
    print("      • 偏离度 > +10% → 涨太多了，可能回调")
    print("      • 偏离度 < -10% → 跌太多了，可能反弹")
    print()
    
    print("2️⃣ 量比 - 看资金")
    print("   ├─ 什么是量比？")
    print("   │  今天的成交量 / 最近5天平均成交量")
    print("   │")
    print("   ├─ 怎么看？")
    print("   │  • 量比 > 1.5 → 放量，有人在买 🔥")
    print("   │  • 量比 < 0.7 → 缩量，没人买 🧊")
    print("   │  • 0.7-1.5 → 正常 ⚪")
    print("   │")
    print("   └─ 为什么重要？")
    print("      • 价格上涨 + 放量 = 真涨 ✅")
    print("      • 价格上涨 + 缩量 = 假涨 ⚠️")
    print()
    
    print("3️⃣ 红绿灯系统 - 综合判断")
    print("   ├─ 🟢 绿灯 (健康)")
    print("   │  • 价格在MA20上方")
    print("   │  • 量比正常或放量")
    print("   │  → 建议: 继续持有")
    print("   │")
    print("   ├─ 🟡 黄灯 (警示)")
    print("   │  • 价格接近MA20")
    print("   │  • 或者缩量")
    print("   │  → 建议: 观望，注意风险")
    print("   │")
    print("   └─ 🔴 红灯 (危险)")
    print("      • 价格跌破MA20")
    print("      • 或者大跌 > 5%")
    print("      → 建议: 考虑止损")
    print()


def main():
    """主函数"""
    print("\n" + "="*80)
    print("持仓健康检查器 - 使用示例")
    print("="*80)
    
    # 示例1: 单只股票
    example_1_single_stock()
    
    # 示例2: 整个持仓
    example_2_portfolio()
    
    # 示例3: 指标解释
    example_3_explain_indicators()
    
    print("="*80)
    print("✅ 示例演示完成！")
    print("="*80 + "\n")
    
    print("💡 使用提示:")
    print("   1. 每天收盘后运行一次，了解持仓健康状况")
    print("   2. 重点关注红灯股票，及时止损")
    print("   3. 绿灯股票可以安心持有")
    print("   4. 黄灯股票需要密切观察\n")


if __name__ == '__main__':
    main()
