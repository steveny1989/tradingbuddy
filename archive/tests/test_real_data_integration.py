#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实数据集成
验证后端API能否返回真实的选股数据
"""
import requests
import json

BASE_URL = 'http://localhost:5001/api/picker'

def test_daily_picks():
    """测试今日精选API"""
    print("\n" + "="*60)
    print("测试今日精选 API")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/daily-picks')
    result = response.json()
    
    if result['success']:
        picks = result['data']
        print(f"\n✅ 成功获取 {len(picks)} 只精选股票:\n")
        
        for i, pick in enumerate(picks[:5], 1):  # 只显示前5只
            print(f"{i}. {pick['code']} {pick['name']}")
            print(f"   价格: ¥{pick['price']:.2f}")
            print(f"   信心指数: {pick['confidence_score']}分")
            print(f"   策略: {pick['strategy_name']}")
            print(f"   理由: {pick['reason']}")
            print()
        
        return True
    else:
        print(f"\n❌ 获取失败: {result}")
        return False


def test_sync_status():
    """测试同步状态API"""
    print("\n" + "="*60)
    print("测试同步状态 API")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/sync/status')
    result = response.json()
    
    if result['success']:
        data = result['data']
        print(f"\n✅ 同步状态:")
        print(f"   最后更新: {data['last_update_time']}")
        print(f"   警告级别: {data['warning_level']}")
        print(f"   消息: {data['message']}")
        print(f"   股票总数: {data['total_stocks']}")
        print(f"   已同步: {data['synced_stocks']}")
        print()
        
        return True
    else:
        print(f"\n❌ 获取失败: {result}")
        return False


def test_strategies():
    """测试策略列表API"""
    print("\n" + "="*60)
    print("测试策略列表 API")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/strategies')
    result = response.json()
    
    if result['success']:
        strategies = result['data']
        print(f"\n✅ 成功获取 {len(strategies)} 个策略:\n")
        
        for strategy in strategies:
            print(f"• {strategy['name']}")
            print(f"  {strategy['description']}")
            print(f"  适合: {strategy['suitable_for']}")
            print(f"  风险: {strategy['risk_level']}")
            print()
        
        return True
    else:
        print(f"\n❌ 获取失败: {result}")
        return False


def main():
    print("\n🚀 开始测试真实数据集成...")
    
    results = []
    
    # 测试各个API
    results.append(("今日精选", test_daily_picks()))
    results.append(("同步状态", test_sync_status()))
    results.append(("策略列表", test_strategies()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！真实数据集成成功！")
        print("\n📝 下一步:")
        print("   1. 打开浏览器访问 http://localhost:3000/")
        print("   2. 查看今日精选是否显示真实股票数据")
        print("   3. 点击股票查看详情页")
    else:
        print("\n⚠️ 部分测试失败，请检查后端服务")
    
    print()


if __name__ == '__main__':
    main()
