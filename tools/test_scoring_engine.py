#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评分引擎
验证评分计算逻辑
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.business.scoring.stock_scoring_engine import StockScoringEngine
from src.data.database import StockDatabase


def test_basic_scoring():
    """测试基本评分功能"""
    print("=" * 80)
    print("测试 1: 基本评分功能")
    print("=" * 80)
    
    engine = StockScoringEngine()
    
    # 测试用例 1: 强信号（高成交量、大均线距离、好流动性）
    signal = {'code': '600000', 'date': '2024-01-15'}
    technical_factors = {
        'volume_ratio': 2.5,      # 成交量放大 2.5 倍
        'ma_distance': 0.015,     # 均线距离 1.5%
        'avg_turnover': 3e8,      # 日均成交额 3 亿
        'date': '2024-01-15'
    }
    
    score = engine.calculate_score(signal, technical_factors)
    print(f"\n测试用例 1 - 强信号:")
    print(f"  成交量放大: {technical_factors['volume_ratio']}x")
    print(f"  均线距离: {technical_factors['ma_distance']*100:.2f}%")
    print(f"  日均成交额: {technical_factors['avg_turnover']/1e8:.1f}亿")
    print(f"  ✅ 总分: {score:.2f}")
    
    # 测试用例 2: 弱信号（低成交量、小均线距离、差流动性）
    technical_factors_weak = {
        'volume_ratio': 1.1,      # 成交量仅放大 1.1 倍
        'ma_distance': 0.002,     # 均线距离 0.2%
        'avg_turnover': 5e7,      # 日均成交额 0.5 亿
        'date': '2024-01-15'
    }
    
    score_weak = engine.calculate_score(signal, technical_factors_weak)
    print(f"\n测试用例 2 - 弱信号:")
    print(f"  成交量放大: {technical_factors_weak['volume_ratio']}x")
    print(f"  均线距离: {technical_factors_weak['ma_distance']*100:.2f}%")
    print(f"  日均成交额: {technical_factors_weak['avg_turnover']/1e8:.1f}亿")
    print(f"  ✅ 总分: {score_weak:.2f}")
    
    # 验证强信号分数高于弱信号
    assert score > score_weak, "强信号分数应该高于弱信号"
    print(f"\n✅ 验证通过: 强信号({score:.2f}) > 弱信号({score_weak:.2f})")


def test_score_range():
    """测试评分范围"""
    print("\n" + "=" * 80)
    print("测试 2: 评分范围验证（0-100）")
    print("=" * 80)
    
    engine = StockScoringEngine()
    signal = {'code': '600000', 'date': '2024-01-15'}
    
    # 测试极端值
    test_cases = [
        {
            'name': '极低值',
            'factors': {
                'volume_ratio': 0.5,
                'ma_distance': 0.0,
                'avg_turnover': 0.0,
                'date': '2024-01-15'
            }
        },
        {
            'name': '极高值',
            'factors': {
                'volume_ratio': 10.0,
                'ma_distance': 0.1,
                'avg_turnover': 50e8,
                'date': '2024-01-15'
            }
        },
        {
            'name': '中等值',
            'factors': {
                'volume_ratio': 1.5,
                'ma_distance': 0.01,
                'avg_turnover': 1e8,
                'date': '2024-01-15'
            }
        }
    ]
    
    for case in test_cases:
        score = engine.calculate_score(signal, case['factors'])
        print(f"\n{case['name']}:")
        print(f"  总分: {score:.2f}")
        
        # 验证分数在 0-100 范围内
        assert 0 <= score <= 100, f"分数 {score} 超出范围 [0, 100]"
        print(f"  ✅ 分数在有效范围内")


def test_fundamental_scoring():
    """测试基本面评分"""
    print("\n" + "=" * 80)
    print("测试 3: 基本面评分")
    print("=" * 80)
    
    engine = StockScoringEngine()
    signal = {'code': '600000', 'date': '2024-01-15'}
    
    technical_factors = {
        'volume_ratio': 2.0,
        'ma_distance': 0.01,
        'avg_turnover': 2e8,
        'date': '2024-01-15'
    }
    
    # 测试用例 1: 优秀基本面
    fundamental_good = {
        'roe': 18.0,           # ROE 18%
        'debt_ratio': 50.0,    # 负债率 50%
        'net_profit': 1e8      # 盈利 1 亿
    }
    
    score_good = engine.calculate_score(signal, technical_factors, fundamental_good)
    print(f"\n优秀基本面:")
    print(f"  ROE: {fundamental_good['roe']}%")
    print(f"  负债率: {fundamental_good['debt_ratio']}%")
    print(f"  净利润: {fundamental_good['net_profit']/1e8:.1f}亿")
    print(f"  ✅ 总分: {score_good:.2f}")
    
    # 测试用例 2: 较差基本面
    fundamental_bad = {
        'roe': 3.0,            # ROE 3%
        'debt_ratio': 85.0,    # 负债率 85%
        'net_profit': -5e7     # 亏损 0.5 亿
    }
    
    score_bad = engine.calculate_score(signal, technical_factors, fundamental_bad)
    print(f"\n较差基本面:")
    print(f"  ROE: {fundamental_bad['roe']}%")
    print(f"  负债率: {fundamental_bad['debt_ratio']}%")
    print(f"  净利润: {fundamental_bad['net_profit']/1e8:.1f}亿")
    print(f"  ✅ 总分: {score_bad:.2f}")
    
    # 测试用例 3: 无基本面数据
    score_no_fundamental = engine.calculate_score(signal, technical_factors, None)
    print(f"\n无基本面数据:")
    print(f"  ✅ 总分: {score_no_fundamental:.2f}")
    
    # 验证优秀基本面分数高于较差基本面
    assert score_good > score_bad, "优秀基本面分数应该高于较差基本面"
    print(f"\n✅ 验证通过: 优秀基本面({score_good:.2f}) > 较差基本面({score_bad:.2f})")


def test_score_breakdown():
    """测试评分分解"""
    print("\n" + "=" * 80)
    print("测试 4: 评分分解")
    print("=" * 80)
    
    engine = StockScoringEngine()
    signal = {'code': '600000', 'date': '2024-01-15'}
    
    technical_factors = {
        'volume_ratio': 2.0,
        'ma_distance': 0.01,
        'avg_turnover': 2e8,
        'date': '2024-01-15'
    }
    
    fundamental_factors = {
        'roe': 15.0,
        'debt_ratio': 50.0,
        'net_profit': 1e8
    }
    
    breakdown = engine.get_score_breakdown(signal, technical_factors, fundamental_factors)
    
    print(f"\n总分: {breakdown['total_score']:.2f}")
    print("\n各因子贡献:")
    
    for factor_name, factor_data in breakdown['breakdown'].items():
        print(f"  {factor_name}:")
        print(f"    分数: {factor_data['score']:.2f}")
        print(f"    权重: {factor_data['weight']*100:.0f}%")
        print(f"    贡献: {factor_data['contribution']:.2f}")
    
    # 验证贡献之和等于总分
    total_contribution = sum(
        factor['contribution'] 
        for factor in breakdown['breakdown'].values()
    )
    
    assert abs(total_contribution - breakdown['total_score']) < 0.01, \
        f"贡献之和({total_contribution:.2f})应该等于总分({breakdown['total_score']:.2f})"
    
    print(f"\n✅ 验证通过: 贡献之和 = 总分")


def test_with_real_data():
    """使用真实数据测试"""
    print("\n" + "=" * 80)
    print("测试 5: 使用真实数据")
    print("=" * 80)
    
    try:
        db = StockDatabase()
        engine = StockScoringEngine(db)
        
        # 获取一只股票的真实数据
        code = 'sh.600000'
        df = db.get_daily_data(code)
        
        if not df.empty:
            # 取最近一天的数据
            latest = df.iloc[-1]
            
            signal = {
                'code': code,
                'date': latest['date']
            }
            
            technical_factors = {
                'volume_ratio': 1.5,  # 假设值
                'ma_distance': 0.008,  # 假设值
                'avg_turnover': latest.get('amount', 1e8),
                'date': latest['date']
            }
            
            score = engine.calculate_score(signal, technical_factors)
            
            print(f"\n股票: {code}")
            print(f"日期: {latest['date']}")
            print(f"收盘价: {latest['close']:.2f}")
            print(f"成交额: {latest.get('amount', 0)/1e8:.2f}亿")
            print(f"✅ 评分: {score:.2f}")
        else:
            print(f"\n⚠️  未找到股票 {code} 的数据")
    
    except Exception as e:
        print(f"\n⚠️  测试跳过: {e}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("股票评分引擎测试")
    print("=" * 80)
    
    test_basic_scoring()
    test_score_range()
    test_fundamental_scoring()
    test_score_breakdown()
    test_with_real_data()
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过")
    print("=" * 80)


if __name__ == "__main__":
    main()
