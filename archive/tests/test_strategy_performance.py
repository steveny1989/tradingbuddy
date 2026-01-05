#!/usr/bin/env python3
"""
测试策略历史表现功能
Test Strategy Performance Functionality
"""
import sys
import requests
import json

BASE_URL = "http://localhost:5001"

def test_get_strategies():
    """测试获取策略列表"""
    print("\n=== 测试获取策略列表 ===")
    response = requests.get(f"{BASE_URL}/api/picker/strategies")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    return data

def test_get_strategy_performance(strategy_id):
    """测试获取策略表现"""
    print(f"\n=== 测试获取策略表现: {strategy_id} ===")
    response = requests.get(f"{BASE_URL}/api/picker/strategies/{strategy_id}/performance")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 验证响应格式
    if data.get('success'):
        result = data.get('data', {})
        print("\n验证响应字段:")
        required_fields = ['strategy_id', 'strategy_name', 'win_rate', 'avg_return', 'max_drawdown']
        for field in required_fields:
            if field in result:
                print(f"  ✓ {field}: {result[field]}")
            else:
                print(f"  ✗ {field}: 缺失")
    
    return data

def test_invalid_strategy():
    """测试无效策略ID"""
    print("\n=== 测试无效策略ID ===")
    response = requests.get(f"{BASE_URL}/api/picker/strategies/invalid_strategy/performance")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    return data

def main():
    """主测试函数"""
    try:
        # 1. 获取策略列表
        strategies_data = test_get_strategies()
        
        if not strategies_data.get('success'):
            print("❌ 获取策略列表失败")
            return
        
        strategies = strategies_data.get('data', [])
        print(f"\n找到 {len(strategies)} 个策略")
        
        # 2. 测试每个策略的表现
        for strategy in strategies:
            strategy_id = strategy.get('id')
            test_get_strategy_performance(strategy_id)
        
        # 3. 测试无效策略
        test_invalid_strategy()
        
        print("\n✅ 所有测试完成")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
        print("   运行命令: python -m src.web.app")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
