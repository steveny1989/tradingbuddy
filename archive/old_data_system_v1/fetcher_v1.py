# -*- coding: utf-8 -*-
"""
数据采集模块 V2 - 使用三层架构

将数据写入新的三层架构：
1. Raw Layer - 原始数据
2. Cleaned Layer - 清洗后的数据
3. Aggregated Layer - 技术指标
"""
import akshare as ak
import pandas as pd
import time
from datetime import datetime
from typing import Optional, List
import logging
from tqdm import tqdm

from src.config.settings import *
from src.data.layers import RawLayer, CleanedLayer, AggregatedLayer

logger = logging.getLogger(__name__)


class DataFetcherV2:
    """数据采集类 V2 - 使用三层架构"""
    
    def __init__(self):
        """初始化三层数据架构"""
        self.raw = RawLayer()
        self.cleaned = CleanedLayer()
        self.aggregated = AggregatedLayer()
        logger.info("DataFetcherV2 initialized with 3-layer architecture")
    
    def fetch_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表"""
        logger.info("开始获取股票列表...")
        
        try:
            # 获取实时行情数据（包含所有A股）
            df = ak.stock_zh_a_spot_em()
            
            # 提取关键字段
            stock_list = pd.DataFrame({
                'code': df['代码'],
                'name': df['名称'],
                'market': df['代码'].apply(self._get_market),
                'list_date': '',
                'status': 'active',
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            logger.info(f"✅ 获取股票列表成功: {len(stock_list)} 只")
            return stock_list
            
        except Exception as e:
            logger.error(f"❌ 获取股票列表失败: {e}")
            raise
    
    def fetch_history(
        self, 
        code: str, 
        start_date: str = START_DATE, 
        end_date: str = END_DATE, 
        retries: int = MAX_RETRIES
    ) -> Optional[pd.DataFrame]:
        """
        获取单只股票历史数据
        
        Args:
            code: 股票代码（纯数字，如 600519）
            start_date: 开始日期
            end_date: 结束日期
            retries: 重试次数
            
        Returns:
            DataFrame 或 None
        """
        for attempt in range(retries):
            try:
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # 前复权
                )
                
                if df.empty:
                    logger.warning(f"⚠️ {code} 返回数据为空")
                    return None
                
                # 重命名列
                df = df.rename(columns=AKSHARE_COLUMNS)
                
                # 添加股票代码
                df['code'] = code
                
                # 选择需要的字段
                columns = ['date', 'code', 'open', 'high', 'low', 'close', 
                          'volume', 'amount', 'pct_chg', 'turnover']
                df = df[[col for col in columns if col in df.columns]]
                
                return df
                
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"⚠️ {code} 第 {attempt + 1} 次尝试失败，重试中...")
                    time.sleep(1)
                else:
                    logger.error(f"❌ {code} 获取失败: {e}")
                    return None
        
        return None
    
    def save_stock_data(self, code: str, df: pd.DataFrame) -> dict:
        """
        保存股票数据到三层架构
        
        Args:
            code: 股票代码
            df: 数据框
            
        Returns:
            dict: 保存统计信息
        """
        if df.empty:
            return {'raw': 0, 'cleaned': 0, 'aggregated': 0}
        
        stats = {}
        
        # 1. 保存到 Raw Layer
        raw_count = self.raw.save_daily_data(df, source='akshare')
        stats['raw'] = raw_count
        
        # 2. 清洗并保存到 Cleaned Layer
        clean_result = self.cleaned.clean_and_save_daily_data(df, source='akshare')
        stats['cleaned'] = clean_result['valid']
        stats['invalid'] = clean_result['invalid']
        stats['valid_rate'] = clean_result['valid_rate']
        
        # 3. 计算技术指标并保存到 Aggregated Layer
        try:
            # 从 Cleaned Layer 读取有效数据
            cleaned_df = self.cleaned.get_daily_data(code, only_valid=True)
            if cleaned_df is not None and not cleaned_df.empty:
                indicator_count = self.aggregated.calculate_and_save_indicators(code, cleaned_df)
                stats['aggregated'] = indicator_count
            else:
                stats['aggregated'] = 0
        except Exception as e:
            logger.warning(f"计算技术指标失败 {code}: {e}")
            stats['aggregated'] = 0
        
        return stats
    
    def update_daily(self, date: str = None):
        """
        每日增量更新
        
        Args:
            date: 更新日期，格式 YYYYMMDD，默认今天
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"\n🔄 开始每日增量更新: {date}")
        logger.info("="*60)
        
        # 获取股票列表
        stock_list = self.fetch_stock_list()
        
        total = len(stock_list)
        success = 0
        failed = 0
        total_records = 0
        
        logger.info(f"📊 共需更新 {total} 只股票")
        
        # 使用进度条
        with tqdm(total=total, desc="更新进度") as pbar:
            for idx, row in stock_list.iterrows():
                code = row['code']
                
                try:
                    # 获取最近一天的数据
                    df = self.fetch_history(
                        code=code,
                        start_date=date,
                        end_date=date
                    )
                    
                    if df is not None and not df.empty:
                        # 保存到三层架构
                        stats = self.save_stock_data(code, df)
                        
                        success += 1
                        total_records += stats['raw']
                        
                        pbar.set_postfix({
                            '成功': success,
                            '失败': failed,
                            '记录': total_records
                        })
                    else:
                        failed += 1
                    
                    # 控制请求频率
                    time.sleep(SLEEP_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"❌ {code} 更新失败: {e}")
                    failed += 1
                
                pbar.update(1)
        
        # 显示统计信息
        logger.info("\n" + "="*60)
        logger.info("📊 更新后统计:")
        logger.info(f"  成功: {success} 只")
        logger.info(f"  失败: {failed} 只")
        logger.info(f"  总记录数: {total_records}")
        logger.info(f"  成功率: {success/total*100:.1f}%")
        
        # 显示各层统计
        raw_stats = self.raw.get_stats()
        cleaned_stats = self.cleaned.get_stats()
        
        logger.info("\n📈 数据层统计:")
        logger.info(f"  Raw Layer: {raw_stats['daily']['total_records']:,} 条记录")
        logger.info(f"  Cleaned Layer: {cleaned_stats['daily']['valid_records']:,} 条有效记录")
        logger.info(f"  数据质量: {cleaned_stats['daily']['valid_rate']*100:.1f}%")
        
        logger.info("\n✅ 每日更新完成！")
    
    def batch_fetch_all(
        self, 
        start_date: str = START_DATE, 
        force_update: bool = False
    ):
        """
        批量下载全市场数据
        
        Args:
            start_date: 开始日期
            force_update: 是否强制更新
        """
        # 获取股票列表
        stock_list = self.fetch_stock_list()
        
        total = len(stock_list)
        success = 0
        failed = 0
        skipped = 0
        total_records = 0
        
        logger.info(f"\n🚀 开始批量下载，共 {total} 只股票")
        logger.info(f"📅 数据范围: {start_date} ~ {END_DATE}")
        logger.info("="*60)
        
        # 使用进度条
        with tqdm(total=total, desc="下载进度") as pbar:
            for idx, row in stock_list.iterrows():
                code = row['code']
                
                try:
                    # 检查是否需要更新
                    if not force_update:
                        last_date = self.cleaned.get_daily_data(code, only_valid=True)
                        if last_date is not None and not last_date.empty:
                            latest = last_date['date'].max()
                            if latest >= datetime.now().strftime('%Y-%m-%d'):
                                skipped += 1
                                pbar.update(1)
                                pbar.set_postfix({
                                    '成功': success,
                                    '失败': failed,
                                    '跳过': skipped
                                })
                                continue
                    
                    # 获取历史数据
                    df = self.fetch_history(
                        code=code,
                        start_date=start_date,
                        end_date=END_DATE
                    )
                    
                    if df is not None and not df.empty:
                        # 保存到三层架构
                        stats = self.save_stock_data(code, df)
                        
                        success += 1
                        total_records += stats['raw']
                        
                        pbar.set_postfix({
                            '成功': success,
                            '失败': failed,
                            '跳过': skipped,
                            '记录': total_records
                        })
                    else:
                        failed += 1
                    
                    # 控制请求频率
                    time.sleep(SLEEP_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"❌ {code} 下载失败: {e}")
                    failed += 1
                
                pbar.update(1)
        
        # 显示最终统计
        logger.info("\n" + "="*60)
        logger.info("📊 下载完成统计:")
        logger.info(f"  成功: {success} 只")
        logger.info(f"  失败: {failed} 只")
        logger.info(f"  跳过: {skipped} 只")
        logger.info(f"  总记录数: {total_records:,}")
        logger.info(f"  成功率: {success/(total-skipped)*100:.1f}%")
        
        # 显示各层统计
        raw_stats = self.raw.get_stats()
        cleaned_stats = self.cleaned.get_stats()
        
        logger.info("\n📈 数据层统计:")
        logger.info(f"  Raw Layer:")
        logger.info(f"    - 总记录: {raw_stats['daily']['total_records']:,}")
        logger.info(f"    - 股票数: {raw_stats['daily']['total_stocks']}")
        logger.info(f"  Cleaned Layer:")
        logger.info(f"    - 有效记录: {cleaned_stats['daily']['valid_records']:,}")
        logger.info(f"    - 停牌记录: {cleaned_stats['daily']['suspended_records']:,}")
        logger.info(f"    - 数据质量: {cleaned_stats['daily']['valid_rate']*100:.1f}%")
        
        logger.info("\n✨ 全市场数据下载完成！")
    
    def _get_market(self, code: str) -> str:
        """根据代码判断市场"""
        if code.startswith('6'):
            return 'sh'
        elif code.startswith('0') or code.startswith('3'):
            return 'sz'
        elif code.startswith('8') or code.startswith('4'):
            return 'bj'
        else:
            return 'unknown'
    
    def get_stats(self) -> dict:
        """获取数据统计信息"""
        raw_stats = self.raw.get_stats()
        cleaned_stats = self.cleaned.get_stats()
        
        return {
            'raw': raw_stats,
            'cleaned': cleaned_stats,
            'summary': {
                'total_stocks': cleaned_stats['daily']['total_stocks'],
                'total_records': cleaned_stats['daily']['total_records'],
                'valid_records': cleaned_stats['daily']['valid_records'],
                'valid_rate': cleaned_stats['daily']['valid_rate']
            }
        }
