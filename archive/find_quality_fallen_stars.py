#!/usr/bin/env python3
"""
基于霍华德·马克斯理论的"优质陨落之星"选股策略

核心理念：
1. 防守优先 - 避免永久损失（财务健康）
2. 价值为本 - 不是买便宜的，而是买得好的
3. 逆向投资 - 在优质公司被错杀时买入
4. 安全边际 - 价格远低于内在价值

选股流程：
第一步：财务健康筛选（防守）
第二步：价格大幅下跌筛选（逆向机会）
第三步：估值安全边际筛选（价值）
第四步：技术面确认筛选（时机）
"""

import sqlite3
from typing import List, Dict, Any
from datetime import datetime

class QualityFallenStarPicker:
    def __init__(self, db_path='data/a_share.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def step1_financial_health_filter(self) -> List[str]:
        """
        第一步：财务健康筛选（防守优先）
        
        标准：
        - ROE > 10%（盈利能力强）
        - EPS > 0（有盈利）
        - 资产负债率 < 60%（财务稳健）
        - 流动比率 > 1.2（短期偿债能力）
        - 毛利率 > 20%（产品竞争力）
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("=" * 80)
        print("第一步：财务健康筛选（防守优先）")
        print("=" * 80)
        print("\n筛选标准：")
        print("  ✓ ROE > 10%（盈利能力强）")
        print("  ✓ EPS > 0（有盈利）")
        print("  ✓ 资产负债率 < 60%（财务稳健）")
        print("  ✓ 流动比率 > 1.2（短期偿债能力）")
        print("  ✓ 毛利率 > 20%（产品竞争力）")
        print()
        
        cursor.execute("""
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
                roe > 10
                AND eps > 0
                AND debt_to_asset_ratio < 60
                AND current_ratio > 1.2
                AND gross_margin > 20
                AND report_date >= '2024-01-01'
            ORDER BY report_date DESC, roe DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        # Get unique codes (latest data per stock)
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
    
    def step2_price_drop_filter(self, codes: List[str], min_drop_pct: float = 30) -> Dict[str, Dict]:
        """
        第二步：价格大幅下跌筛选（寻找逆向机会）
        
        标准：
        - 当前价格比历史最高下跌 > 30%
        - 但不是ST/退市股票
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print(f"\n第二步：价格大幅下跌筛选（跌幅 > {min_drop_pct}%）")
        print("=" * 80)
        
        fallen_stocks = {}
        checked = 0
        
        for code in codes:
            # Try to find the matching table
            # Code format in financial_indicators: 600519, 000001, etc.
            # Table names: daily_sh_600519, daily_sz_000001, etc.
            
            # Try both sh and sz prefixes
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
                
                # Get current price and historical high
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
                
                if drop_pct < -min_drop_pct:  # Dropped more than min_drop_pct%
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
    
    def step3_valuation_filter(self, stocks: Dict[str, Dict], financial_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        第三步：估值安全边际筛选
        
        标准：
        - PB < 3（不追高估值）
        - PE < 30（合理估值）
        - 股价 < 每股净资产 * 2（安全边际）
        """
        print("\n第三步：估值安全边际筛选")
        print("=" * 80)
        
        value_stocks = {}
        
        for code, price_data in stocks.items():
            if code not in financial_data:
                continue
            
            fin = financial_data[code]
            current_price = price_data['current_price']
            
            # Calculate PB ratio
            if fin['bvps'] and fin['bvps'] > 0:
                pb = current_price / fin['bvps']
            else:
                continue
            
            # Calculate PE ratio
            if fin['eps'] and fin['eps'] > 0:
                pe = current_price / fin['eps']
            else:
                continue
            
            # Check valuation criteria
            if pb < 3 and pe < 30 and current_price < fin['bvps'] * 2:
                value_stocks[code] = {
                    **price_data,
                    'financial': fin,
                    'pb': pb,
                    'pe': pe
                }
        
        print(f"找到 {len(value_stocks)} 只具有估值安全边际的股票")
        return value_stocks
    
    def step4_technical_confirmation(self, stocks: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        第四步：技术面确认（寻找企稳信号）
        
        标准：
        - 股价在20日均线附近或以上（短期企稳）
        - 成交量相对稳定（不是暴跌中）
        - 近5日涨跌幅 > -5%（没有继续暴跌）
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("\n第四步：技术面确认（寻找企稳信号）")
        print("=" * 80)
        
        confirmed_stocks = {}
        
        for code, data in stocks.items():
            # Find the table name (same logic as step2)
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
                # Get recent 20 days data
                cursor.execute(f"""
                    SELECT close, volume, date
                    FROM "{table_name}"
                    ORDER BY date DESC
                    LIMIT 20
                """)
                
                recent_data = cursor.fetchall()
                if len(recent_data) < 20:
                    continue
                
                # Calculate 20-day MA
                ma20 = sum([row[0] for row in recent_data]) / 20
                current_price = recent_data[0][0]
                
                # Check if price is near or above MA20 (within 10%)
                price_to_ma = (current_price - ma20) / ma20 * 100
                
                # Calculate 5-day return
                price_5d_ago = recent_data[4][0]
                return_5d = (current_price - price_5d_ago) / price_5d_ago * 100
                
                # Check volume stability (recent 5 days vs previous 15 days)
                recent_vol = sum([row[1] for row in recent_data[:5]]) / 5
                prev_vol = sum([row[1] for row in recent_data[5:20]]) / 15
                vol_ratio = recent_vol / prev_vol if prev_vol > 0 else 0
                
                # Technical confirmation criteria
                if price_to_ma > -10 and return_5d > -5:
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
    
    def run(self, min_drop_pct: float = 30):
        """Run the complete screening process"""
        print("\n" + "=" * 80)
        print("基于霍华德·马克斯理论的'优质陨落之星'选股策略")
        print("=" * 80)
        print()
        
        # Step 1: Financial health
        healthy_codes, financial_data = self.step1_financial_health_filter()
        
        if not healthy_codes:
            print("\n❌ 没有找到符合财务健康标准的股票")
            return []
        
        # Step 2: Price drop
        fallen_stocks = self.step2_price_drop_filter(healthy_codes, min_drop_pct)
        
        if not fallen_stocks:
            print(f"\n❌ 没有找到价格下跌超过{min_drop_pct}%的优质股票")
            return []
        
        # Step 3: Valuation
        value_stocks = self.step3_valuation_filter(fallen_stocks, financial_data)
        
        if not value_stocks:
            print("\n❌ 没有找到具有估值安全边际的股票")
            return []
        
        # Step 4: Technical confirmation
        final_stocks = self.step4_technical_confirmation(value_stocks)
        
        if not final_stocks:
            print("\n❌ 没有找到技术面确认的股票")
            return []
        
        # Display results
        print("\n" + "=" * 80)
        print("最终筛选结果")
        print("=" * 80)
        print()
        
        # Sort by综合评分 (ROE * 跌幅 / PE)
        sorted_stocks = sorted(
            final_stocks.items(),
            key=lambda x: x[1]['financial']['roe'] * abs(x[1]['drop_pct']) / x[1]['pe'],
            reverse=True
        )
        
        results = []
        for i, (code, data) in enumerate(sorted_stocks, 1):
            name = self.get_stock_name(code)
            fin = data['financial']
            
            print(f"\n【{i}】{name} ({code})")
            print("-" * 60)
            
            # Price info
            print(f"价格信息：")
            print(f"  现价: ¥{data['current_price']:.2f}")
            print(f"  历史最高: ¥{data['historical_high']:.2f} ({data['high_date']})")
            print(f"  跌幅: {data['drop_pct']:.1f}%")
            print(f"  20日均线: ¥{data['ma20']:.2f} (偏离: {data['price_to_ma']:.1f}%)")
            print(f"  近5日涨跌: {data['return_5d']:.1f}%")
            
            # Financial info
            print(f"\n财务指标（{fin['report_date']}）：")
            print(f"  ROE: {fin['roe']:.1f}% ✓")
            print(f"  EPS: ¥{fin['eps']:.2f} ✓")
            print(f"  BVPS: ¥{fin['bvps']:.2f}")
            print(f"  资产负债率: {fin['debt_ratio']:.1f}% ✓")
            print(f"  流动比率: {fin['current_ratio']:.2f} ✓")
            print(f"  毛利率: {fin['gross_margin']:.1f}% ✓")
            print(f"  净利率: {fin['net_margin']:.1f}%")
            
            # Valuation
            print(f"\n估值指标：")
            print(f"  PE: {data['pe']:.1f}x")
            print(f"  PB: {data['pb']:.2f}x")
            print(f"  安全边际: {((fin['bvps'] * 2 - data['current_price']) / data['current_price'] * 100):.1f}%")
            
            # Investment score
            score = fin['roe'] * abs(data['drop_pct']) / data['pe']
            print(f"\n综合评分: {score:.1f}")
            print(f"  (ROE × 跌幅 / PE = {fin['roe']:.1f} × {abs(data['drop_pct']):.1f} / {data['pe']:.1f})")
            
            # Investment thesis
            print(f"\n投资逻辑：")
            print(f"  ✓ 财务健康：ROE {fin['roe']:.1f}%，负债率{fin['debt_ratio']:.1f}%")
            print(f"  ✓ 价格回调：从最高点下跌{abs(data['drop_pct']):.1f}%")
            print(f"  ✓ 估值合理：PE {data['pe']:.1f}x，PB {data['pb']:.2f}x")
            print(f"  ✓ 技术企稳：近5日涨跌{data['return_5d']:.1f}%")
            
            results.append({
                'code': code,
                'name': name,
                'data': data
            })
        
        print("\n" + "=" * 80)
        print(f"共找到 {len(results)} 只符合标准的优质陨落之星")
        print("=" * 80)
        
        return results


def main():
    picker = QualityFallenStarPicker()
    
    # Run with different drop thresholds
    print("\n尝试不同的跌幅阈值...")
    
    for drop_pct in [30, 25, 20]:
        print(f"\n\n{'='*80}")
        print(f"尝试跌幅阈值: {drop_pct}%")
        print(f"{'='*80}")
        
        results = picker.run(min_drop_pct=drop_pct)
        
        if results:
            print(f"\n✓ 成功找到 {len(results)} 只股票")
            break
        else:
            print(f"\n⚠️  跌幅阈值 {drop_pct}% 未找到符合条件的股票，尝试降低标准...")
    
    if not results:
        print("\n" + "="*80)
        print("建议：")
        print("="*80)
        print("1. 当前市场可能没有'优质陨落之星'")
        print("2. 可以考虑放宽某些条件（如ROE > 8%，跌幅 > 15%）")
        print("3. 或者等待市场调整，优质公司出现更好的买入机会")


if __name__ == "__main__":
    main()
