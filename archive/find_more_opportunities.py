#!/usr/bin/env python3
"""
放宽条件，寻找更多投资机会

调整后的标准：
1. ROE > 8%（原来10%）
2. 跌幅 > 20%（原来30%）
3. PE < 40（原来30%）
4. 资产负债率 < 70%（原来60%）
"""

import sqlite3
from typing import List, Dict, Any

class FlexibleStockPicker:
    def __init__(self, db_path='data/a_share.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def step1_financial_health_filter(self, min_roe=8, max_debt=70) -> tuple:
        """财务健康筛选（放宽标准）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("=" * 80)
        print("第一步：财务健康筛选（放宽标准）")
        print("=" * 80)
        print(f"\n筛选标准：")
        print(f"  ✓ ROE > {min_roe}%（盈利能力）")
        print(f"  ✓ EPS > 0（有盈利）")
        print(f"  ✓ 资产负债率 < {max_debt}%（财务稳健）")
        print(f"  ✓ 流动比率 > 1.0（短期偿债能力）")
        print(f"  ✓ 毛利率 > 15%（产品竞争力）")
        print()
        
        cursor.execute(f"""
            SELECT 
                code,
                roe,
                eps,
                bvps,
                debt_to_asset_ratio,
                current_ratio,
                gross_margin,
                net_margin,
                report_date
            FROM financial_indicators
            WHERE 
                roe > {min_roe}
                AND eps > 0
                AND debt_to_asset_ratio < {max_debt}
                AND current_ratio > 1.0
                AND gross_margin > 15
                AND report_date >= '2024-01-01'
            ORDER BY report_date DESC, roe DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        code_dict = {}
        for row in results:
            code = row[0]
            if code not in code_dict:
                code_dict[code] = {
                    'code': code,
                    'roe': row[1],
                    'eps': row[2],
                    'bvps': row[3],
                    'debt_ratio': row[4],
                    'current_ratio': row[5],
                    'gross_margin': row[6],
                    'net_margin': row[7],
                    'report_date': row[8]
                }
        
        print(f"找到 {len(code_dict)} 只财务健康的股票")
        return list(code_dict.keys()), code_dict
    
    def step2_price_drop_filter(self, codes: List[str], min_drop_pct: float = 20) -> Dict[str, Dict]:
        """价格下跌筛选（放宽标准）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print(f"\n第二步：价格下跌筛选（跌幅 > {min_drop_pct}%）")
        print("=" * 80)
        
        fallen_stocks = {}
        checked = 0
        
        for code in codes:
            table_candidates = [
                f"daily_sh_{code}",
                f"daily_sz_{code}",
                f"daily_unknown_{code}"
            ]
            
            table_name = None
            for candidate in table_candidates:
                try:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name = ?
                    """, (candidate,))
                    
                    if cursor.fetchone():
                        table_name = candidate
                        break
                except:
                    continue
            
            if not table_name:
                continue
            
            checked += 1
            if checked % 500 == 0:
                print(f"  已检查 {checked}/{len(codes)} 只股票...")
            
            try:
                cursor.execute(f"""
                    SELECT 
                        close as current_price,
                        date as latest_date,
                        (SELECT MAX(high) FROM "{table_name}") as historical_high,
                        (SELECT date FROM "{table_name}" WHERE high = (SELECT MAX(high) FROM "{table_name}") LIMIT 1) as high_date
                    FROM "{table_name}"
                    ORDER BY date DESC
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                if not result or not result[2]:
                    continue
                
                current_price = result[0]
                latest_date = result[1]
                historical_high = result[2]
                high_date = result[3]
                
                drop_pct = ((current_price - historical_high) / historical_high) * 100
                
                if drop_pct < -min_drop_pct:
                    fallen_stocks[code] = {
                        'current_price': current_price,
                        'historical_high': historical_high,
                        'drop_pct': drop_pct,
                        'latest_date': latest_date,
                        'high_date': high_date
                    }
                    
            except Exception as e:
                continue
        
        conn.close()
        
        print(f"找到 {len(fallen_stocks)} 只价格大幅下跌的优质股票")
        return fallen_stocks
    
    def step3_valuation_filter(self, stocks: Dict[str, Dict], financial_data: Dict[str, Dict], max_pe=40, max_pb=5) -> Dict[str, Dict]:
        """估值筛选（放宽标准）"""
        print(f"\n第三步：估值筛选（PE < {max_pe}, PB < {max_pb}）")
        print("=" * 80)
        
        value_stocks = {}
        
        for code, price_data in stocks.items():
            if code not in financial_data:
                continue
            
            fin = financial_data[code]
            current_price = price_data['current_price']
            
            if fin['bvps'] and fin['bvps'] > 0:
                pb = current_price / fin['bvps']
            else:
                continue
            
            if fin['eps'] and fin['eps'] > 0:
                pe = current_price / fin['eps']
            else:
                continue
            
            if pb < max_pb and pe < max_pe and current_price < fin['bvps'] * 3:
                value_stocks[code] = {
                    **price_data,
                    'financial': fin,
                    'pb': pb,
                    'pe': pe
                }
        
        print(f"找到 {len(value_stocks)} 只具有估值安全边际的股票")
        return value_stocks
    
    def step4_technical_confirmation(self, stocks: Dict[str, Dict]) -> Dict[str, Dict]:
        """技术面确认"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("\n第四步：技术面确认")
        print("=" * 80)
        
        confirmed_stocks = {}
        
        for code, data in stocks.items():
            table_candidates = [
                f"daily_sh_{code}",
                f"daily_sz_{code}",
                f"daily_unknown_{code}"
            ]
            
            table_name = None
            for candidate in table_candidates:
                try:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name = ?
                    """, (candidate,))
                    
                    if cursor.fetchone():
                        table_name = candidate
                        break
                except:
                    continue
            
            if not table_name:
                continue
            
            try:
                cursor.execute(f"""
                    SELECT close, volume, date
                    FROM "{table_name}"
                    ORDER BY date DESC
                    LIMIT 20
                """)
                
                recent_data = cursor.fetchall()
                if len(recent_data) < 20:
                    continue
                
                ma20 = sum([row[0] for row in recent_data]) / 20
                current_price = recent_data[0][0]
                price_to_ma = (current_price - ma20) / ma20 * 100
                
                price_5d_ago = recent_data[4][0]
                return_5d = (current_price - price_5d_ago) / price_5d_ago * 100
                
                recent_vol = sum([row[1] for row in recent_data[:5]]) / 5
                prev_vol = sum([row[1] for row in recent_data[5:20]]) / 15
                vol_ratio = recent_vol / prev_vol if prev_vol > 0 else 0
                
                if price_to_ma > -15 and return_5d > -10:
                    confirmed_stocks[code] = {
                        **data,
                        'ma20': ma20,
                        'price_to_ma': price_to_ma,
                        'return_5d': return_5d,
                        'vol_ratio': vol_ratio
                    }
                    
            except Exception as e:
                continue
        
        conn.close()
        
        print(f"找到 {len(confirmed_stocks)} 只技术面确认的股票")
        return confirmed_stocks
    
    def get_stock_name(self, code: str) -> str:
        """Get stock name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT name FROM stock_basic 
                WHERE code = ? OR full_code = ?
            """, (code, code))
            result = cursor.fetchone()
            return result[0] if result else "未知"
        except:
            return "未知"
        finally:
            conn.close()
    
    def run(self, min_roe=8, max_debt=70, min_drop_pct=20, max_pe=40, max_pb=5):
        """运行完整筛选流程"""
        print("\n" + "=" * 80)
        print("放宽条件，寻找更多投资机会")
        print("=" * 80)
        print()
        
        # Step 1
        healthy_codes, financial_data = self.step1_financial_health_filter(min_roe, max_debt)
        
        if not healthy_codes:
            print("\n❌ 没有找到符合财务健康标准的股票")
            return []
        
        # Step 2
        fallen_stocks = self.step2_price_drop_filter(healthy_codes, min_drop_pct)
        
        if not fallen_stocks:
            print(f"\n❌ 没有找到价格下跌超过{min_drop_pct}%的优质股票")
            return []
        
        # Step 3
        value_stocks = self.step3_valuation_filter(fallen_stocks, financial_data, max_pe, max_pb)
        
        if not value_stocks:
            print("\n❌ 没有找到具有估值安全边际的股票")
            return []
        
        # Step 4
        final_stocks = self.step4_technical_confirmation(value_stocks)
        
        if not final_stocks:
            print("\n❌ 没有找到技术面确认的股票")
            return []
        
        # Display results
        print("\n" + "=" * 80)
        print(f"最终筛选结果（共 {len(final_stocks)} 只）")
        print("=" * 80)
        print()
        
        # Sort by score
        sorted_stocks = sorted(
            final_stocks.items(),
            key=lambda x: x[1]['financial']['roe'] * abs(x[1]['drop_pct']) / x[1]['pe'],
            reverse=True
        )
        
        results = []
        for i, (code, data) in enumerate(sorted_stocks[:20], 1):  # Show top 20
            name = self.get_stock_name(code)
            fin = data['financial']
            
            print(f"【{i}】{name} ({code})")
            print("-" * 60)
            print(f"现价: ¥{data['current_price']:.2f} | 跌幅: {data['drop_pct']:.1f}% | ROE: {fin['roe']:.1f}% | PE: {data['pe']:.1f}x")
            print(f"负债率: {fin['debt_ratio']:.1f}% | 毛利率: {fin['gross_margin']:.1f}% | 净利率: {fin['net_margin']:.1f}%")
            
            score = fin['roe'] * abs(data['drop_pct']) / data['pe']
            print(f"综合评分: {score:.1f}")
            print()
            
            results.append({
                'code': code,
                'name': name,
                'data': data
            })
        
        if len(sorted_stocks) > 20:
            print(f"... 还有 {len(sorted_stocks) - 20} 只股票未显示")
        
        print("\n" + "=" * 80)
        print(f"共找到 {len(results)} 只符合标准的股票（显示前20只）")
        print("=" * 80)
        
        return results


def main():
    picker = FlexibleStockPicker()
    
    print("\n" + "="*80)
    print("尝试多种参数组合，寻找更多机会")
    print("="*80)
    
    # 配置1：标准放宽
    print("\n\n【配置1】标准放宽：ROE>8%, 跌幅>20%, PE<40")
    print("="*80)
    results1 = picker.run(min_roe=8, max_debt=70, min_drop_pct=20, max_pe=40, max_pb=5)
    
    # 配置2：更激进
    print("\n\n【配置2】更激进：ROE>6%, 跌幅>15%, PE<50")
    print("="*80)
    results2 = picker.run(min_roe=6, max_debt=75, min_drop_pct=15, max_pe=50, max_pb=6)
    
    # 配置3：高ROE，大跌幅
    print("\n\n【配置3】高质量大跌：ROE>12%, 跌幅>25%, PE<35")
    print("="*80)
    results3 = picker.run(min_roe=12, max_debt=65, min_drop_pct=25, max_pe=35, max_pb=4)


if __name__ == "__main__":
    main()
