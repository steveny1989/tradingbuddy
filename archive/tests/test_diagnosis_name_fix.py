#!/usr/bin/env python3
"""
测试诊断 API 的股票名称显示
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_diagnosis_name():
    """测试诊断 API 返回的股票名称"""
    print("=" * 60)
    print("测试诊断 API 股票名称显示")
    print("=" * 60)
    
    test_codes = [
        ("sh.600519", "贵州茅台"),
        ("sz.000001", "平安银行"),
        ("sh.600000", "浦发银行"),
    ]
    
    for code, expected_name in test_codes:
        print(f"\n测试股票: {code}")
        print("-" * 60)
        
        try:
            response = requests.get(f"{BASE_URL}/api/diagnosis/{code}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                actual_name = data.get('name', '')
                actual_code = data.get('code', '')
                
                # 检查是否显示中文名称
                is_chinese = not ('sh.' in actual_name.lower() or 'sz.' in actual_name.lower())
                status = "✅" if is_chinese else "❌"
                
                print(f"{status} 返回的代码: {actual_code}")
                print(f"{status} 返回的名称: {actual_name}")
                
                if is_chinese:
                    print(f"   期望名称: {expected_name}")
                    if actual_name == expected_name:
                        print(f"   ✅ 名称完全匹配！")
                    else:
                        print(f"   ⚠️  名称不匹配，但至少是中文")
                else:
                    print(f"   ❌ 错误：名称应该是中文（{expected_name}），而不是代码！")
                
                # 显示其他信息
                print(f"   当前价格: {data.get('current_price', 0)}")
                print(f"   综合评分: {data.get('overall_score', 0)}")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_diagnosis_name()
