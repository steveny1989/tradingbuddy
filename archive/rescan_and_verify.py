#!/usr/bin/env python3
"""
重新扫描并验证股票名称显示修复
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def trigger_sync():
    """触发数据同步"""
    print_section("1. 触发数据同步")
    
    try:
        print("正在触发同步...")
        response = requests.post(f"{BASE_URL}/api/picker/sync", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 同步成功！")
            print(f"   返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 同步失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 同步失败: {str(e)}")
        return False

def check_daily_picks():
    """检查今日精选的股票名称"""
    print_section("2. 检查今日精选股票名称")
    
    try:
        print("正在获取今日精选...")
        response = requests.get(f"{BASE_URL}/api/picker/daily-picks?limit=5", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success') and result.get('data'):
                picks = result['data']
                print(f"✅ 获取到 {len(picks)} 只股票\n")
                
                all_correct = True
                for i, pick in enumerate(picks, 1):
                    code = pick.get('code', '')
                    name = pick.get('name', '')
                    
                    # 检查 name 是否包含 "sh." 或 "sz."
                    is_chinese = not ('sh.' in name.lower() or 'sz.' in name.lower())
                    status = "✅" if is_chinese else "❌"
                    
                    print(f"{status} 股票 {i}:")
                    print(f"   代码: {code}")
                    print(f"   名称: {name}")
                    print(f"   信心分数: {pick.get('confidence_score', 0)}")
                    print(f"   策略: {pick.get('strategy_name', '')}")
                    
                    if not is_chinese:
                        all_correct = False
                        print(f"   ⚠️  警告: 名称包含市场前缀，应该显示中文名称！")
                    print()
                
                if all_correct:
                    print("🎉 所有股票名称都正确显示为中文！")
                else:
                    print("⚠️  部分股票名称仍然显示为代码格式")
                
                return all_correct
            else:
                print("❌ 没有获取到精选股票")
                print(f"   返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return False
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def test_stock_detail():
    """测试股票详情页的名称显示"""
    print_section("3. 测试股票详情页")
    
    test_codes = ["sh.600519", "sz.000001", "sh.600000"]
    
    for code in test_codes:
        try:
            print(f"\n测试股票: {code}")
            response = requests.get(f"{BASE_URL}/api/picker/stocks/{code}", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success') and result.get('data'):
                    data = result['data']
                    name = data.get('name', '')
                    
                    is_chinese = not ('sh.' in name.lower() or 'sz.' in name.lower())
                    status = "✅" if is_chinese else "❌"
                    
                    print(f"{status} 代码: {code}")
                    print(f"   名称: {name}")
                    print(f"   价格: {data.get('price', 0)}")
                    
                    if not is_chinese:
                        print(f"   ⚠️  警告: 名称应该是中文！")
                else:
                    print(f"❌ 获取失败: {result}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")

def check_database():
    """检查数据库中的数据"""
    print_section("4. 检查数据库")
    
    try:
        import sqlite3
        import pandas as pd
        
        conn = sqlite3.connect('data/stock_data.db')
        
        # 测试新的 SQL 查询
        print("\n测试 JOIN 查询:")
        query = """
        SELECT 
            m.full_code, 
            m.code, 
            m.name as market_cap_name,
            s.name as stock_basic_name,
            COALESCE(s.name, m.name) as final_name
        FROM market_cap_data m
        LEFT JOIN stock_basic s ON m.code = s.code
        LIMIT 5
        """
        
        result = pd.read_sql(query, conn)
        print(result.to_string())
        
        # 检查是否有中文名称
        if not result.empty:
            has_chinese = result['final_name'].str.contains('[\u4e00-\u9fff]').any()
            if has_chinese:
                print("\n✅ 数据库中包含中文名称")
            else:
                print("\n⚠️  数据库中没有中文名称，可能需要检查 stock_basic 表")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {str(e)}")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 股票名称显示修复 - 重新扫描验证")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 步骤1: 触发同步
    sync_success = trigger_sync()
    
    if sync_success:
        print("\n⏳ 等待3秒让数据同步完成...")
        time.sleep(3)
    
    # 步骤2: 检查今日精选
    picks_correct = check_daily_picks()
    
    # 步骤3: 测试股票详情
    test_stock_detail()
    
    # 步骤4: 检查数据库
    check_database()
    
    # 总结
    print_section("总结")
    
    if picks_correct:
        print("✅ 修复成功！所有股票名称都正确显示为中文")
        print("\n下一步:")
        print("1. 访问前端: http://localhost:3000/picker")
        print("2. 查看今日精选和自选股列表")
        print("3. 确认显示为中文名称（如：贵州茅台、中金岭南）")
    else:
        print("⚠️  修复可能未完全生效")
        print("\n可能的原因:")
        print("1. 后端服务未重启")
        print("2. stock_basic 表中没有数据")
        print("3. market_cap_data 表中的 code 字段与 stock_basic 不匹配")
        print("\n建议:")
        print("1. 重启后端: ./start_backend.sh")
        print("2. 检查数据库表结构和数据")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
