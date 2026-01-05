#!/usr/bin/env python3
"""
Analyze "Fallen Star" stocks - currently under 10 yuan but historically above 30 yuan
Step 1: Show all stocks meeting price criteria
Step 2: Analyze financial health of each stock
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any

def get_all_fallen_stars():
    """Find all stocks: current price < 10, historical high > 30"""
    conn = sqlite3.connect('data/a_share.db')
    cursor = conn.cursor()
    
    # Get all stock tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'daily_%'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Scanning {len(tables)} stock tables...")
    
    fallen_stars = []
    
    for table in tables:
        try:
            # Extract stock code from table name (daily_sh_600000 -> sh.600000)
            code_part = table.replace('daily_', '').replace('_', '.', 1)
            
            # Get latest price
            cursor.execute(f"""
                SELECT close, date 
                FROM "{table}"
                ORDER BY date DESC 
                LIMIT 1
            """)
            latest = cursor.fetchone()
            if not latest:
                continue
                
            current_price = latest[0]
            latest_date = latest[1]
            
            # Skip if current price >= 10
            if current_price >= 10:
                continue
            
            # Get historical high
            cursor.execute(f"""
                SELECT MAX(high) as max_high
                FROM "{table}"
            """)
            max_high = cursor.fetchone()[0]
            
            # Check if historical high > 30
            if max_high and max_high > 30:
                drop_pct = ((current_price - max_high) / max_high) * 100
                
                fallen_stars.append({
                    'code': code_part,
                    'current_price': current_price,
                    'historical_high': max_high,
                    'drop_pct': drop_pct,
                    'latest_date': latest_date
                })
                
        except Exception as e:
            continue
    
    conn.close()
    return fallen_stars

def get_stock_name(code: str) -> str:
    """Get stock name from code"""
    conn = sqlite3.connect('data/a_share.db')
    cursor = conn.cursor()
    
    try:
        # Try different formats
        code_variants = [
            code,
            code.split('.')[-1] if '.' in code else code,
        ]
        
        for variant in code_variants:
            cursor.execute("""
                SELECT name FROM stock_basic 
                WHERE code = ? OR full_code = ?
            """, (variant, code))
            result = cursor.fetchone()
            if result:
                return result[0]
        
        return "未知"
    except:
        return "未知"
    finally:
        conn.close()

def get_financial_data(code: str) -> Dict[str, Any]:
    """Get latest financial indicators for a stock"""
    conn = sqlite3.connect('data/a_share.db')
    cursor = conn.cursor()
    
    try:
        # Try different code formats
        code_variants = [
            code,
            code.split('.')[-1] if '.' in code else code,
            f"{code.split('.')[-1]}.{code.split('.')[0].upper()}" if '.' in code else code
        ]
        
        for variant in code_variants:
            cursor.execute("""
                SELECT 
                    report_date,
                    roe,
                    eps,
                    bvps,
                    current_ratio,
                    debt_to_asset_ratio,
                    gross_margin,
                    net_margin
                FROM financial_indicators
                WHERE code = ?
                ORDER BY report_date DESC
                LIMIT 1
            """, (variant,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'end_date': result[0],
                    'roe': result[1],
                    'eps': result[2],
                    'bvps': result[3],
                    'current_ratio': result[4],
                    'debt_to_assets': result[5],
                    'gross_margin': result[6],
                    'netprofit_margin': result[7]
                }
        
        return None
        
    except Exception as e:
        print(f"Error getting financial data for {code}: {e}")
        return None
    finally:
        conn.close()

def check_st_status(name: str) -> bool:
    """Check if stock is ST or delisted"""
    st_keywords = ['ST', '*ST', '退', 'S*ST', 'SST']
    return any(keyword in name for keyword in st_keywords)

def main():
    print("=" * 80)
    print("寻找'陨落之星'：现价<10元，历史最高>30元")
    print("=" * 80)
    print()
    
    # Step 1: Find all stocks meeting price criteria
    print("第一步：价格筛选")
    print("-" * 80)
    fallen_stars = get_all_fallen_stars()
    
    print(f"\n找到 {len(fallen_stars)} 只股票符合价格条件\n")
    
    # Add names and ST status
    for stock in fallen_stars:
        stock['name'] = get_stock_name(stock['code'])
        stock['is_st'] = check_st_status(stock['name'])
    
    # Sort by current price
    fallen_stars.sort(key=lambda x: x['current_price'])
    
    # Display all stocks
    print(f"{'代码':<15} {'名称':<12} {'现价':>8} {'历史最高':>10} {'跌幅':>8} {'状态':<6}")
    print("-" * 80)
    
    normal_stocks = []
    st_stocks = []
    
    for stock in fallen_stars:
        status = "ST/退市" if stock['is_st'] else "正常"
        print(f"{stock['code']:<15} {stock['name']:<12} "
              f"{stock['current_price']:>8.2f} {stock['historical_high']:>10.2f} "
              f"{stock['drop_pct']:>7.1f}% {status:<6}")
        
        if stock['is_st']:
            st_stocks.append(stock)
        else:
            normal_stocks.append(stock)
    
    print()
    print(f"统计：正常交易 {len(normal_stocks)} 只，ST/退市 {len(st_stocks)} 只")
    print()
    
    # Step 2: Analyze financial health of normal stocks
    if normal_stocks:
        print("\n" + "=" * 80)
        print("第二步：财务健康度分析（仅分析正常交易股票）")
        print("=" * 80)
        print()
        
        for i, stock in enumerate(normal_stocks, 1):
            print(f"\n【{i}】{stock['name']} ({stock['code']})")
            print("-" * 60)
            print(f"现价: ¥{stock['current_price']:.2f}")
            print(f"历史最高: ¥{stock['historical_high']:.2f}")
            print(f"跌幅: {stock['drop_pct']:.1f}%")
            print()
            
            # Get financial data
            financial = get_financial_data(stock['code'])
            
            if financial:
                print(f"财务数据（截至 {financial['end_date']}）：")
                print(f"  ROE (净资产收益率): {financial['roe']:.2f}%" if financial['roe'] else "  ROE: 无数据")
                print(f"  EPS (每股收益): ¥{financial['eps']:.2f}" if financial['eps'] else "  EPS: 无数据")
                print(f"  BVPS (每股净资产): ¥{financial['bvps']:.2f}" if financial['bvps'] else "  BVPS: 无数据")
                print(f"  流动比率: {financial['current_ratio']:.2f}" if financial['current_ratio'] else "  流动比率: 无数据")
                print(f"  资产负债率: {financial['debt_to_assets']:.2f}%" if financial['debt_to_assets'] else "  资产负债率: 无数据")
                print(f"  毛利率: {financial['gross_margin']:.2f}%" if financial['gross_margin'] else "  毛利率: 无数据")
                print(f"  净利率: {financial['netprofit_margin']:.2f}%" if financial['netprofit_margin'] else "  净利率: 无数据")
                
                # Investment assessment
                print()
                print("投资评估：")
                
                issues = []
                strengths = []
                
                # Check ROE
                if financial['roe']:
                    if financial['roe'] < 0:
                        issues.append(f"❌ ROE为负({financial['roe']:.1f}%)，公司亏损")
                    elif financial['roe'] < 5:
                        issues.append(f"⚠️  ROE过低({financial['roe']:.1f}%)，盈利能力弱")
                    elif financial['roe'] > 15:
                        strengths.append(f"✓ ROE良好({financial['roe']:.1f}%)")
                
                # Check EPS
                if financial['eps']:
                    if financial['eps'] < 0:
                        issues.append(f"❌ EPS为负(¥{financial['eps']:.2f})，每股亏损")
                    elif financial['eps'] > 0.5:
                        strengths.append(f"✓ EPS为正(¥{financial['eps']:.2f})")
                
                # Check debt
                if financial['debt_to_assets']:
                    if financial['debt_to_assets'] > 70:
                        issues.append(f"⚠️  资产负债率过高({financial['debt_to_assets']:.1f}%)")
                    elif financial['debt_to_assets'] < 50:
                        strengths.append(f"✓ 负债率健康({financial['debt_to_assets']:.1f}%)")
                
                # Check profitability
                if financial['netprofit_margin']:
                    if financial['netprofit_margin'] < 0:
                        issues.append(f"❌ 净利率为负({financial['netprofit_margin']:.1f}%)，经营亏损")
                    elif financial['netprofit_margin'] > 10:
                        strengths.append(f"✓ 净利率良好({financial['netprofit_margin']:.1f}%)")
                
                if strengths:
                    print("  优势：")
                    for s in strengths:
                        print(f"    {s}")
                
                if issues:
                    print("  问题：")
                    for issue in issues:
                        print(f"    {issue}")
                
                # Overall recommendation
                print()
                if len(issues) == 0 and len(strengths) >= 2:
                    print("  💡 综合评价：财务健康，值得关注")
                elif len(issues) >= 2:
                    print("  ⛔ 综合评价：财务状况较差，风险较高")
                else:
                    print("  ⚠️  综合评价：财务状况一般，需谨慎")
                    
            else:
                print("⚠️  无法获取财务数据")
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
