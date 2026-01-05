"""
个股诊断系统测试脚本
"""

import sys
sys.path.insert(0, '.')

from src.data.database import StockDatabase
from src.business.diagnosis import StockDiagnosisEngine


def test_diagnosis():
    """测试诊断功能"""
    # 初始化数据库
    db = StockDatabase("data/stock_data.db")
    
    # 创建诊断引擎
    engine = StockDiagnosisEngine(data_fetcher=db)
    
    # 测试诊断
    test_codes = ['sh.600000', '600036', 'sz.000001']
    
    for code in test_codes:
        print(f"\n{'='*60}")
        print(f"诊断股票: {code}")
        print('='*60)
        
        try:
            report = engine.diagnose_stock(code)
            
            print(f"\n股票名称: {report.name}")
            print(f"股票代码: {report.code}")
            print(f"当前价格: {report.current_price:.2f} 元")
            print(f"涨跌幅: {report.change_pct:+.2f}%")
            print(f"\n综合评分: {report.overall_score:.1f}")
            print(f"  - 技术面评分: {report.technical_score.value:.1f}")
            print(f"  - 流动性评分: {report.liquidity_score.value:.1f}")
            print(f"  - 市场环境评分: {report.market_score.value:.1f}")
            
            print(f"\n信号灯: {report.signal_light.color} - {report.signal_light.label}")
            print(f"信号强度: {report.signal_light.confidence:.1f}")
            print(f"信号理由: {report.signal_light.reason}")
            
            print(f"\n风险管理:")
            print(f"  - 当前价格: {report.risk_info.current_price:.2f} 元")
            print(f"  - 止损价位: {report.risk_info.stop_loss_price:.2f} 元 ({report.risk_info.stop_loss_pct*100:.1f}%)")
            print(f"  - 止盈价位: {report.risk_info.take_profit_price:.2f} 元 ({report.risk_info.take_profit_pct*100:.1f}%)")
            print(f"  - 盈亏比: {report.risk_info.risk_reward_ratio:.2f}")
            print(f"  - 风险等级: {report.risk_info.risk_level}")
            
            if report.risk_info.warnings:
                print(f"\n风险警告:")
                for warning in report.risk_info.warnings:
                    print(f"  ⚠️  {warning}")
            
            print(f"\n诊断意见:")
            print(report.diagnosis_text)
            
        except Exception as e:
            print(f"❌ 诊断失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    test_diagnosis()
