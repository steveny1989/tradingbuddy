#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模拟盘API
"""
import sys
sys.path.insert(0, '.')

from src.web.app import create_app
import json

def test_paper_trading_api():
    """测试模拟盘API"""
    app = create_app()
    client = app.test_client()
    
    print("=" * 80)
    print("测试模拟盘API")
    print("=" * 80)
    
    # 1. 测试获取模拟盘状态
    print("\n1. 测试获取模拟盘状态")
    response = client.get('/api/paper-trading/status')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['success'] == True
    assert 'account' in data['data']
    assert 'positions' in data['data']
    assert 'today_trades' in data['data']
    print("✅ 测试通过")
    
    # 2. 测试获取模拟盘绩效
    print("\n2. 测试获取模拟盘绩效")
    response = client.get('/api/paper-trading/performance')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['success'] == True
    assert 'metrics' in data['data']
    assert 'daily_values' in data['data']
    print("✅ 测试通过")
    
    # 3. 测试启动模拟盘
    print("\n3. 测试启动模拟盘（跳过，避免实际交易）")
    # response = client.post('/api/paper-trading/start', 
    #                        json={'date': '2024-01-02'})
    # print(f"状态码: {response.status_code}")
    # data = json.loads(response.data)
    # print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("⏭️  已跳过（避免实际交易）")
    
    # 4. 测试停止模拟盘
    print("\n4. 测试停止模拟盘")
    response = client.post('/api/paper-trading/stop')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['success'] == True
    print("✅ 测试通过")
    
    # 5. 测试重置模拟盘（跳过，避免清空数据）
    print("\n5. 测试重置模拟盘（跳过，避免清空数据）")
    # response = client.post('/api/paper-trading/reset')
    # print(f"状态码: {response.status_code}")
    # data = json.loads(response.data)
    # print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("⏭️  已跳过（避免清空数据）")
    
    print("\n" + "=" * 80)
    print("所有测试通过！")
    print("=" * 80)


if __name__ == '__main__':
    test_paper_trading_api()
