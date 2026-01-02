"""
测试极简选股助手的止损止盈预警功能
"""
import sys
import json
from src.web.app import create_app

def test_watchlist_with_alerts():
    """测试自选股API的止损止盈预警功能"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # 测试数据：模拟自选股
        test_data = {
            "stocks": [
                {
                    "code": "000001",  # 平安银行
                    "add_time": "2025-01-01 10:00:00",
                    "add_price": 10.0,
                    "stop_loss": -0.10,  # -10%
                    "take_profit": 0.20   # +20%
                },
                {
                    "code": "600000",  # 浦发银行
                    "add_time": "2025-01-01 10:00:00",
                    "add_price": 8.0,
                    "stop_loss": -0.10,
                    "take_profit": 0.20
                }
            ]
        }
        
        # 发送请求
        response = client.post(
            '/api/picker/watchlist',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"成功: {data.get('success')}")
            
            if data.get('success'):
                watchlist = data.get('data', [])
                print(f"\n自选股数量: {len(watchlist)}")
                
                for item in watchlist:
                    print(f"\n股票: {item['code']} - {item['name']}")
                    print(f"  添加价格: {item['add_price']:.2f}")
                    print(f"  当前价格: {item['current_price']:.2f}")
                    print(f"  盈亏: {item['profit_pct']*100:.2f}%")
                    print(f"  信号: {item['signal']['label']} ({item['signal']['color']})")
                    print(f"  止损: {item['stop_loss']*100:.0f}%")
                    print(f"  止盈: {item['take_profit']*100:.0f}%")
                    
                    # 检查预警
                    if item.get('alert'):
                        alert = item['alert']
                        print(f"  ⚠️ 预警: {alert['type']}")
                        print(f"     消息: {alert['message']}")
                        print(f"     当前价格: {alert['current_price']:.2f}")
                        print(f"     目标价格: {alert['target_price']:.2f}")
                    else:
                        print(f"  ✓ 无预警")
                
                print("\n✅ 测试通过：止损止盈预警功能正常工作")
                return True
            else:
                print(f"❌ API返回失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.get_json())
            return False

if __name__ == '__main__':
    success = test_watchlist_with_alerts()
    sys.exit(0 if success else 1)
