#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载大盘指数数据"""
import akshare as ak
import pandas as pd
from src.data.database import StockDatabase
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def download_index_data(index_code='sh.000001', symbol='sh000001'):
    """
    下载指数数据
    
    Args:
        index_code: 数据库中使用的代码（如 sh.000001）
        symbol: akshare使用的代码（如 sh000001）
    """
    logger.info(f"开始下载指数数据: {index_code}")
    
    try:
        # 使用akshare下载指数数据（使用stock_zh_index_daily_em接口）
        df = ak.stock_zh_index_daily_em(symbol=symbol)
        
        if df.empty:
            logger.error("下载失败：数据为空")
            return
        
        logger.info(f"原始列名: {df.columns.tolist()}")
        
        # 重命名列以匹配数据库格式
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '涨跌幅': 'pct_chg',
            '涨跌额': 'change',
            '换手率': 'turn'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 选择需要的列
        columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        if 'amount' in df.columns:
            columns.append('amount')
        if 'turn' in df.columns:
            columns.append('turn')
        
        df = df[columns]
        
        # 保存到数据库
        db = StockDatabase('data/a_share.db')
        db.save_daily_data(index_code, df)
        db.close()
        
        logger.info(f"下载完成: {len(df)} 条记录")
        logger.info(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
        
    except Exception as e:
        logger.error(f"下载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 下载上证指数
    download_index_data('sh.000001', 'sh000001')
    
    # 可选：下载深证成指
    # download_index_data('sz.399001', 'sz399001')
