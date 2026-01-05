#!/usr/bin/env python3
"""
测试 Top 10 推荐与个股诊断的评分一致性
"""
import requests
import json

def test_score_consistency():
    """测试评分一致性"""
    print("=" * 60)
    print("测试 Top 10 推荐与个股诊断的评分一致性")
    print("=" * 60)
    
    # 1. 获取 Top 10 推荐
    print("\n1. 获取 Top 10 推荐...")
    response = requests.get('http://localhost:5001/api/diagnosis/top-picks')
    top_picks = response.json()
    
    if not top_picks.get('success'):
        print("❌ 获取 Top 10 失败")
        return False
    
    picks = top_picks['data']
    print(f"✓ 获取到 {len(picks)} 只推荐股票")
    
    # 2. 逐一验证每只股票的评分
    print("\n2. 验证每只股票的评分一致性...")
    all_consistent = True
    
    for i, pick in enumerate(picks[:5], 1):  # 只测试前5只
        code = pick['code']
        top_picks_score = pick['overall_score']
        
        # 获取个股诊断评分
        response = requests.get(f'http://localhost:5001/api/diagnosis/{code}')
        diagnosis = response.json()
        diagnosis_score = diagnosis['overall_score']
        
        # 比较评分（允许 0.1 的误差）
        is_consistent = abs(top_picks_score - diagnosis_score) < 0.1
        
        status = "✓" if is_consistent else "❌"
        print(f"{status} {i}. {pick['name']} ({code})")
        print(f"   Top 10 评分: {top_picks_score:.1f}")
        print(f"   个股诊断评分: {diagnosis_score:.1f}")
        
        if not is_consistent:
            all_consistent = False
            print(f"   ⚠️  评分不一致！差异: {abs(top_picks_score - diagnosis_score):.1f}")
    
    # 3. 总结
    print("\n" + "=" * 60)
    if all_consistent:
        print("✓ 所有股票的评分都一致！")
        print("✓ Top 10 推荐使用的是诊断引擎的真实评分")
        return True
    else:
        print("❌ 发现评分不一致的股票")
        return False

if __name__ == '__main__':
    try:
        success = test_score_consistency()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
