"""
资金面分析模块
提供北向资金、主力资金流向分析
"""

import sqlite3
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CapitalAnalyzer:
    """资金面分析器"""
    
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = db_path
    
    def get_northbound_holding(self, code: str) -> Optional[Dict]:
        """
        获取北向资金持股情况
        
        Args:
            code: 股票代码 (如: 600519 或 sh.600519)
        
        Returns:
            {
                'hold_ratio': 6.56,
                'hold_value': 117865659.0,
                'change_ratio_5d': -0.14,
                'status': 'yellow',
                'message': '北向资金持股比例6.56%，持仓稳定'
            }
        """
        # 处理代码格式
        if '.' in code:
            code = code.split('.')[1]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT hold_ratio, hold_value, change_ratio_5d, date
        FROM northbound_capital
        WHERE code = ?
        ORDER BY date DESC
        LIMIT 1
        """
        
        cursor.execute(query, (code,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        hold_ratio, hold_value, change_ratio_5d, date = result
        
        # 判断状态
        if change_ratio_5d is None:
            status = 'yellow'
            message = f"北向资金持股比例{hold_ratio:.2f}%"
        elif change_ratio_5d > 0.5:
            status = 'green'
            message = f"北向资金持股比例{hold_ratio:.2f}%，近5日增持{change_ratio_5d:.2f}%，外资看好"
        elif change_ratio_5d < -0.5:
            status = 'red'
            message = f"北向资金持股比例{hold_ratio:.2f}%，近5日减持{abs(change_ratio_5d):.2f}%，外资减仓"
        else:
            status = 'yellow'
            message = f"北向资金持股比例{hold_ratio:.2f}%，持仓稳定"
        
        return {
            'hold_ratio': round(hold_ratio, 2) if hold_ratio else None,
            'hold_value': hold_value,
            'hold_value_billion': round(hold_value / 1e8, 2) if hold_value else None,
            'change_ratio_5d': round(change_ratio_5d, 2) if change_ratio_5d else None,
            'date': date,
            'status': status,
            'message': message
        }
    
    def get_capital_flow(self, code: str) -> Optional[Dict]:
        """
        获取主力资金流向
        
        Args:
            code: 股票代码
        
        Returns:
            {
                'main_net_inflow': -747402784.0,
                'main_net_inflow_ratio': -15.57,
                'super_large_inflow': -500000000.0,
                'large_inflow': -247402784.0,
                'status': 'red',
                'message': '主力资金大幅流出7.47亿元（占比-15.6%）'
            }
        """
        # 处理代码格式
        if '.' in code:
            code = code.split('.')[1]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            main_net_inflow, 
            main_net_inflow_ratio,
            super_large_inflow,
            large_inflow,
            medium_inflow,
            small_inflow,
            pct_chg,
            date
        FROM capital_flow
        WHERE code = ?
        ORDER BY date DESC
        LIMIT 1
        """
        
        cursor.execute(query, (code,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        (main_net_inflow, main_net_inflow_ratio, super_large_inflow, 
         large_inflow, medium_inflow, small_inflow, pct_chg, date) = result
        
        # 判断状态
        if main_net_inflow > 0 and main_net_inflow_ratio > 10:
            status = 'green'
            message = f"主力资金大幅流入{main_net_inflow/1e8:.2f}亿元（占比{main_net_inflow_ratio:.1f}%），有大资金在建仓"
        elif main_net_inflow > 0 and main_net_inflow_ratio > 5:
            status = 'green'
            message = f"主力资金流入{main_net_inflow/1e8:.2f}亿元（占比{main_net_inflow_ratio:.1f}%）"
        elif main_net_inflow < 0 and main_net_inflow_ratio < -10:
            status = 'red'
            message = f"主力资金大幅流出{abs(main_net_inflow)/1e8:.2f}亿元（占比{main_net_inflow_ratio:.1f}%），机构在出货"
        elif main_net_inflow < 0 and main_net_inflow_ratio < -5:
            status = 'red'
            message = f"主力资金流出{abs(main_net_inflow)/1e8:.2f}亿元（占比{main_net_inflow_ratio:.1f}%）"
        else:
            status = 'yellow'
            message = f"资金流向正常，主力净流入{main_net_inflow/1e8:.2f}亿元"
        
        return {
            'main_net_inflow': main_net_inflow,
            'main_net_inflow_billion': round(main_net_inflow / 1e8, 2) if main_net_inflow else None,
            'main_net_inflow_ratio': round(main_net_inflow_ratio, 2) if main_net_inflow_ratio else None,
            'super_large_inflow': super_large_inflow,
            'super_large_inflow_billion': round(super_large_inflow / 1e8, 2) if super_large_inflow else None,
            'large_inflow': large_inflow,
            'large_inflow_billion': round(large_inflow / 1e8, 2) if large_inflow else None,
            'medium_inflow': medium_inflow,
            'small_inflow': small_inflow,
            'pct_chg': round(pct_chg, 2) if pct_chg else None,
            'date': date,
            'status': status,
            'message': message
        }
    
    def get_capital_flow_ranking(self, order_by: str = 'inflow', top_n: int = 20) -> pd.DataFrame:
        """
        获取资金流向排名
        
        Args:
            order_by: 排序方式 ('inflow'=流入, 'outflow'=流出, 'ratio'=占比)
            top_n: 返回前N只股票
        
        Returns:
            DataFrame
        """
        conn = sqlite3.connect(self.db_path)
        
        if order_by == 'inflow':
            order_clause = "main_net_inflow DESC"
        elif order_by == 'outflow':
            order_clause = "main_net_inflow ASC"
        elif order_by == 'ratio':
            order_clause = "main_net_inflow_ratio DESC"
        else:
            order_clause = "main_net_inflow DESC"
        
        query = f"""
        SELECT 
            code,
            name,
            pct_chg,
            main_net_inflow / 1e8 as inflow_billion,
            main_net_inflow_ratio,
            super_large_inflow / 1e8 as super_large_billion,
            large_inflow / 1e8 as large_billion
        FROM capital_flow
        WHERE date = (SELECT MAX(date) FROM capital_flow)
        ORDER BY {order_clause}
        LIMIT ?
        """
        
        df = pd.read_sql(query, conn, params=(top_n,))
        conn.close()
        
        return df
    
    def get_northbound_ranking(self, order_by: str = 'hold_ratio', top_n: int = 20) -> pd.DataFrame:
        """
        获取北向资金持股排名
        
        Args:
            order_by: 排序方式 ('hold_ratio'=持股比例, 'hold_value'=持股市值, 'change'=变化)
            top_n: 返回前N只股票
        
        Returns:
            DataFrame
        """
        conn = sqlite3.connect(self.db_path)
        
        if order_by == 'hold_ratio':
            order_clause = "hold_ratio DESC"
        elif order_by == 'hold_value':
            order_clause = "hold_value DESC"
        elif order_by == 'change':
            order_clause = "change_ratio_5d DESC"
        else:
            order_clause = "hold_ratio DESC"
        
        query = f"""
        SELECT 
            code,
            hold_ratio,
            hold_value / 1e8 as hold_value_billion,
            change_ratio_5d,
            date
        FROM northbound_capital
        WHERE date = (SELECT MAX(date) FROM northbound_capital)
        ORDER BY {order_clause}
        LIMIT ?
        """
        
        df = pd.read_sql(query, conn, params=(top_n,))
        conn.close()
        
        # 添加股票名称
        if len(df) > 0:
            conn = sqlite3.connect(self.db_path)
            codes = "','".join(df['code'].tolist())
            name_query = f"SELECT code, name FROM industry_data WHERE code IN ('{codes}')"
            df_names = pd.read_sql(name_query, conn)
            conn.close()
            
            df = df.merge(df_names, on='code', how='left')
        
        return df
    
    def generate_capital_report(self, code: str) -> Dict:
        """
        生成完整的资金面分析报告
        
        Args:
            code: 股票代码
        
        Returns:
            完整的资金分析报告
        """
        # 1. 北向资金
        northbound = self.get_northbound_holding(code)
        
        # 2. 主力资金流向
        capital_flow = self.get_capital_flow(code)
        
        # 3. 综合判断
        status = 'yellow'
        message_parts = []
        
        # 北向资金判断
        if northbound:
            message_parts.append(northbound['message'])
            if northbound['status'] == 'green':
                status = 'green'
            elif northbound['status'] == 'red' and status != 'green':
                status = 'red'
        
        # 主力资金判断
        if capital_flow:
            message_parts.append(capital_flow['message'])
            if capital_flow['status'] == 'red':
                status = 'red'
            elif capital_flow['status'] == 'green' and status != 'red':
                status = 'green'
        
        # 如果都没有数据
        if not northbound and not capital_flow:
            return {
                'status': 'yellow',
                'message': '暂无资金面数据',
                'northbound': None,
                'capital_flow': None
            }
        
        return {
            'status': status,
            'message': '；'.join(message_parts),
            'northbound': northbound,
            'capital_flow': capital_flow
        }


if __name__ == "__main__":
    # 测试代码
    analyzer = CapitalAnalyzer()
    
    # 测试1: 北向资金
    print("=== 测试1: 北向资金持股 ===")
    result = analyzer.get_northbound_holding("600519")
    print(result)
    
    # 测试2: 主力资金流向
    print("\n=== 测试2: 主力资金流向 ===")
    result = analyzer.get_capital_flow("600519")
    print(result)
    
    # 测试3: 资金流入排名
    print("\n=== 测试3: 资金流入排名 ===")
    df = analyzer.get_capital_flow_ranking(order_by='inflow', top_n=10)
    print(df.to_string())
    
    # 测试4: 北向资金排名
    print("\n=== 测试4: 北向资金持股排名 ===")
    df = analyzer.get_northbound_ranking(order_by='hold_ratio', top_n=10)
    print(df.to_string())
    
    # 测试5: 完整报告
    print("\n=== 测试5: 完整资金分析报告 ===")
    result = analyzer.generate_capital_report("600519")
    print(result)
