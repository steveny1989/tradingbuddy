#!/usr/bin/env python3
"""
测试极简选股助手 API
"""
import requests
import json

BASE_URL = 'http://localhost:5555/api'

def test_get_golden_strategies():
    """测试获取金牌策略列表"""
    print("\n=== 测试: 获取金牌策略列表 ===")
    
    response = requests.get(f'{BASE_URL}/picker/strategies')
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert len(data['data']) >= 2  # 至少有2个金牌策略
    
    # 检查策略字段
    for strategy in data['data']:
        assert 'id' in strategy
        assert 'name' in strategy
        assert 'description' in strategy
        assert 'suitable_for' in strategy
        assert 'risk_level' in strategy
        
        # 确保没有技术参数
        assert 'params' not in strategy
        assert 'ma_short' not in strategy['name'].lower()
        assert 'ma20' not in strategy['description'].lower()
    
    print("✅ 测试通过")


def test_get_daily_picks():
    """测试获取今日精选"""
    print("\n=== 测试: 获取今日精选 ===")
    
    response = requests.get(f'{BASE_URL}/picker/daily-picks?limit=3')
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['data']) <= 3  # 最多3只
    
    # 检查字段
    for pick in data['data']:
        assert 'code' in pick
        assert 'name' in pick
        assert 'price' in pick
        assert 'confidence_score' in pick
        assert 'reason' in pick
        assert 'strategy_id' in pick
        assert 'strategy_name' in pick
        
        # 检查信号强度在合理范围
        assert 30 <= pick['confidence_score'] <= 100
        
        # 确保理由是大白话（不包含技术术语）
        reason = pick['reason'].lower()
        assert 'ma5' not in reason
        assert 'ma20' not in reason
        assert 'rsi' not in reason
        
        print(f"\n股票: {pick['name']} ({pick['code']})")
        print(f"价格: {pick['price']}")
        print(f"信号强度: {pick['confidence_score']}")
        print(f"选股理由: {pick['reason']}")
        print(f"策略: {pick['strategy_name']}")
    
    print("\n✅ 测试通过")


if __name__ == '__main__':
    print("请先启动后端服务: PORT=5555 python3 src/web/app.py")
    print("然后运行此测试脚本")
    
    try:
        test_get_golden_strategies()
        test_get_daily_picks()
        print("\n🎉 所有测试通过!")
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请先启动后端服务")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
