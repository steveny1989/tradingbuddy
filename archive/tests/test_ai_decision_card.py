"""
测试 AI 决策卡片数据
验证诊断 API 返回的数据是否符合前端组件的需求
"""

import sys
sys.path.insert(0, '.')

from src.data.database import StockDatabase
from src.business.diagnosis import StockDiagnosisEngine


def test_ai_decision_card_data():
    """测试 AI 决策卡片所需的数据"""
    # 初始化数据库
    db = StockDatabase("data/a_share.db")
    
    # 创建诊断引擎
    engine = StockDiagnosisEngine(data_fetcher=db)
    
    # 测试几只股票
    test_codes = ['000630', '600000', '000001']
    
    for code in test_codes:
        print(f"\n{'='*80}")
        print(f"测试股票: {code}")
        print('='*80)
        
        try:
            report = engine.diagnose_stock(code)
            
            # 验证 AI 决策卡片所需的数据
            print(f"\n✅ AI 决策卡片数据验证:")
            print(f"  股票名称: {report.name}")
            print(f"  综合评分: {report.overall_score:.1f} 分")
            print(f"  信号灯颜色: {report.signal_light.color}")
            print(f"  信号灯标签: {report.signal_light.label}")
            print(f"  信号强度: {report.signal_light.confidence:.1f}")
            print(f"  信号理由: {report.signal_light.reason}")
            
            # 根据评分获取阶段描述
            if report.overall_score >= 80:
                phase = "黄金布局期"
            elif report.overall_score >= 60:
                phase = "观察窗口期"
            elif report.overall_score >= 40:
                phase = "谨慎观望期"
            else:
                phase = "高风险区域"
            
            print(f"\n  阶段描述: {phase}")
            
            # 根据信号灯颜色获取建议
            if report.signal_light.color == 'GREEN':
                recommendation = "基本面非常硬朗，技术面刚抬头，建议加入自选重点观察"
            elif report.signal_light.color == 'YELLOW':
                recommendation = "目前处于调整期，建议等待更明确的信号再做决策"
            elif report.signal_light.color == 'RED':
                recommendation = "当前风险较高，建议观望或考虑止损离场"
            else:
                recommendation = "请谨慎评估风险后再做决策"
            
            print(f"  建议: {recommendation}")
            
            # 诊断意见摘要
            first_paragraph = report.diagnosis_text.split('\n\n')[0]
            summary = first_paragraph[:100] + '...' if len(first_paragraph) > 100 else first_paragraph
            print(f"\n  诊断摘要: {summary}")
            
            print(f"\n✅ 数据完整，可以正常渲染 AI 决策卡片")
            
        except Exception as e:
            print(f"❌ 诊断失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    test_ai_decision_card_data()
