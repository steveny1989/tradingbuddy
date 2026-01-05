#!/usr/bin/env python3
"""
测试 Top 10 推荐功能
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_top_picks_api():
    """测试 Top 10 API"""
    print("=" * 60)
    print("测试 Top 10 推荐 API")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/diagnosis/top-picks", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success') and result.get('data'):
                picks = result['data']
                print(f"\n✅ 获取到 {len(picks)} 只推荐股票\n")
                
                for i, pick in enumerate(picks, 1):
                    print(f"{'🏆' if i <= 3 else '📈'} Top {i}:")
                    print(f"   股票名称: {pick.get('name', '')}")
                    print(f"   股票代码: {pick.get('code', '')}")
                    print(f"   信心分数: {pick.get('confidence_score', 0)} 分")
                    print(f"   策略: {pick.get('strategy_name', '')}")
                    print(f"   理由: {pick.get('reason', '')[:50]}...")
                    print()
                
                print("✅ API 测试通过！")
            else:
                print("⚠️  API 返回数据为空")
                print(f"   返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_top_picks_api()
