"""
测试个股诊断 API
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_search():
    """测试搜索功能"""
    print("="*80)
    print("测试搜索功能")
    print("="*80)
    
    # 测试搜索
    response = requests.get(f"{BASE_URL}/api/diagnosis/search?q=中金")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"搜索结果: {len(data['stocks'])} 只股票")
        for stock in data['stocks'][:5]:
            print(f"  - {stock['code']}: {stock['name']}")
    else:
        print(f"错误: {response.text}")
    print()

def test_diagnosis(code):
    """测试诊断功能"""
    print("="*80)
    print(f"测试诊断功能: {code}")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/diagnosis/{code}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n股票名称: {data['name']}")
        print(f"股票代码: {data['code']}")
        print(f"当前价格: {data['current_price']:.2f} 元")
        print(f"涨跌幅: {data['change_pct']:+.2f}%")
        print(f"\n综合评分: {data['overall_score']:.1f} 分")
        print(f"  技术面: {data['technical_score']['value']:.1f} 分")
        print(f"  流动性: {data['liquidity_score']['value']:.1f} 分")
        print(f"  市场环境: {data['market_score']['value']:.1f} 分")
        print(f"\n信号灯: {data['signal_light']['color']} - {data['signal_light']['label']}")
        print(f"风险等级: {data['risk_info']['risk_level']}")
        print(f"\n诊断意见:")
        print(data['diagnosis_text'][:200] + "...")
    else:
        print(f"错误: {response.text}")
    print()

if __name__ == '__main__':
    # 测试搜索
    test_search()
    
    # 测试诊断
    test_diagnosis('000060')  # 中金岭南
    test_diagnosis('000630')  # 铜陵有色
