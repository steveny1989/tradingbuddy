#!/usr/bin/env python3
"""
完整测试极简选股助手 API - Checkpoint 8
测试所有后端 API 端点是否正常工作
"""
import requests
import json
import sys
from datetime import datetime

# 使用实际运行的端口
BASE_URL = 'http://localhost:5001/api'

def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(success, message):
    """打印测试结果"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    return success

def test_1_golden_strategies():
    """测试1: 获取金牌策略列表"""
    print_section("测试1: 获取金牌策略列表")
    
    try:
        response = requests.get(f'{BASE_URL}/picker/strategies', timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            return print_result(False, f"状态码错误: {response.status_code}")
        
        data = response.json()
        
        if not data.get('success'):
            return print_result(False, f"API返回失败: {data.get('error')}")
        
        strategies = data.get('data', [])
        print(f"策略数量: {len(strategies)}")
        
        if len(strategies) < 2:
            return print_result(False, f"策略数量不足，期望至少2个，实际{len(strategies)}个")
        
        # 检查每个策略的字段
        required_fields = ['id', 'name', 'description', 'suitable_for', 'risk_level']
        for strategy in strategies:
            print(f"\n策略: {strategy.get('name')}")
            print(f"  描述: {strategy.get('description')}")
            print(f"  适合人群: {strategy.get('suitable_for')}")
            print(f"  风险等级: {strategy.get('risk_level')}")
            
            for field in required_fields:
                if field not in strategy:
                    return print_result(False, f"策略缺少必需字段: {field}")
            
            # 确保没有技术参数泄露
            if 'params' in strategy or 'ma_short' in str(strategy).lower():
                return print_result(False, "策略包含技术参数，应该隐藏")
        
        return print_result(True, "金牌策略列表测试通过")
        
    except requests.exceptions.ConnectionError:
        return print_result(False, "无法连接到服务器")
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def test_2_daily_picks():
    """测试2: 获取今日精选"""
    print_section("测试2: 获取今日精选")
    
    try:
        response = requests.get(f'{BASE_URL}/picker/daily-picks?limit=5', timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            return print_result(False, f"状态码错误: {response.status_code}")
        
        data = response.json()
        
        if not data.get('success'):
            return print_result(False, f"API返回失败: {data.get('error')}")
        
        picks = data.get('data', [])
        print(f"精选股票数量: {len(picks)}")
        
        if len(picks) > 5:
            return print_result(False, f"返回数量超过限制，期望最多5个，实际{len(picks)}个")
        
        # 检查每只股票的字段
        required_fields = ['code', 'name', 'price', 'confidence_score', 'reason', 'strategy_id', 'strategy_name']
        technical_terms = ['ma5', 'ma20', 'rsi', 'macd', 'kdj', 'boll']
        
        for pick in picks:
            print(f"\n股票: {pick.get('name')} ({pick.get('code')})")
            print(f"  价格: {pick.get('price')}")
            print(f"  信号强度: {pick.get('confidence_score')}")
            print(f"  策略: {pick.get('strategy_name')}")
            print(f"  理由: {pick.get('reason')}")
            
            for field in required_fields:
                if field not in pick:
                    return print_result(False, f"股票缺少必需字段: {field}")
            
            # 检查信号强度范围
            score = pick.get('confidence_score', 0)
            if not (30 <= score <= 100):
                return print_result(False, f"信号强度超出范围: {score}")
            
            # 检查理由是否包含技术术语
            reason = pick.get('reason', '').lower()
            for term in technical_terms:
                if term in reason:
                    return print_result(False, f"选股理由包含技术术语: {term}")
        
        # 检查排序（按信号强度降序）
        if len(picks) > 1:
            for i in range(len(picks) - 1):
                if picks[i]['confidence_score'] < picks[i+1]['confidence_score']:
                    return print_result(False, "精选股票未按信号强度降序排列")
        
        return print_result(True, "今日精选测试通过")
        
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def test_3_watchlist():
    """测试3: 获取自选股数据"""
    print_section("测试3: 获取自选股数据")
    
    try:
        # 测试数据
        test_data = {
            "stocks": [
                {
                    "code": "000001",
                    "add_time": "2025-01-01 10:00:00",
                    "add_price": 10.0,
                    "stop_loss": -0.10,
                    "take_profit": 0.20
                },
                {
                    "code": "600000",
                    "add_time": "2025-01-01 10:00:00",
                    "add_price": 8.0,
                    "stop_loss": -0.10,
                    "take_profit": 0.20
                }
            ]
        }
        
        response = requests.post(
            f'{BASE_URL}/picker/watchlist',
            json=test_data,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            return print_result(False, f"状态码错误: {response.status_code}")
        
        data = response.json()
        
        if not data.get('success'):
            return print_result(False, f"API返回失败: {data.get('error')}")
        
        watchlist = data.get('data', [])
        print(f"自选股数量: {len(watchlist)}")
        
        # 检查每只自选股的字段
        required_fields = ['code', 'name', 'current_price', 'change_pct', 'add_time', 
                          'add_price', 'profit_pct', 'signal', 'stop_loss', 'take_profit']
        
        for item in watchlist:
            print(f"\n股票: {item.get('name')} ({item.get('code')})")
            print(f"  添加价格: {item.get('add_price')}")
            print(f"  当前价格: {item.get('current_price')}")
            print(f"  盈亏: {item.get('profit_pct', 0)*100:.2f}%")
            print(f"  信号: {item.get('signal', {}).get('label')}")
            
            for field in required_fields:
                if field not in item:
                    return print_result(False, f"自选股缺少必需字段: {field}")
            
            # 检查信号字段
            signal = item.get('signal', {})
            if not all(k in signal for k in ['signal', 'label', 'color']):
                return print_result(False, "信号字段不完整")
            
            # 检查预警
            if item.get('alert'):
                alert = item['alert']
                print(f"  ⚠️ 预警: {alert.get('type')} - {alert.get('message')}")
                
                required_alert_fields = ['type', 'message', 'current_price', 'target_price']
                for field in required_alert_fields:
                    if field not in alert:
                        return print_result(False, f"预警缺少必需字段: {field}")
        
        return print_result(True, "自选股数据测试通过")
        
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def test_4_strategy_performance():
    """测试4: 获取策略历史表现"""
    print_section("测试4: 获取策略历史表现")
    
    try:
        # 测试两个策略
        strategy_ids = ['low_volume_breakout', 'ma_golden_cross']
        
        for strategy_id in strategy_ids:
            print(f"\n测试策略: {strategy_id}")
            
            response = requests.get(
                f'{BASE_URL}/picker/strategies/{strategy_id}/performance',
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code != 200:
                return print_result(False, f"状态码错误: {response.status_code}")
            
            data = response.json()
            
            if not data.get('success'):
                return print_result(False, f"API返回失败: {data.get('error')}")
            
            performance = data.get('data', {})
            
            # 检查必需字段
            required_fields = ['strategy_id', 'strategy_name', 'win_rate', 
                             'avg_return', 'max_drawdown', 'total_backtests']
            
            for field in required_fields:
                if field not in performance:
                    return print_result(False, f"策略表现缺少必需字段: {field}")
            
            print(f"  策略名称: {performance.get('strategy_name')}")
            print(f"  胜率: {performance.get('win_rate', 0)*100:.2f}%")
            print(f"  平均收益: {performance.get('avg_return', 0)*100:.2f}%")
            print(f"  最大回撤: {performance.get('max_drawdown', 0)*100:.2f}%")
            print(f"  回测次数: {performance.get('total_backtests', 0)}")
        
        return print_result(True, "策略历史表现测试通过")
        
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def test_5_sync_trigger():
    """测试5: 触发数据同步"""
    print_section("测试5: 触发数据同步")
    
    try:
        response = requests.post(f'{BASE_URL}/picker/sync', timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            return print_result(False, f"状态码错误: {response.status_code}")
        
        data = response.json()
        
        if not data.get('success'):
            return print_result(False, f"API返回失败: {data.get('error')}")
        
        result = data.get('data', {})
        
        # 检查必需字段
        if 'task_id' not in result or 'status' not in result:
            return print_result(False, "同步响应缺少必需字段")
        
        print(f"任务ID: {result.get('task_id')}")
        print(f"状态: {result.get('status')}")
        print(f"消息: {result.get('message')}")
        
        return print_result(True, "触发数据同步测试通过")
        
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def test_6_sync_status():
    """测试6: 获取同步状态"""
    print_section("测试6: 获取同步状态")
    
    try:
        response = requests.get(f'{BASE_URL}/picker/sync/status', timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            return print_result(False, f"状态码错误: {response.status_code}")
        
        data = response.json()
        
        if not data.get('success'):
            return print_result(False, f"API返回失败: {data.get('error')}")
        
        status = data.get('data', {})
        
        # 检查必需字段
        required_fields = ['last_update_time', 'warning_level', 'message', 
                          'total_stocks', 'synced_stocks']
        
        for field in required_fields:
            if field not in status:
                return print_result(False, f"同步状态缺少必需字段: {field}")
        
        print(f"最后更新时间: {status.get('last_update_time')}")
        print(f"警告级别: {status.get('warning_level')}")
        print(f"消息: {status.get('message')}")
        print(f"总股票数: {status.get('total_stocks')}")
        print(f"已同步股票数: {status.get('synced_stocks')}")
        
        # 检查警告级别是否合法
        warning_level = status.get('warning_level')
        if warning_level not in ['none', 'yellow', 'red']:
            return print_result(False, f"警告级别不合法: {warning_level}")
        
        return print_result(True, "获取同步状态测试通过")
        
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def test_7_error_handling():
    """测试7: 错误处理和友好提示"""
    print_section("测试7: 错误处理和友好提示")
    
    try:
        # 测试不存在的策略
        response = requests.get(
            f'{BASE_URL}/picker/strategies/non_existent/performance',
            timeout=10
        )
        
        print(f"测试不存在的策略 - 状态码: {response.status_code}")
        
        if response.status_code != 404:
            return print_result(False, f"期望404，实际{response.status_code}")
        
        data = response.json()
        
        if data.get('success'):
            return print_result(False, "期望失败响应，实际成功")
        
        error_message = data.get('error', '')
        print(f"错误消息: {error_message}")
        
        # 检查错误消息是否友好（不包含技术术语）
        technical_terms = ['api', 'database', 'sql', 'http', '500', 'exception']
        for term in technical_terms:
            if term in error_message.lower():
                return print_result(False, f"错误消息包含技术术语: {term}")
        
        return print_result(True, "错误处理测试通过")
        
    except Exception as e:
        return print_result(False, f"测试出错: {e}")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  极简选股助手 API 完整测试")
    print("  Checkpoint 8: 后端 API 完成")
    print("="*60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 运行所有测试
    tests = [
        test_1_golden_strategies,
        test_2_daily_picks,
        test_3_watchlist,
        test_4_strategy_performance,
        test_5_sync_trigger,
        test_6_sync_status,
        test_7_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ 测试执行失败: {e}")
            results.append(False)
    
    # 打印总结
    print_section("测试总结")
    passed = sum(results)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！后端 API 工作正常！")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
