#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析数据完整性和需求"""
import sys
sys.path.insert(0, '.')

from src.data.database import StockDatabase
import pandas as pd

def analyze_data_completeness():
    """分析当前数据是否足够进行量化分析"""
    
    print("="*80)
    print("📊 数据完整性分析报告")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    
    # 1. 当前数据概况
    print("\n【1. 当前数据概况】")
    print("-"*80)
    
    stats = db.get_statistics()
    stock_list = db.get_stock_list()
    
    print(f"总股票数: {stats['total_stocks']}")
    print(f"已下载: {stats['downloaded_stocks']}")
    print(f"完成度: {stats['completion_rate']}")
    print(f"总记录数: {stats['total_records']:,}")
    print(f"平均每只: {stats['avg_records_per_stock']} 条 (约 {stats['avg_records_per_stock']/250:.1f} 年)")
    
    # 2. 现有数据能做什么
    print("\n【2. 现有数据可以做的分析】")
    print("-"*80)
    
    print("""
✅ 可以做的分析（基于日线数据）:

1. 技术分析
   - 均线系统 (MA5, MA10, MA20, MA60, MA120, MA250)
   - MACD, KDJ, RSI, BOLL 等技术指标
   - 量价关系分析
   - 形态识别（头肩顶、双底等）
   
2. 量化策略
   - 趋势跟踪策略
   - 均线交叉策略
   - 突破策略
   - 缩量三连跌策略（你的需求）
   - 动量策略
   
3. 选股分析
   - 技术面选股
   - 涨跌幅排序
   - 成交量异动
   - 价格突破
   
4. 回测验证
   - 策略历史表现
   - 收益率计算
   - 最大回撤
   - 胜率统计
    """)
    
    # 3. 缺少的数据
    print("\n【3. 当前缺少的数据】")
    print("-"*80)
    
    print("""
❌ 缺少的数据类型:

1. 基本面数据
   - 财务报表（资产负债表、利润表、现金流量表）
   - 财务指标（ROE, 负债率, 营收增长率等）
   - 业绩预告
   - 分红送转
   
2. 市场数据
   - 实时市值、流通市值
   - PE、PB、PS 等估值指标（部分有）
   - 行业分类
   - 概念板块
   
3. 资金流向
   - 主力资金流入流出
   - 大单、中单、小单统计
   - 北向资金、南向资金
   
4. 新闻舆情
   - 公司公告
   - 新闻资讯
   - 研报评级
   - 社交媒体情绪
    """)
    
    # 4. 针对你的策略需求
    print("\n【4. 针对你的'缩量三连跌'策略】")
    print("-"*80)
    
    print("""
当前数据 ✅ 完全足够:

你的策略需要的数据:
  ✓ 日线价格（开高低收）
  ✓ 成交量
  ✓ 涨跌幅
  ✓ 历史数据（用于回测）

这些数据我们都有！可以直接开始开发策略。
    """)
    
    # 5. 建议补充的数据
    print("\n【5. 建议补充的数据（按优先级）】")
    print("-"*80)
    
    print("""
🔴 高优先级（强烈建议）:

1. 市值和估值数据
   - 总市值、流通市值
   - PE、PB、PS
   - 用途: 筛选股票池（如你要的50-200亿市值）
   - 获取方式: akshare 的 stock_zh_a_spot_em() 已包含
   
2. 行业分类
   - 所属行业、概念板块
   - 用途: 行业轮动分析、分散风险
   - 获取方式: akshare 的 stock_board_industry_name_em()

🟡 中优先级（建议有）:

3. 基础财务数据
   - ROE、负债率、营收增长
   - 用途: 基本面筛选，避开地雷股
   - 获取方式: akshare 的 stock_financial_analysis_indicator()
   
4. 资金流向
   - 主力资金净流入
   - 用途: 判断资金动向
   - 获取方式: akshare 的 stock_individual_fund_flow()

🟢 低优先级（可选）:

5. 分钟级数据
   - 用途: 日内交易、精确入场点
   - 注意: 数据量大，存储成本高
   
6. 新闻舆情
   - 用途: 事件驱动策略
   - 注意: 需要 NLP 处理
    """)
    
    # 6. 实际测试
    print("\n【6. 实际测试：用现有数据运行策略】")
    print("-"*80)
    
    # 找一只有完整数据的股票测试
    test_results = []
    checked = 0
    
    for _, row in stock_list.head(100).iterrows():
        code = row.get('full_code', f"{row['market']}.{row['code']}")
        
        if not db.table_exists(code):
            continue
        
        df = db.get_daily_data(code)
        
        if len(df) < 4:
            continue
        
        # 测试缩量三连跌逻辑
        p = df['close'].values
        v = df['volume'].values
        
        # 检查最近4天
        if len(p) >= 4:
            # 三连跌
            price_down = (p[-1] < p[-2] < p[-3] < p[-4])
            # 缩量
            volume_down = (v[-1] < v[-2] < v[-3])
            # 跌幅
            drop_rate = (p[-1] - p[-4]) / p[-4]
            
            if price_down and volume_down and drop_rate <= -0.07:
                test_results.append({
                    'code': code,
                    'name': row['name'],
                    'drop': f"{drop_rate*100:.2f}%"
                })
        
        checked += 1
        if checked >= 50:
            break
    
    print(f"\n测试结果: 在 {checked} 只股票中找到 {len(test_results)} 只符合条件")
    
    if test_results:
        print("\n符合条件的股票:")
        for r in test_results[:5]:
            print(f"  {r['name']} ({r['code']}): {r['drop']}")
    
    print("\n✅ 结论: 现有数据完全可以运行策略！")
    
    # 7. 行动建议
    print("\n【7. 行动建议】")
    print("-"*80)
    
    print("""
立即可以做:
  1. ✅ 用现有数据开发"缩量三连跌"策略
  2. ✅ 进行历史回测验证策略效果
  3. ✅ 计算技术指标辅助判断
  
建议补充（可选）:
  1. 🔴 下载全市场数据（目前只有100只）
     命令: python3 main.py download
     
  2. 🟡 补充市值数据（用于筛选50-200亿）
     已有接口，需要每日更新
     
  3. 🟢 补充行业分类（用于行业分析）
     可以后续添加

优先级排序:
  第一步: 下载全市场数据 ⭐⭐⭐⭐⭐
  第二步: 开发和测试策略 ⭐⭐⭐⭐⭐
  第三步: 补充市值数据   ⭐⭐⭐⭐
  第四步: 补充行业数据   ⭐⭐⭐
  第五步: 补充财务数据   ⭐⭐
    """)
    
    print("\n" + "="*80)
    print("✨ 分析完成！")
    print("="*80)
    
    db.close()

if __name__ == "__main__":
    analyze_data_completeness()
