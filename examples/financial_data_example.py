#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务数据使用示例
展示如何查询和分析财务数据
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import StockDatabase
import pandas as pd


def example_1_get_latest_financial_data():
    """示例1：获取最新财务数据"""
    print("\n" + "="*60)
    print("示例1：获取最新财务数据")
    print("="*60)
    
    db = StockDatabase()
    
    # 获取贵州茅台（600519）的最新财务数据
    code = '600519'
    data = db.get_latest_financial_data(code)
    
    print(f"\n{code} 最新财务数据：")
    
    if data['balance_sheet']:
        print("\n资产负债表（最新一期）：")
        bs = data['balance_sheet']
        print(f"  报告期: {bs.get('report_date')}")
        print(f"  总资产: {bs.get('total_assets', 0)/1e8:.2f} 亿元")
        print(f"  总负债: {bs.get('total_liabilities', 0)/1e8:.2f} 亿元")
        print(f"  股东权益: {bs.get('shareholders_equity', 0)/1e8:.2f} 亿元")
        print(f"  资产负债率: {bs.get('total_liabilities', 0)/bs.get('total_assets', 1)*100:.2f}%")
    
    if data['income_statement']:
        print("\n利润表（最新一期）：")
        is_ = data['income_statement']
        print(f"  报告期: {is_.get('report_date')}")
        print(f"  营业收入: {is_.get('total_revenue', 0)/1e8:.2f} 亿元")
        print(f"  净利润: {is_.get('net_profit', 0)/1e8:.2f} 亿元")
        print(f"  净利率: {is_.get('net_profit', 0)/is_.get('total_revenue', 1)*100:.2f}%")
        print(f"  每股收益: {is_.get('basic_eps', 0):.2f} 元")
    
    if data['cash_flow']:
        print("\n现金流量表（最新一期）：")
        cf = data['cash_flow']
        print(f"  报告期: {cf.get('report_date')}")
        print(f"  经营活动现金流: {cf.get('operating_cash_flow', 0)/1e8:.2f} 亿元")
        print(f"  投资活动现金流: {cf.get('investing_cash_flow', 0)/1e8:.2f} 亿元")
        print(f"  筹资活动现金流: {cf.get('financing_cash_flow', 0)/1e8:.2f} 亿元")
    
    if data['financial_indicators']:
        print("\n财务指标（最新一期）：")
        fi = data['financial_indicators']
        print(f"  报告期: {fi.get('report_date')}")
        print(f"  ROE: {fi.get('roe', 0):.2f}%")
        print(f"  ROA: {fi.get('roa', 0):.2f}%")
        print(f"  毛利率: {fi.get('gross_margin', 0):.2f}%")
        print(f"  流动比率: {fi.get('current_ratio', 0):.2f}")
        print(f"  速动比率: {fi.get('quick_ratio', 0):.2f}")
    
    db.close()


def example_2_analyze_profitability_trend():
    """示例2：分析盈利能力趋势"""
    print("\n" + "="*60)
    print("示例2：分析盈利能力趋势")
    print("="*60)
    
    db = StockDatabase()
    
    code = '600519'
    
    # 获取历史利润表数据
    income_df = db.get_income_statement(code)
    
    if not income_df.empty:
        print(f"\n{code} 近期盈利能力趋势：")
        print("\n报告期 | 营业收入(亿) | 净利润(亿) | 净利率(%) | 同比增长(%)")
        print("-" * 70)
        
        # 按报告期排序
        income_df = income_df.sort_values('report_date', ascending=False)
        
        for idx, row in income_df.head(8).iterrows():
            revenue = row.get('total_revenue', 0) / 1e8
            net_profit = row.get('net_profit', 0) / 1e8
            net_margin = (row.get('net_profit', 0) / row.get('total_revenue', 1)) * 100 if row.get('total_revenue', 0) > 0 else 0
            
            print(f"{row['report_date']} | {revenue:>11.2f} | {net_profit:>10.2f} | {net_margin:>9.2f} |")
    
    db.close()


def example_3_screen_high_roe_stocks():
    """示例3：筛选高ROE股票"""
    print("\n" + "="*60)
    print("示例3：筛选高ROE股票（ROE > 15%）")
    print("="*60)
    
    db = StockDatabase()
    
    # 查询所有股票的最新财务指标
    query = """
        SELECT 
            fi.code,
            sb.name,
            fi.report_date,
            fi.roe,
            fi.roa,
            fi.gross_margin,
            fi.debt_to_asset_ratio
        FROM financial_indicators fi
        JOIN stock_basic sb ON fi.code = sb.code
        WHERE fi.roe > 15
        AND fi.report_date = (
            SELECT MAX(report_date) 
            FROM financial_indicators 
            WHERE code = fi.code
        )
        ORDER BY fi.roe DESC
        LIMIT 20
    """
    
    try:
        df = pd.read_sql(query, db.conn)
        
        if not df.empty:
            print(f"\n找到 {len(df)} 只高ROE股票：")
            print("\n代码   | 名称     | 报告期     | ROE(%) | ROA(%) | 毛利率(%) | 资产负债率(%)")
            print("-" * 85)
            
            for idx, row in df.iterrows():
                print(f"{row['code']} | {row['name']:<8} | {row['report_date']} | "
                      f"{row['roe']:>6.2f} | {row['roa']:>6.2f} | "
                      f"{row['gross_margin']:>9.2f} | {row['debt_to_asset_ratio']:>13.2f}")
        else:
            print("\n暂无数据，请先下载财务数据")
    
    except Exception as e:
        print(f"\n查询失败: {e}")
        print("提示：请先使用 tools/fetch_financial_data.py 下载财务数据")
    
    db.close()


def example_4_analyze_cash_flow_quality():
    """示例4：分析现金流质量"""
    print("\n" + "="*60)
    print("示例4：分析现金流质量")
    print("="*60)
    
    db = StockDatabase()
    
    code = '600519'
    
    # 获取利润表和现金流量表
    income_df = db.get_income_statement(code)
    cash_flow_df = db.get_cash_flow(code)
    
    if not income_df.empty and not cash_flow_df.empty:
        print(f"\n{code} 现金流质量分析：")
        print("\n报告期 | 净利润(亿) | 经营现金流(亿) | 现金流/净利润")
        print("-" * 65)
        
        # 合并数据
        merged = pd.merge(
            income_df[['report_date', 'net_profit']],
            cash_flow_df[['report_date', 'operating_cash_flow']],
            on='report_date'
        )
        
        merged = merged.sort_values('report_date', ascending=False)
        
        for idx, row in merged.head(8).iterrows():
            net_profit = row['net_profit'] / 1e8
            ocf = row['operating_cash_flow'] / 1e8
            ratio = ocf / net_profit if net_profit != 0 else 0
            
            quality = "优秀" if ratio > 1.2 else "良好" if ratio > 0.8 else "一般"
            
            print(f"{row['report_date']} | {net_profit:>10.2f} | {ocf:>14.2f} | "
                  f"{ratio:>14.2f} ({quality})")
        
        print("\n说明：现金流/净利润 > 1.2 为优秀，> 0.8 为良好")
    
    db.close()


def example_5_calculate_financial_ratios():
    """示例5：计算财务比率"""
    print("\n" + "="*60)
    print("示例5：计算关键财务比率")
    print("="*60)
    
    db = StockDatabase()
    
    code = '600519'
    
    # 获取最新的资产负债表和利润表
    balance_sheet = db.get_balance_sheet(code)
    income_statement = db.get_income_statement(code)
    
    if not balance_sheet.empty and not income_statement.empty:
        bs = balance_sheet.iloc[0]
        is_ = income_statement.iloc[0]
        
        print(f"\n{code} 关键财务比率：")
        print(f"报告期: {bs['report_date']}")
        
        # 偿债能力
        print("\n【偿债能力】")
        current_ratio = bs.get('current_assets', 0) / bs.get('current_liabilities', 1)
        quick_ratio = (bs.get('current_assets', 0) - bs.get('inventory', 0)) / bs.get('current_liabilities', 1)
        debt_ratio = bs.get('total_liabilities', 0) / bs.get('total_assets', 1)
        
        print(f"  流动比率: {current_ratio:.2f}")
        print(f"  速动比率: {quick_ratio:.2f}")
        print(f"  资产负债率: {debt_ratio*100:.2f}%")
        
        # 盈利能力
        print("\n【盈利能力】")
        gross_margin = (is_.get('total_revenue', 0) - is_.get('operating_cost', 0)) / is_.get('total_revenue', 1)
        net_margin = is_.get('net_profit', 0) / is_.get('total_revenue', 1)
        roe = is_.get('net_profit', 0) / bs.get('shareholders_equity', 1)
        roa = is_.get('net_profit', 0) / bs.get('total_assets', 1)
        
        print(f"  毛利率: {gross_margin*100:.2f}%")
        print(f"  净利率: {net_margin*100:.2f}%")
        print(f"  ROE: {roe*100:.2f}%")
        print(f"  ROA: {roa*100:.2f}%")
        
        # 营运能力
        print("\n【营运能力】")
        asset_turnover = is_.get('total_revenue', 0) / bs.get('total_assets', 1)
        
        print(f"  总资产周转率: {asset_turnover:.2f}")
    
    db.close()


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("财务数据使用示例")
    print("="*60)
    
    # 运行示例
    example_1_get_latest_financial_data()
    example_2_analyze_profitability_trend()
    example_3_screen_high_roe_stocks()
    example_4_analyze_cash_flow_quality()
    example_5_calculate_financial_ratios()
    
    print("\n" + "="*60)
    print("所有示例运行完成！")
    print("="*60)


if __name__ == '__main__':
    main()
