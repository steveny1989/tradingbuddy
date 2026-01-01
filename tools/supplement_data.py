#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充市值和行业数据"""
import akshare as ak
import pandas as pd
from src.data.database import StockDatabase
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def supplement_market_cap_data(db):
    """补充市值数据"""
    logger.info("="*80)
    logger.info("📊 开始补充市值数据...")
    logger.info("="*80)
    
    try:
        # 获取实时行情（包含市值）
        logger.info("正在从 akshare 获取数据...")
        df = ak.stock_zh_a_spot_em()
        
        logger.info(f"✅ 获取成功: {len(df)} 只股票")
        
        # 提取需要的字段
        market_data = pd.DataFrame({
            'code': df['代码'],
            'name': df['名称'],
            'price': df['最新价'],
            'total_cap': df['总市值'],      # 单位：元
            'float_cap': df['流通市值'],     # 单位：元
            'pe_ttm': df['市盈率-动态'],
            'pb': df['市净率'],
            'ps_ttm': df.get('市销率', None),  # 可能没有
            'total_shares': df.get('总股本', None),  # 可能没有
            'float_shares': df.get('流通股', None),  # 可能没有
            'update_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 添加市场标识
        def get_market(code):
            if code.startswith(('6', '68')):
                return 'sh'
            elif code.startswith(('0', '3')):
                return 'sz'
            elif code.startswith(('4', '8')):
                return 'bj'
            else:
                return 'unknown'
        
        market_data['market'] = market_data['code'].apply(get_market)
        market_data['full_code'] = market_data['market'] + '.' + market_data['code']
        
        # 添加市值分类（方便筛选）
        def classify_market_cap(cap):
            if pd.isna(cap):
                return '未知'
            cap_yi = cap / 1e8  # 转换为亿
            if cap_yi < 50:
                return '小盘股'
            elif cap_yi < 200:
                return '中盘股'
            elif cap_yi < 1000:
                return '大盘股'
            else:
                return '超大盘股'
        
        market_data['cap_category'] = market_data['total_cap'].apply(classify_market_cap)
        
        # 保存到数据库
        logger.info("正在保存到数据库...")
        market_data.to_sql('market_cap_data', db.conn, if_exists='replace', index=False)
        
        # 统计信息
        logger.info("\n" + "="*80)
        logger.info("✅ 市值数据补充完成！")
        logger.info("="*80)
        logger.info(f"总股票数: {len(market_data)}")
        logger.info(f"\n市值分类统计:")
        cap_stats = market_data['cap_category'].value_counts()
        for cat, count in cap_stats.items():
            logger.info(f"  {cat:10s}: {count:5d} 只")
        
        # 显示50-200亿市值的股票数量
        mid_cap = market_data[
            (market_data['total_cap'] >= 50e8) & 
            (market_data['total_cap'] <= 200e8)
        ]
        logger.info(f"\n🎯 50-200亿市值股票: {len(mid_cap)} 只")
        
        return market_data
        
    except Exception as e:
        logger.error(f"❌ 获取市值数据失败: {e}")
        raise


def supplement_industry_data(db):
    """补充行业数据"""
    logger.info("\n" + "="*80)
    logger.info("🏭 开始补充行业数据...")
    logger.info("="*80)
    
    try:
        # 获取行业分类
        logger.info("正在从 akshare 获取行业分类...")
        
        # 方法1: 获取板块成分股（包含行业信息）
        industry_data_list = []
        
        # 获取所有行业板块
        logger.info("正在获取行业板块列表...")
        industry_list = ak.stock_board_industry_name_em()
        
        logger.info(f"找到 {len(industry_list)} 个行业板块")
        
        # 获取每个行业的成分股
        from tqdm import tqdm
        for idx, row in tqdm(industry_list.iterrows(), total=len(industry_list), desc="获取行业成分"):
            industry_name = row['板块名称']
            
            try:
                # 获取该行业的成分股
                stocks = ak.stock_board_industry_cons_em(symbol=industry_name)
                
                for _, stock in stocks.iterrows():
                    industry_data_list.append({
                        'code': stock['代码'],
                        'name': stock['名称'],
                        'industry': industry_name,
                        'update_date': datetime.now().strftime('%Y-%m-%d')
                    })
                
                # 限速
                if idx % 10 == 0:
                    import time
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.warning(f"获取 {industry_name} 失败: {e}")
                continue
        
        if not industry_data_list:
            logger.warning("⚠️ 未能获取行业数据")
            return None
        
        # 转换为DataFrame
        industry_data = pd.DataFrame(industry_data_list)
        
        # 去重（一只股票可能属于多个行业，保留第一个）
        industry_data = industry_data.drop_duplicates(subset=['code'], keep='first')
        
        # 添加市场标识
        def get_market(code):
            if code.startswith(('6', '68')):
                return 'sh'
            elif code.startswith(('0', '3')):
                return 'sz'
            elif code.startswith(('4', '8')):
                return 'bj'
            else:
                return 'unknown'
        
        industry_data['market'] = industry_data['code'].apply(get_market)
        industry_data['full_code'] = industry_data['market'] + '.' + industry_data['code']
        
        # 保存到数据库
        logger.info("正在保存到数据库...")
        industry_data.to_sql('industry_data', db.conn, if_exists='replace', index=False)
        
        # 统计信息
        logger.info("\n" + "="*80)
        logger.info("✅ 行业数据补充完成！")
        logger.info("="*80)
        logger.info(f"总股票数: {len(industry_data)}")
        logger.info(f"行业数量: {industry_data['industry'].nunique()}")
        logger.info(f"\n行业分布 Top 10:")
        industry_stats = industry_data['industry'].value_counts().head(10)
        for ind, count in industry_stats.items():
            logger.info(f"  {ind:20s}: {count:4d} 只")
        
        return industry_data
        
    except Exception as e:
        logger.error(f"❌ 获取行业数据失败: {e}")
        logger.info("提示: 行业数据获取较慢，可能需要几分钟")
        raise


def verify_data(db):
    """验证补充的数据"""
    logger.info("\n" + "="*80)
    logger.info("🔍 验证补充的数据...")
    logger.info("="*80)
    
    try:
        # 检查市值数据
        market_cap = pd.read_sql("SELECT COUNT(*) as count FROM market_cap_data", db.conn)
        logger.info(f"✅ 市值数据表: {market_cap['count'].iloc[0]} 条记录")
        
        # 检查行业数据
        try:
            industry = pd.read_sql("SELECT COUNT(*) as count FROM industry_data", db.conn)
            logger.info(f"✅ 行业数据表: {industry['count'].iloc[0]} 条记录")
        except:
            logger.warning("⚠️ 行业数据表不存在")
        
        # 测试查询：50-200亿市值的股票
        query = """
            SELECT code, name, total_cap/100000000 as cap_yi, cap_category
            FROM market_cap_data
            WHERE total_cap >= 5000000000 AND total_cap <= 20000000000
            ORDER BY total_cap DESC
            LIMIT 10
        """
        result = pd.read_sql(query, db.conn)
        
        logger.info(f"\n📊 50-200亿市值股票示例（前10只）:")
        logger.info(result.to_string(index=False))
        
        # 测试查询：带行业的股票
        try:
            query = """
                SELECT m.code, m.name, m.total_cap/100000000 as cap_yi, i.industry
                FROM market_cap_data m
                LEFT JOIN industry_data i ON m.code = i.code
                WHERE m.total_cap >= 5000000000 AND m.total_cap <= 20000000000
                LIMIT 10
            """
            result = pd.read_sql(query, db.conn)
            logger.info(f"\n📊 带行业信息的中盘股示例:")
            logger.info(result.to_string(index=False))
        except:
            pass
        
        logger.info("\n" + "="*80)
        logger.info("✅ 数据验证完成！")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"❌ 验证失败: {e}")


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("🚀 数据补充工具")
    logger.info("="*80)
    logger.info("将补充以下数据:")
    logger.info("  1. 市值数据（总市值、流通市值、PE、PB）")
    logger.info("  2. 行业分类（申万行业）")
    logger.info("="*80)
    
    # 初始化数据库
    db = StockDatabase("data/a_share.db")
    
    try:
        # 补充市值数据
        market_data = supplement_market_cap_data(db)
        
        # 补充行业数据
        industry_data = supplement_industry_data(db)
        
        # 验证数据
        verify_data(db)
        
        logger.info("\n" + "="*80)
        logger.info("🎉 所有数据补充完成！")
        logger.info("="*80)
        logger.info("\n现在你可以:")
        logger.info("  1. 按市值筛选股票（50-200亿）")
        logger.info("  2. 按行业分析（行业轮动）")
        logger.info("  3. 开发完整的选股策略")
        logger.info("\n下一步: 运行策略开发脚本")
        logger.info("  python3 develop_strategy.py")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n❌ 补充数据失败: {e}")
        logger.info("\n可能的原因:")
        logger.info("  1. 网络连接问题")
        logger.info("  2. akshare 接口变化")
        logger.info("  3. 数据源暂时不可用")
        logger.info("\n建议:")
        logger.info("  1. 检查网络连接")
        logger.info("  2. 稍后重试")
        logger.info("  3. 或者先用现有数据开发策略")
    finally:
        db.close()


if __name__ == "__main__":
    main()
