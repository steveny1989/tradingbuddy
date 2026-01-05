#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于现有数据的选股程序
使用技术面 + 基本面（ROE）筛选
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.database import StockDatabase
import pandas as pd
import numpy as np

def find_stocks():
    """基于现有数据找股票"""
    
    print("=" * 80)
    print("🔍 智能选股 - 基于技术面 + 基本面")
    print("=" * 80)
    print()
    
    db = StockDatabase("data/a_share.db")
    
    # 1. 获取有ROE数据的优质股票
    print("【步骤1】筛选基本面优质股票（ROE > 10%）")
    print("-" * 80)
    
    query = '''
    SELECT DISTINCT f.code, s.name, f.roe, f.report_date
    FROM financial_indicators f
    LEFT JOIN stock_basic s ON f.code = s.code
    WHERE f.report_date >= '2024-01-01'
      AND f.roe > 10
      AND f.roe < 100
      AND f.roe IS NOT NULL
      AND s.name NOT LIKE '%ST%'
    ORDER BY f.roe DESC
    '''
    
    quality_stocks = pd.read_sql(query, db.conn)
    print(f"找到 {len(quality_stocks)} 只基本面优质股票")
    print()
    
    if quality_stocks.empty:
        print("未找到符合条件的股票")
        return
    
    # 2. 获取这些股票的市值信息
    print("【步骤2】筛选市值范围（50-500亿）")
    print("-" * 80)
    
    codes = quality_stocks['code'].unique().tolist()
    codes_str = ','.join([f"'{c}'" for c in codes])
    
    query = f'''
    SELECT m.code, m.full_code, COALESCE(s.name, m.name) as name, m.total_cap
    FROM market_cap_data m
    LEFT JOIN stock_basic s ON m.code = s.code
    WHERE m.code IN ({codes_str})
      AND m.total_cap >= 50e8
      AND m.total_cap <= 500e8
    '''
    
    cap_filtered = pd.read_sql(query, db.conn)
    print(f"市值筛选后: {len(cap_filtered)} 只股票")
    print()
    
    if cap_filtered.empty:
        print("未找到符合市值条件的股票")
        return
    
    # 3. 技术面分析
    print("【步骤3】技术面分析")
    print("-" * 80)
    
    results = []
    for idx, row in cap_filtered.iterrows():
        code = row['full_code']
        name = row['name']
        
        # 获取最近60天数据
        df = db.get_daily_data(code)
        if df.empty or len(df) < 60:
            continue
        
        df = df.sort_values('date').tail(60)
        
        # 计算技术指标
        latest = df.iloc[-1]
        price = latest['close']
        
        # 20日均线
        ma20 = df['close'].tail(20).mean()
        
        # 60日均线
        ma60 = df['close'].tail(60).mean()
        
        # 最近5天涨跌幅
        if len(df) >= 5:
            price_5d_ago = df.iloc[-5]['close']
            change_5d = (price - price_5d_ago) / price_5d_ago * 100
        else:
            change_5d = 0
        
        # 最近20天涨跌幅
        if len(df) >= 20:
            price_20d_ago = df.iloc[-20]['close']
            change_20d = (price - price_20d_ago) / price_20d_ago * 100
        else:
            change_20d = 0
        
        # 判断趋势
        if price > ma20 > ma60:
            trend = '上升'
            trend_score = 3
        elif price < ma20 < ma60:
            trend = '下降'
            trend_score = 1
        else:
            trend = '震荡'
            trend_score = 2
        
        # 获取ROE
        roe_data = quality_stocks[quality_stocks['code'] == row['code']]
        if not roe_data.empty:
            roe = roe_data.iloc[0]['roe']
        else:
            roe = 0
        
        # 综合评分
        score = 0
        
        # ROE评分（0-40分）
        if roe > 20:
            score += 40
        elif roe > 15:
            score += 30
        elif roe > 10:
            score += 20
        
        # 趋势评分（0-30分）
        score += trend_score * 10
        
        # 涨跌幅评分（0-30分）
        if -10 < change_20d < -5:  # 适度回调
            score += 30
        elif -5 <= change_20d < 0:  # 小幅回调
            score += 20
        elif 0 <= change_20d < 10:  # 温和上涨
            score += 25
        elif change_20d >= 10:  # 强势上涨
            score += 15
        
        results.append({
            'code': code,
            'name': name,
            'price': price,
            'market_cap': row['total_cap'] / 1e8,
            'roe': roe,
            'change_5d': change_5d,
            'change_20d': change_20d,
            'trend': trend,
            'ma20': ma20,
            'ma60': ma60,
            'score': score
        })
    
    # 转换为DataFrame并排序
    df_results = pd.DataFrame(results)
    
    if df_results.empty:
        print("未找到符合条件的股票")
        return
    
    df_results = df_results.sort_values('score', ascending=False)
    
    print(f"完成技术面分析: {len(df_results)} 只股票")
    print()
    
    # 4. 显示结果
    print("=" * 80)
    print("📊 选股结果（按综合评分排序）")
    print("=" * 80)
    print()
    
    print("【TOP 10 推荐股票】")
    print("-" * 80)
    
    for idx, row in df_results.head(10).iterrows():
        print(f"\n{idx+1}. {row['name']} ({row['code']})")
        print(f"   综合评分: {row['score']:.0f}/100")
        print(f"   价格: ¥{row['price']:.2f}, 市值: {row['market_cap']:.1f}亿")
        print(f"   ROE: {row['roe']:.1f}%")
        print(f"   涨跌幅: 5日={row['change_5d']:.1f}%, 20日={row['change_20d']:.1f}%")
        print(f"   趋势: {row['trend']}")
        
        # 投资建议
        if row['score'] >= 80:
            print(f"   💎 强烈推荐：基本面优秀，技术面强势")
        elif row['score'] >= 70:
            print(f"   ⭐ 推荐：基本面良好，技术面稳健")
        elif row['score'] >= 60:
            print(f"   ✅ 关注：基本面不错，等待更好时机")
        else:
            print(f"   ⚠️  观望：需要进一步观察")
    
    print()
    print("=" * 80)
    print("📈 分类推荐")
    print("=" * 80)
    print()
    
    # 高ROE股票
    high_roe = df_results[df_results['roe'] > 20].head(5)
    if not high_roe.empty:
        print("【高ROE股票】（ROE > 20%，盈利能力强）")
        for idx, row in high_roe.iterrows():
            print(f"  • {row['name']} ({row['code']}): ROE={row['roe']:.1f}%, 评分={row['score']:.0f}")
        print()
    
    # 上升趋势股票
    uptrend = df_results[df_results['trend'] == '上升'].head(5)
    if not uptrend.empty:
        print("【上升趋势股票】（技术面强势）")
        for idx, row in uptrend.iterrows():
            print(f"  • {row['name']} ({row['code']}): 20日涨幅={row['change_20d']:.1f}%, 评分={row['score']:.0f}")
        print()
    
    # 回调机会股票
    pullback = df_results[(df_results['change_20d'] < 0) & (df_results['change_20d'] > -10)].head(5)
    if not pullback.empty:
        print("【回调机会股票】（基本面好，技术面回调）")
        for idx, row in pullback.iterrows():
            print(f"  • {row['name']} ({row['code']}): 20日跌幅={row['change_20d']:.1f}%, ROE={row['roe']:.1f}%")
        print()
    
    print("=" * 80)
    print("💡 投资建议")
    print("=" * 80)
    print()
    print("1. 高评分股票（≥80分）：基本面和技术面都很好，可以重点关注")
    print("2. 上升趋势股票：顺势而为，但注意不要追高")
    print("3. 回调机会股票：基本面好但短期回调，可以等待企稳后买入")
    print("4. 风险控制：单只股票不超过总资金的10%，设置止损-8%")
    print()
    
    # 保存结果
    df_results.to_csv('stock_picks.csv', index=False, encoding='utf-8-sig')
    print("✅ 结果已保存到 stock_picks.csv")
    print()

if __name__ == '__main__':
    try:
        find_stocks()
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
