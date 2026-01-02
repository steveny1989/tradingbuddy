"""
诊断铜陵有色
"""

import sys
sys.path.insert(0, '.')

from src.data.database import StockDatabase
from src.business.diagnosis import StockDiagnosisEngine


def diagnose_tongling():
    """诊断铜陵有色"""
    # 初始化数据库
    db = StockDatabase("data/a_share.db")
    
    # 创建诊断引擎
    engine = StockDiagnosisEngine(data_fetcher=db)
    
    # 铜陵有色的股票代码
    code = '000630'  # 深圳市场
    
    print("="*80)
    print("🏥 TradingBuddy 个股诊断系统")
    print("="*80)
    print(f"\n正在诊断: {code} (铜陵有色)...\n")
    
    try:
        report = engine.diagnose_stock(code)
        
        # 基本信息
        print("📊 基本信息")
        print("-"*80)
        print(f"股票名称: {report.name}")
        print(f"股票代码: {report.code}")
        print(f"当前价格: {report.current_price:.2f} 元")
        print(f"涨跌幅: {report.change_pct:+.2f}%")
        
        # 综合评分
        print(f"\n⭐ 综合评分: {report.overall_score:.1f} 分")
        print("-"*80)
        print(f"  📈 技术面评分: {report.technical_score.value:.1f} 分")
        for reason in report.technical_score.reasons:
            print(f"     • {reason}")
        
        print(f"\n  💰 流动性评分: {report.liquidity_score.value:.1f} 分")
        for reason in report.liquidity_score.reasons:
            print(f"     • {reason}")
        
        print(f"\n  🌍 市场环境评分: {report.market_score.value:.1f} 分")
        for reason in report.market_score.reasons:
            print(f"     • {reason}")
        
        # 信号灯
        print(f"\n🚦 信号灯评价")
        print("-"*80)
        color_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}
        print(f"{color_emoji.get(report.signal_light.color, '⚪')} {report.signal_light.color} - {report.signal_light.label}")
        print(f"信号强度: {report.signal_light.confidence:.1f}")
        print(f"理由: {report.signal_light.reason}")
        
        # 风险管理
        print(f"\n⚠️  风险管理指南")
        print("-"*80)
        print(f"当前价格: {report.risk_info.current_price:.2f} 元")
        print(f"建议止损: {report.risk_info.stop_loss_price:.2f} 元 ({report.risk_info.stop_loss_pct*100:.1f}%)")
        print(f"建议止盈: {report.risk_info.take_profit_price:.2f} 元 ({report.risk_info.take_profit_pct*100:.1f}%)")
        print(f"盈亏比: {report.risk_info.risk_reward_ratio:.2f}:1")
        print(f"风险等级: {report.risk_info.risk_level}")
        print(f"波动率: {report.risk_info.volatility*100:.1f}%")
        
        if report.risk_info.warnings:
            print(f"\n⚠️  风险警告:")
            for warning in report.risk_info.warnings:
                print(f"  ⚠️  {warning}")
        
        # 诊断意见
        print(f"\n💬 诊断意见（大白话）")
        print("-"*80)
        print(report.diagnosis_text)
        
        # 免责声明
        print(f"\n📋 免责声明")
        print("-"*80)
        print(report.disclaimer)
        
        print(f"\n数据来源: {report.data_source}")
        print(f"数据覆盖: {report.data_coverage}")
        if report.data_update_time:
            print(f"数据更新时间: {report.data_update_time.strftime('%Y-%m-%d')}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    diagnose_tongling()
