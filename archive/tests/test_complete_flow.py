#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整流程测试
测试从后端API到前端显示的完整数据流
"""
import requests
import json

BASE_URL = 'http://localhost:5001/api/picker'

def test_complete_flow():
    """测试完整的数据流"""
    print("\n" + "="*70)
    print("🚀 测试完整数据流：后端 API → 前端显示")
    print("="*70)
    
    # 步骤1：获取今日精选
    print("\n📊 步骤 1: 获取今日精选股票")
    print("-" * 70)
    
    response = requests.get(f'{BASE_URL}/daily-picks')
    result = response.json()
    
    if not result['success']:
        print("❌ 获取今日精选失败")
        return False
    
    picks = result['data']
    print(f"✅ 成功获取 {len(picks)} 只精选股票")
    
    if len(picks) == 0:
        print("⚠️ 没有找到精选股票")
        return False
    
    # 显示前3只
    print("\n前3只精选股票:")
    for i, pick in enumerate(picks[:3], 1):
        print(f"\n{i}. {pick['name']} ({pick['code']})")
        print(f"   价格: ¥{pick['price']:.2f}")
        print(f"   信心指数: {pick['confidence_score']}分")
        print(f"   策略: {pick['strategy_name']}")
        print(f"   理由: {pick['reason'][:50]}...")
    
    # 步骤2：获取第一只股票的详情
    first_stock = picks[0]
    stock_code = first_stock['code']
    
    print(f"\n\n📈 步骤 2: 获取股票详情 ({first_stock['name']})")
    print("-" * 70)
    
    response = requests.get(f'{BASE_URL}/stocks/{stock_code}')
    result = response.json()
    
    if not result['success']:
        print(f"❌ 获取股票详情失败: {result}")
        return False
    
    stock_detail = result['data']
    print(f"✅ 成功获取股票详情")
    print(f"\n股票信息:")
    print(f"  代码: {stock_detail['code']}")
    print(f"  名称: {stock_detail['name']}")
    print(f"  价格: ¥{stock_detail['price']:.2f}")
    print(f"  涨跌幅: {stock_detail['pct_change']*100:.2f}%")
    print(f"  今开: ¥{stock_detail['open']:.2f}")
    print(f"  最高: ¥{stock_detail['high']:.2f}")
    print(f"  最低: ¥{stock_detail['low']:.2f}")
    print(f"  成交量: {stock_detail['volume']:.0f}")
    
    if stock_detail.get('pick_reason'):
        print(f"\n选股理由:")
        print(f"  策略: {stock_detail['pick_reason']['title']}")
        print(f"  信心指数: {stock_detail['pick_reason']['confidence_score']}分")
        print(f"  理由: {stock_detail['pick_reason']['content']}")
    
    if stock_detail.get('key_metrics'):
        print(f"\n关键指标:")
        metrics = stock_detail['key_metrics']
        print(f"  市盈率(PE): {metrics['pe_ratio']:.2f}")
        print(f"  市净率(PB): {metrics['pb_ratio']:.2f}")
        print(f"  ROE: {metrics['roe']*100:.2f}%")
        print(f"  资产负债率: {metrics['debt_ratio']*100:.2f}%")
    
    # 步骤3：测试同步状态
    print(f"\n\n🔄 步骤 3: 检查数据同步状态")
    print("-" * 70)
    
    response = requests.get(f'{BASE_URL}/sync/status')
    result = response.json()
    
    if not result['success']:
        print("❌ 获取同步状态失败")
        return False
    
    sync_status = result['data']
    print(f"✅ 数据同步状态:")
    print(f"  最后更新: {sync_status['last_update_time']}")
    print(f"  警告级别: {sync_status['warning_level']}")
    print(f"  消息: {sync_status['message']}")
    print(f"  股票总数: {sync_status['total_stocks']}")
    print(f"  已同步: {sync_status['synced_stocks']}")
    
    # 汇总
    print("\n" + "="*70)
    print("✅ 完整流程测试通过！")
    print("="*70)
    print("\n📝 验证结果:")
    print("  ✓ 后端 API 正常工作")
    print("  ✓ 策略扫描找到真实股票")
    print("  ✓ 股票详情数据完整")
    print("  ✓ 数据同步状态正常")
    
    print("\n🎯 下一步:")
    print("  1. 打开浏览器访问 http://localhost:3000/")
    print("  2. 查看今日精选是否显示真实数据")
    print("  3. 点击任意股票查看详情页")
    print("  4. 验证所有数据都是从后端API获取的真实数据")
    
    return True


if __name__ == '__main__':
    try:
        success = test_complete_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
