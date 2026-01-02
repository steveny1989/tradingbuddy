#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载指数数据到数据库
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import akshare as ak
import pandas as pd
from datetime import datetime
from src.data.database import StockDatabase
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 主要指数列表
INDICES = [
    # 中国大陆
    {'code': '000001', 'name': '上证指数', 'market': 'sh', 'symbol': 'sh000001', 'type': 'cn'},
    {'code': '399001', 'name': '深证成指', 'market': 'sz', 'symbol': 'sz399001', 'type': 'cn'},
    {'code': '399006', 'name': '创业板指', 'market': 'sz', 'symbol': 'sz399006', 'type': 'cn'},
    {'code': '000300', 'name': '沪深300', 'market': 'sh', 'symbol': 'sh000300', 'type': 'cn'},
    {'code': '000016', 'name': '上证50', 'market': 'sh', 'symbol': 'sh000016', 'type': 'cn'},
    {'code': '000905', 'name': '中证500', 'market': 'sh', 'symbol': 'sh000905', 'type': 'cn'},
    
    # 香港
    {'code': 'HSI', 'name': '恒生指数', 'market': 'hk', 'symbol': 'HSI', 'type': 'hk'},
    {'code': 'HSCEI', 'name': '国企指数', 'market': 'hk', 'symbol': 'HSCEI', 'type': 'hk'},
    
    # 全球指数（使用东方财富的全球指数接口，需要使用中文名称）
    {'code': 'N225', 'name': '日经225', 'market': 'jp', 'symbol': '日经225', 'type': 'global'},
    {'code': 'DJIA', 'name': '道琼斯', 'market': 'us', 'symbol': '道琼斯', 'type': 'global'},
    {'code': 'SPX', 'name': '标普500', 'market': 'us', 'symbol': '标普500', 'type': 'global'},
    {'code': 'NDX', 'name': '纳斯达克', 'market': 'us', 'symbol': '纳斯达克', 'type': 'global'},
    {'code': 'FTSE', 'name': '英国富时', 'market': 'uk', 'symbol': '英国富时100', 'type': 'global'},
]


def fetch_cn_index_data(symbol: str, start_date: str = '20200101') -> pd.DataFrame:
    """
    获取中国指数历史数据
    
    Args:
        symbol: 指数代码，如 'sh000001'
        start_date: 开始日期
    
    Returns:
        DataFrame with columns: date, open, close, high, low, volume, amount
    """
    try:
        logger.info(f"正在获取中国指数 {symbol} 的数据...")
        
        # 使用akshare获取指数数据
        df = ak.stock_zh_index_daily(symbol=symbol)
        
        if df.empty:
            logger.warning(f"{symbol} 返回数据为空")
            return None
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 筛选日期
        df = df[df['date'] >= start_date]
        
        # 确保所有必需的列都存在
        required_columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"{symbol} 缺少列 {col}")
                df[col] = 0
        
        # 如果没有amount列，添加一个（指数通常没有成交额）
        if 'amount' not in df.columns:
            df['amount'] = 0
        
        # 选择需要的列并确保顺序正确
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']]
        
        logger.info(f"✅ {symbol} 获取成功，共 {len(df)} 条数据")
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def fetch_hk_index_data(symbol: str, start_date: str = '20200101') -> pd.DataFrame:
    """
    获取香港指数历史数据
    
    Args:
        symbol: 指数代码，如 'HSI', 'HSCEI'
        start_date: 开始日期
    
    Returns:
        DataFrame with columns: date, open, close, high, low, volume, amount
    """
    try:
        logger.info(f"正在获取香港指数 {symbol} 的数据...")
        
        # 使用akshare获取香港指数数据
        df = ak.stock_hk_index_daily_em(symbol=symbol)
        
        if df.empty:
            logger.warning(f"{symbol} 返回数据为空")
            return None
        
        # 重命名列以匹配我们的格式
        column_mapping = {
            'date': 'date',
            'latest': 'close',
            'open': 'open',
            'high': 'high',
            'low': 'low',
        }
        
        df = df.rename(columns=column_mapping)
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 筛选日期
        df = df[df['date'] >= start_date]
        
        # 确保所有必需的列都存在
        required_columns = ['date', 'open', 'close', 'high', 'low']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"{symbol} 缺少列 {col}")
                df[col] = 0
        
        # 添加volume和amount列（香港指数通常没有这些数据）
        df['volume'] = 0
        df['amount'] = 0
        
        # 选择需要的列并确保顺序正确
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']]
        
        # 按日期排序
        df = df.sort_values('date')
        
        logger.info(f"✅ {symbol} 获取成功，共 {len(df)} 条数据")
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def fetch_global_index_data(symbol: str, start_date: str = '20200101') -> pd.DataFrame:
    """
    获取全球指数历史数据
    
    Args:
        symbol: 指数代码，如 'DJIA', 'SPX', 'N225'
        start_date: 开始日期
    
    Returns:
        DataFrame with columns: date, open, close, high, low, volume, amount
    """
    try:
        logger.info(f"正在获取全球指数 {symbol} 的数据...")
        
        # 使用akshare获取全球指数数据（不支持日期参数）
        df = ak.index_global_hist_em(symbol=symbol)
        
        if df.empty:
            logger.warning(f"{symbol} 返回数据为空")
            return None
        
        # 重命名列以匹配我们的格式
        column_mapping = {
            '日期': 'date',
            '收盘': 'close',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '涨跌幅': 'pct_chg'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 筛选日期
        df = df[df['date'] >= start_date]
        
        # 确保所有必需的列都存在
        required_columns = ['date', 'open', 'close', 'high', 'low']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"{symbol} 缺少列 {col}")
                df[col] = 0
        
        # 处理volume列
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
        else:
            df['volume'] = 0
        
        # 添加amount列（全球指数通常没有成交额）
        df['amount'] = 0
        
        # 选择需要的列并确保顺序正确
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']]
        
        # 按日期排序
        df = df.sort_values('date')
        
        logger.info(f"✅ {symbol} 获取成功，共 {len(df)} 条数据")
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_index_to_db(db: StockDatabase, index_info: dict, df: pd.DataFrame):
    """
    保存指数数据到数据库
    
    Args:
        db: 数据库实例
        index_info: 指数信息字典
        df: 数据DataFrame
    """
    try:
        full_code = f"{index_info['market']}.{index_info['code']}"
        table_name = f"daily_{index_info['market']}_{index_info['code']}"
        
        logger.info(f"正在保存 {index_info['name']} 到表 {table_name}...")
        
        # 创建表（如果不存在）
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            "date" TEXT PRIMARY KEY,
            "open" REAL,
            "close" REAL,
            "high" REAL,
            "low" REAL,
            "volume" INTEGER,
            "amount" REAL
        )
        """
        db.conn.execute(create_table_sql)
        db.conn.commit()
        
        # 保存数据
        df.to_sql(table_name, db.conn, if_exists='replace', index=False)
        
        logger.info(f"✅ {index_info['name']} 保存成功，共 {len(df)} 条数据")
        
    except Exception as e:
        logger.error(f"❌ {index_info['name']} 保存失败: {e}")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始下载指数数据")
    logger.info("=" * 60)
    
    # 初始化数据库
    db = StockDatabase()
    
    success_count = 0
    failed_count = 0
    
    for index_info in INDICES:
        logger.info(f"\n处理 {index_info['name']} ({index_info['symbol']})...")
        
        # 根据类型选择不同的获取方法
        if index_info['type'] == 'cn':
            df = fetch_cn_index_data(index_info['symbol'], start_date='20200101')
        elif index_info['type'] == 'hk':
            df = fetch_hk_index_data(index_info['symbol'], start_date='2020-01-01')
        else:  # global
            df = fetch_global_index_data(index_info['symbol'], start_date='2020-01-01')
        
        if df is not None and not df.empty:
            # 保存到数据库
            save_index_to_db(db, index_info, df)
            success_count += 1
        else:
            failed_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"下载完成！成功: {success_count}, 失败: {failed_count}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
