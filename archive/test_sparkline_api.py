"""
测试 Sparkline API
"""
import requests
import json

# 测试股票列表API（应该包含 sparkline 数据）
response = requests.get('http://localhost:5001/api/stocks?page=1&page_size=5')

if response.status_code == 200:
    data = response.json()
    print("✅ API 调用成功")
    print(f"总股票数: {data['pagination']['total']}")
    print(f"返回股票数: {len(data['data'])}")
    
    if data['data']:
        first_stock = data['data'][0]
        print(f"\n第一只股票: {first_stock['code']} - {first_stock['name']}")
        
        if 'sparkline' in first_stock:
            sparkline = first_stock['sparkline']
            print(f"Sparkline 数据点数: {len(sparkline)}")
            if sparkline:
                print(f"价格范围: {min(sparkline):.2f} - {max(sparkline):.2f}")
                print(f"首尾价格: {sparkline[0]:.2f} -> {sparkline[-1]:.2f}")
                trend = ((sparkline[-1] - sparkline[0]) / sparkline[0]) * 100
                print(f"趋势: {trend:+.2f}%")
            else:
                print("⚠️  Sparkline 数据为空")
        else:
            print("❌ 没有 sparkline 字段")
else:
    print(f"❌ API 调用失败: {response.status_code}")
    print(response.text)
