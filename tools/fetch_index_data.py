#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数数据获取工具 - V2 版本
使用三层数据架构存储指数数据
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
import logging
import sqlite3
from datetime import datetime
from src.config.settings import DB_PATHS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 指数列表
INDICES = [
    # A股指数
    {'name': '上证指数', 'code': '000001', 'market': 'sh', 'symbol': 'sh000001', 'type': 'cn'},
    {'name': '深证成指', 'code': '399001', 'market': 'sz', 'symbol': 'sz399001', 'type': 'cn'},
    {'name': '创业板指', 'code': '399006', 'market': 'sz', 'symbol': 'sz399006', 'type': 'cn'},
    {'name': '科创50', 'code': '000688', 'market': 'sh', 'symbol': 'sh000688', 'type': 'cn'},
    {'name': '沪深300', 'code': '000300', 'market': 'sh', 'symbol': 'sh000300', 'type': 'cn'},
    {'name': '中证500', 'code': '000905', 'market': 'sh', 'symbol': 'sh000905', 'type': 'cn'},
    {'name': '中证1000', 'code': '000852', 'market': 'sh', 'symbol': 'sh000852', 'type': 'cn'},
    
    # 港股指数
    {'name': '恒生指数', 'code': 'HSI', 'market': 'hk', 'symbol': 'HSI', 'type': 'hk'},
    {'name': '恒生科技', 'code': 'HSTECH', 'market': 'hk', 'symbol': 'HSTECH', 'type': 'hk'},
    
    # 全球指数
    {'name': '道琼斯', 'code': 'DJI', 'market': 'us', 'symbol': '.DJI', 'type': 'global'},
    {'name': '纳斯达克', 'code': 'IXIC', 'market': 'us', 'symbol': '.IXIC', 'type': 'global'},
    {'name': '标普500', 'code': 'SPX', 'market': 'us', 'symbol': '.SPX', 'type': 'global'},
]


def get_market_db_path():
    """获取市场数据库路径"""
    raw_path = DB_PATHS['raw']
    os.makedirs(raw_path, exist_ok=True)
    return os.path.join(raw_path, 'market_raw.db')


def init_market_db():
    """初始化市场数据库表结构"""
    db_path = get_market_db_path()
    
    with sqlite3.connect(db_path) as conn:
        # 创建指数数据表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS index_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                market TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                -- 元数据
                source TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                UNIQUE(code, date)
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_index_daily_code_date ON index_daily(code, date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_index_daily_market ON index_daily(market)')
        conn.commit()
    
    logger.info(f"✅ 市场数据库初始化完成: {db_path}")


def fetch_cn_index_data(symbol: str, start_date: str = '20200101'):
    """获取A股指数数据"""
    try:
        logger.info(f"正在获取 {symbol} 数据...")
        df = ak.stock_zh_index_daily(symbol=symbol)
        
        if df is None or df.empty:
            logger.warning(f"{symbol} 返回空数据")
            return None
        
        # 重命名列
        column_mapping = {
            'date': 'date',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'amount'
        }
        
        df = df.rename(columns=column_mapping)
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df = df[df['date'] >= start_date.replace('-', '')]
        
        # 确保必需列存在
        for col in ['date', 'open', 'close', 'high', 'low']:
            if col not in df.columns:
                df[col] = 0
        
        if 'volume' not in df.columns:
            df['volume'] = 0
        if 'amount' not in df.columns:
            df['amount'] = 0
        
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']]
        df = df.sort_values('date')
        
        logger.info(f"✅ {symbol} 获取成功，共 {len(df)} 条数据")
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 获取失败: {e}")
        return None


def fetch_hk_index_data(symbol: str, start_date: str = '2020-01-01'):
    """获取港股指数数据"""
    try:
        logger.info(f"正在获取 {symbol} 数据...")
        df = ak.stock_hk_index_daily_em(symbol=symbol)
        
        if df is None or df.empty:
            logger.warning(f"{symbol} 返回空数据")
            return None
        
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        
        df = df.rename(columns=column_mapping)
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df = df[df['date'] >= start_date]
        
        for col in ['date', 'open', 'close', 'high', 'low']:
            if col not in df.columns:
                df[col] = 0
        
        if 'volume' not in df.columns:
            df['volume'] = 0
        if 'amount' not in df.columns:
            df['amount'] = 0
        
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']]
        df = df.sort_values('date')
        
        logger.info(f"✅ {symbol} 获取成功，共 {len(df)} 条数据")
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 获取失败: {e}")
        return None


def fetch_global_index_data(symbol: str, start_date: str = '2020-01-01'):
    """获取全球指数数据"""
    try:
        logger.info(f"正在获取 {symbol} 数据...")
        df = ak.index_investing_global(symbol=symbol, period="每日", start_date=start_date, end_date=datetime.now().strftime('%Y-%m-%d'))
        
        if df is None or df.empty:
            logger.warning(f"{symbol} 返回空数据")
            return None
        
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '涨跌幅': 'pct_chg'
        }
        
        df = df.rename(columns=column_mapping)
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df = df[df['date'] >= start_date]
        
        for col in ['date', 'open', 'close', 'high', 'low']:
            if col not in df.columns:
                df[col] = 0
        
        df['volume'] = 0
        df['amount'] = 0
        
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']]
        df = df.sort_values('date')
        
        logger.info(f"✅ {symbol} 获取成功，共 {len(df)} 条数据")
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 获取失败: {e}")
        return None


def save_index_to_db(index_info: dict, df: pd.DataFrame):
    """
    保存指数数据到 V2 数据库
    
    Args:
        index_info: 指数信息字典
        df: 数据DataFrame
    """
    try:
        db_path = get_market_db_path()
        full_code = f"{index_info['market']}.{index_info['code']}"
        
        logger.info(f"正在保存 {index_info['name']} 到 V2 数据库...")
        
        fetched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(db_path) as conn:
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO index_daily 
                    (code, name, market, date, open, high, low, close, volume, amount, source, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    full_code,
                    index_info['name'],
                    index_info['market'],
                    row['date'],
                    row['open'],
                    row['high'],
                    row['low'],
                    row['close'],
                    row['volume'],
                    row['amount'],
                    'akshare',
                    fetched_at
                ))
            conn.commit()
        
        logger.info(f"✅ {index_info['name']} 保存成功，共 {len(df)} 条数据")
        
    except Exception as e:
        logger.error(f"❌ {index_info['name']} 保存失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始下载指数数据 (V2 架构)")
    logger.info(f"目标数据库: {get_market_db_path()}")
    logger.info("=" * 60)
    
    # 初始化数据库
    init_market_db()
    
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
            # 保存到 V2 数据库
            save_index_to_db(index_info, df)
            success_count += 1
        else:
            failed_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"下载完成！成功: {success_count}, 失败: {failed_count}")
    logger.info(f"数据已保存到: {get_market_db_path()}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
