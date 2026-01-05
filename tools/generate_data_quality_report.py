#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量报告生成工具

定期生成数据质量报告，包括：
- 数据完整性统计
- 异常数据汇总
- 停牌股票列表
- 数据更新时效性
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.layers import CleanedLayer, RawLayer
from datetime import datetime, timedelta
import json


class DataQualityReporter:
    """数据质量报告生成器"""
    
    def __init__(self):
        self.cleaned = CleanedLayer()
        self.raw = RawLayer()
    
    def generate_report(self, output_file: str = None):
        """生成完整的数据质量报告"""
        print('='*70)
        print('数据质量报告')
        print('='*70)
        print(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('='*70)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self._get_summary(),
            'data_completeness': self._check_completeness(),
            'data_quality': self._check_quality(),
            'suspended_stocks': self._get_suspended_stocks(),
            'anomalies': self._get_anomalies(),
            'recommendations': self._get_recommendations()
        }
        
        # 打印报告
        self._print_report(report)
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f'\n✅ 报告已保存到: {output_file}')
        
        return report
    
    def _get_summary(self):
        """获取数据概览"""
        stats = self.cleaned.get_stats()
        
        return {
            'total_stocks': stats['daily']['total_stocks'],
            'total_records': stats['daily']['total_records'],
            'valid_records': stats['daily']['valid_records'],
            'valid_rate': stats['daily']['valid_rate'],
            'suspended_records': stats['daily']['suspended_records']
        }
    
    def _check_completeness(self):
        """检查数据完整性"""
        import sqlite3
        
        completeness = {
            'stocks_with_data': 0,
            'stocks_without_recent_data': [],
            'date_gaps': []
        }
        
        # 检查最近是否有数据更新
        with sqlite3.connect(self.cleaned.daily_db) as conn:
            # 获取所有股票的最新日期
            cursor = conn.execute('''
                SELECT code, MAX(date) as last_date
                FROM daily_cleaned
                GROUP BY code
            ''')
            
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            for row in cursor.fetchall():
                code = row[0]
                last_date = datetime.strptime(row[1], '%Y-%m-%d').date()
                
                completeness['stocks_with_data'] += 1
                
                # 检查是否超过7天没有更新
                if last_date < week_ago:
                    completeness['stocks_without_recent_data'].append({
                        'code': code,
                        'last_date': row[1],
                        'days_ago': (today - last_date).days
                    })
        
        return completeness
    
    def _check_quality(self):
        """检查数据质量"""
        import sqlite3
        
        quality = {
            'invalid_records': 0,
            'error_types': {},
            'warning_types': {}
        }
        
        with sqlite3.connect(self.cleaned.daily_db) as conn:
            # 统计无效记录
            cursor = conn.execute('''
                SELECT COUNT(*) FROM daily_cleaned WHERE is_valid = 0
            ''')
            quality['invalid_records'] = cursor.fetchone()[0]
            
            # 统计错误类型
            cursor = conn.execute('''
                SELECT validation_errors, COUNT(*) as count
                FROM daily_cleaned
                WHERE validation_errors IS NOT NULL
                GROUP BY validation_errors
                ORDER BY count DESC
                LIMIT 10
            ''')
            
            for row in cursor.fetchall():
                if row[0]:
                    try:
                        errors = json.loads(row[0])
                        for error in errors:
                            quality['error_types'][error] = quality['error_types'].get(error, 0) + row[1]
                    except:
                        pass
        
        return quality
    
    def _get_suspended_stocks(self):
        """获取停牌股票列表"""
        import sqlite3
        
        suspended = []
        
        with sqlite3.connect(self.cleaned.daily_db) as conn:
            # 获取最近停牌的股票
            cursor = conn.execute('''
                SELECT code, date, close
                FROM daily_cleaned
                WHERE is_suspended = 1
                ORDER BY date DESC
                LIMIT 50
            ''')
            
            for row in cursor.fetchall():
                suspended.append({
                    'code': row[0],
                    'date': row[1],
                    'price': row[2]
                })
        
        return suspended
    
    def _get_anomalies(self):
        """获取异常数据"""
        import sqlite3
        
        anomalies = {
            'extreme_changes': [],
            'zero_volume': [],
            'price_anomalies': []
        }
        
        with sqlite3.connect(self.cleaned.daily_db) as conn:
            # 查找极端涨跌幅（需要计算）
            # 这里简化处理，只查找有验证错误的记录
            cursor = conn.execute('''
                SELECT code, date, close, validation_errors
                FROM daily_cleaned
                WHERE validation_errors IS NOT NULL
                ORDER BY date DESC
                LIMIT 20
            ''')
            
            for row in cursor.fetchall():
                if row[3]:
                    try:
                        errors = json.loads(row[3])
                        anomalies['price_anomalies'].append({
                            'code': row[0],
                            'date': row[1],
                            'close': row[2],
                            'errors': errors
                        })
                    except:
                        pass
        
        return anomalies
    
    def _get_recommendations(self):
        """生成改进建议"""
        stats = self.cleaned.get_stats()
        
        recommendations = []
        
        # 检查有效率
        if stats['daily']['valid_rate'] < 0.95:
            recommendations.append({
                'priority': 'HIGH',
                'issue': '数据有效率低于95%',
                'suggestion': '检查数据源质量，加强数据验证规则'
            })
        
        # 检查停牌记录
        if stats['daily']['suspended_records'] > 100:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'停牌记录较多（{stats["daily"]["suspended_records"]}条）',
                'suggestion': '定期清理历史停牌记录，或标记长期停牌股票'
            })
        
        # 如果没有问题
        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'issue': '数据质量良好',
                'suggestion': '继续保持当前的数据管理策略'
            })
        
        return recommendations
    
    def _print_report(self, report):
        """打印报告"""
        # 1. 数据概览
        print('\n【数据概览】')
        print(f"  总股票数: {report['summary']['total_stocks']:,}")
        print(f"  总记录数: {report['summary']['total_records']:,}")
        print(f"  有效记录: {report['summary']['valid_records']:,}")
        print(f"  有效率:   {report['summary']['valid_rate']*100:.2f}%")
        print(f"  停牌记录: {report['summary']['suspended_records']:,}")
        
        # 2. 数据完整性
        print('\n【数据完整性】')
        print(f"  有数据的股票: {report['data_completeness']['stocks_with_data']:,}")
        
        outdated = report['data_completeness']['stocks_without_recent_data']
        if outdated:
            print(f"  ⚠️  超过7天未更新: {len(outdated)} 只股票")
            if len(outdated) <= 5:
                for stock in outdated:
                    print(f"     - {stock['code']}: 最后更新 {stock['last_date']} ({stock['days_ago']}天前)")
        else:
            print(f"  ✅ 所有股票数据都是最新的")
        
        # 3. 数据质量
        print('\n【数据质量】')
        print(f"  无效记录: {report['data_quality']['invalid_records']:,}")
        
        if report['data_quality']['error_types']:
            print(f"  错误类型分布:")
            for error_type, count in list(report['data_quality']['error_types'].items())[:5]:
                print(f"     - {error_type}: {count} 次")
        
        # 4. 停牌股票
        print('\n【停牌股票】')
        suspended = report['suspended_stocks']
        if suspended:
            print(f"  最近停牌: {len(suspended)} 只股票")
            for stock in suspended[:5]:
                print(f"     - {stock['code']}: {stock['date']} (价格: {stock['price']:.2f})")
            if len(suspended) > 5:
                print(f"     ... 还有 {len(suspended)-5} 只")
        else:
            print(f"  ✅ 没有停牌股票")
        
        # 5. 异常数据
        print('\n【异常数据】')
        anomalies = report['anomalies']['price_anomalies']
        if anomalies:
            print(f"  价格异常: {len(anomalies)} 条记录")
            for anomaly in anomalies[:3]:
                print(f"     - {anomaly['code']} ({anomaly['date']}): {anomaly['errors']}")
        else:
            print(f"  ✅ 没有发现异常数据")
        
        # 6. 改进建议
        print('\n【改进建议】')
        for rec in report['recommendations']:
            priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': 'ℹ️'}
            icon = priority_icon.get(rec['priority'], '•')
            print(f"  {icon} [{rec['priority']}] {rec['issue']}")
            print(f"     建议: {rec['suggestion']}")
        
        print('\n' + '='*70)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据质量报告生成工具')
    parser.add_argument('--output', '-o', help='输出文件路径（JSON格式）')
    
    args = parser.parse_args()
    
    reporter = DataQualityReporter()
    reporter.generate_report(output_file=args.output)


if __name__ == "__main__":
    main()
