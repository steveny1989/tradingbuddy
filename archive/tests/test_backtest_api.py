#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试回测API
"""
import sys
sys.path.insert(0, '.')

from src.web.app import create_app
from src.data.database import StockDatabase
import json
from datetime import datetime

def test_backtest_api():
    """测试回测API"""
    app = create_app()
    client = app.test_client()
    
    print("=" * 80)
    print("测试回测API")
    print("=" * 80)
    
    # 1. 测试获取回测列表（空列表）
    print("\n1. 测试获取回测列表（空列表）")
    response = client.get('/api/backtest')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['success'] == True
    assert data['data']['total'] == 0
    print("✅ 测试通过")
    
    # 2. 添加一个测试回测记录
    print("\n2. 添加测试回测记录")
    db = StockDatabase()
    test_backtest = {
        'id': 'test-backtest-001',
        'strategy_id': 'volume_shrink',
        'strategy_name': '缩量三连跌（稳健版）',
        'config': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'initial_capital': 1000000
        },
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 1000000,
        'final_value': 1150000,
        'total_return': 0.15,
        'total_profit': 150000,
        'max_drawdown': -0.08,
        'total_trades': 50,
        'completed_trades': 48,
        'win_trades': 30,
        'loss_trades': 18,
        'win_rate': 0.625,
        'avg_profit': 3125,
        'avg_profit_rate': 0.0312,
        'max_profit': 15000,
        'max_loss': -8000,
        'avg_hold_days': 5.2,
        'daily_values': [
            {'date': '2024-01-01', 'total_value': 1000000},
            {'date': '2024-01-02', 'total_value': 1005000},
            {'date': '2024-01-03', 'total_value': 1010000}
        ],
        'trades': [
            {
                'date': '2024-01-02',
                'code': '000001.SZ',
                'action': 'buy',
                'price': 10.5,
                'shares': 1000,
                'amount': 10500
            },
            {
                'date': '2024-01-05',
                'code': '000001.SZ',
                'action': 'sell',
                'price': 11.2,
                'shares': 1000,
                'amount': 11200,
                'cost_price': 10.5,
                'profit': 700,
                'profit_rate': 0.0667,
                'hold_days': 3,
                'reason': '到期'
            }
        ],
        'status': 'completed',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat()
    }
    
    success = db.save_backtest_result(test_backtest)
    assert success == True
    print("✅ 测试回测记录已添加")
    
    # 3. 测试获取回测列表（有数据）
    print("\n3. 测试获取回测列表（有数据）")
    response = client.get('/api/backtest')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['success'] == True
    assert data['data']['total'] == 1
    assert len(data['data']['items']) == 1
    assert data['data']['items'][0]['id'] == 'test-backtest-001'
    print("✅ 测试通过")
    
    # 4. 测试获取回测详情
    print("\n4. 测试获取回测详情")
    response = client.get('/api/backtest/test-backtest-001')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['success'] == True
    assert data['data']['id'] == 'test-backtest-001'
    assert data['data']['total_return'] == 0.15
    assert len(data['data']['trades']) == 2
    print("✅ 测试通过")
    
    # 5. 测试获取不存在的回测
    print("\n5. 测试获取不存在的回测")
    response = client.get('/api/backtest/non-existent')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 404
    assert data['success'] == False
    print("✅ 测试通过")
    
    # 6. 测试分页
    print("\n6. 测试分页")
    response = client.get('/api/backtest?page=1&page_size=10')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['data']['page'] == 1
    assert data['data']['page_size'] == 10
    print("✅ 测试通过")
    
    # 7. 测试策略筛选
    print("\n7. 测试策略筛选")
    response = client.get('/api/backtest?strategy_id=volume_shrink')
    print(f"状态码: {response.status_code}")
    data = json.loads(response.data)
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert data['data']['total'] == 1
    print("✅ 测试通过")
    
    # 8. 测试导出CSV
    print("\n8. 测试导出CSV")
    response = client.get('/api/backtest/test-backtest-001/export')
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"CSV内容预览:\n{response.data.decode('utf-8-sig')[:200]}...")
    assert response.status_code == 200
    assert 'text/csv' in response.headers.get('Content-Type')
    print("✅ 测试通过")
    
    print("\n" + "=" * 80)
    print("所有测试通过！")
    print("=" * 80)


if __name__ == '__main__':
    test_backtest_api()
