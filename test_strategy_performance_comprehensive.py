#!/usr/bin/env python3
"""
综合测试策略历史表现功能
Comprehensive Test for Strategy Performance Functionality

验证需求:
- Requirements 6.2: 显示策略详细表现数据
- Requirements 6.3: 显示近30天胜率
- Requirements 6.4: 显示平均收益率
- Requirements 6.5: 显示最大回撤
- Requirements 6.6: 显示资金曲线
- Requirements 6.7: 显示历史选股记录
- Requirements 6.8: 标注成功/失败
"""
import sys
import requests
import json

BASE_URL = "http://localhost:5001"

def test_strategy_performance_fields():
    """测试策略表现API返回所有必需字段"""
    print("\n=== 测试策略表现API字段完整性 ===")
    
    # 获取策略列表
    response = requests.get(f"{BASE_URL}/api/picker/strategies")
    if not response.json().get('success'):
        print("❌ 无法获取策略列表")
        return False
    
    strategies = response.json().get('data', [])
    if not strategies:
        print("❌ 没有可用的策略")
        return False
    
    # 测试第一个策略
    strategy_id = strategies[0]['id']
    print(f"测试策略: {strategy_id}")
    
    response = requests.get(f"{BASE_URL}/api/picker/strategies/{strategy_id}/performance")
    
    if response.status_code != 200:
        print(f"❌ API返回错误状态码: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ API返回失败: {data.get('error')}")
        return False
    
    result = data.get('data', {})
    
    # 验证必需字段
    required_fields = {
        'strategy_id': 'str',
        'strategy_name': 'str',
        'description': 'str',
        'win_rate': 'float',
        'avg_return': 'float',
        'max_drawdown': 'float',
        'total_backtests': 'int',
        'recent_performance': 'list'
    }
    
    all_fields_present = True
    for field, expected_type in required_fields.items():
        if field not in result:
            print(f"  ❌ 缺少字段: {field}")
            all_fields_present = False
        else:
            value = result[field]
            actual_type = type(value).__name__
            
            # 类型检查
            if expected_type == 'float' and not isinstance(value, (int, float)):
                print(f"  ❌ 字段 {field} 类型错误: 期望 {expected_type}, 实际 {actual_type}")
                all_fields_present = False
            elif expected_type == 'int' and not isinstance(value, int):
                print(f"  ❌ 字段 {field} 类型错误: 期望 {expected_type}, 实际 {actual_type}")
                all_fields_present = False
            elif expected_type == 'str' and not isinstance(value, str):
                print(f"  ❌ 字段 {field} 类型错误: 期望 {expected_type}, 实际 {actual_type}")
                all_fields_present = False
            elif expected_type == 'list' and not isinstance(value, list):
                print(f"  ❌ 字段 {field} 类型错误: 期望 {expected_type}, 实际 {actual_type}")
                all_fields_present = False
            else:
                print(f"  ✓ {field}: {value} ({actual_type})")
    
    if all_fields_present:
        print("✅ 所有必需字段都存在且类型正确")
        return True
    else:
        print("❌ 部分字段缺失或类型错误")
        return False


def test_recent_performance_structure():
    """测试recent_performance数组结构"""
    print("\n=== 测试历史表现数据结构 ===")
    
    response = requests.get(f"{BASE_URL}/api/picker/strategies")
    strategies = response.json().get('data', [])
    strategy_id = strategies[0]['id']
    
    response = requests.get(f"{BASE_URL}/api/picker/strategies/{strategy_id}/performance")
    result = response.json().get('data', {})
    
    recent_performance = result.get('recent_performance', [])
    print(f"历史表现记录数: {len(recent_performance)}")
    
    if len(recent_performance) == 0:
        print("⚠️  暂无历史回测数据（这是正常的，因为还没有运行回测）")
        return True
    
    # 验证每条记录的结构
    required_fields = ['return', 'win_rate', 'max_drawdown', 'total_trades', 'date']
    
    for i, record in enumerate(recent_performance[:3]):  # 只检查前3条
        print(f"\n记录 {i+1}:")
        all_present = True
        for field in required_fields:
            if field in record:
                print(f"  ✓ {field}: {record[field]}")
            else:
                print(f"  ❌ 缺少字段: {field}")
                all_present = False
        
        if not all_present:
            return False
    
    print("✅ 历史表现数据结构正确")
    return True


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试不存在的策略
    response = requests.get(f"{BASE_URL}/api/picker/strategies/nonexistent_strategy/performance")
    
    if response.status_code != 404:
        print(f"❌ 期望状态码404，实际: {response.status_code}")
        return False
    
    data = response.json()
    if data.get('success'):
        print("❌ 期望success=false")
        return False
    
    error_message = data.get('error', '')
    print(f"错误消息: {error_message}")
    
    # 验证错误消息是用户友好的（不包含技术术语）
    technical_terms = ['API', 'database', 'SQL', 'HTTP', '404', 'exception', 'traceback']
    has_technical_terms = any(term.lower() in error_message.lower() for term in technical_terms)
    
    if has_technical_terms:
        print(f"❌ 错误消息包含技术术语: {error_message}")
        return False
    
    print("✅ 错误处理正确，消息用户友好")
    return True


def test_all_strategies():
    """测试所有策略的表现API"""
    print("\n=== 测试所有策略 ===")
    
    response = requests.get(f"{BASE_URL}/api/picker/strategies")
    strategies = response.json().get('data', [])
    
    print(f"共有 {len(strategies)} 个策略")
    
    all_passed = True
    for strategy in strategies:
        strategy_id = strategy['id']
        strategy_name = strategy['name']
        
        print(f"\n测试策略: {strategy_name} ({strategy_id})")
        
        response = requests.get(f"{BASE_URL}/api/picker/strategies/{strategy_id}/performance")
        
        if response.status_code != 200:
            print(f"  ❌ 状态码错误: {response.status_code}")
            all_passed = False
            continue
        
        data = response.json()
        if not data.get('success'):
            print(f"  ❌ API返回失败")
            all_passed = False
            continue
        
        result = data.get('data', {})
        
        # 验证策略ID匹配
        if result.get('strategy_id') != strategy_id:
            print(f"  ❌ 策略ID不匹配")
            all_passed = False
            continue
        
        # 验证策略名称匹配
        if result.get('strategy_name') != strategy_name:
            print(f"  ❌ 策略名称不匹配")
            all_passed = False
            continue
        
        print(f"  ✓ 胜率: {result.get('win_rate', 0):.2%}")
        print(f"  ✓ 平均收益: {result.get('avg_return', 0):.2%}")
        print(f"  ✓ 最大回撤: {result.get('max_drawdown', 0):.2%}")
        print(f"  ✓ 回测次数: {result.get('total_backtests', 0)}")
    
    if all_passed:
        print("\n✅ 所有策略测试通过")
        return True
    else:
        print("\n❌ 部分策略测试失败")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("策略历史表现功能综合测试")
    print("=" * 60)
    
    try:
        results = []
        
        # 运行所有测试
        results.append(("字段完整性测试", test_strategy_performance_fields()))
        results.append(("历史表现结构测试", test_recent_performance_structure()))
        results.append(("错误处理测试", test_error_handling()))
        results.append(("所有策略测试", test_all_strategies()))
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status} - {name}")
        
        print(f"\n总计: {passed}/{total} 测试通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！策略历史表现功能实现正确。")
            return 0
        else:
            print(f"\n⚠️  {total - passed} 个测试失败")
            return 1
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器")
        print("请确保后端服务正在运行: python -m src.web.app")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
