# -*- coding: utf-8 -*-
"""数据采集模块"""
import akshare as ak
import pandas as pd
import time
from datetime import datetime
from typing import Optional, List
import logging
from tqdm import tqdm
from core.config import *

logger = logging.getLogger(__name__)


class DataFetcher:
    """数据采集类"""
    
    def __init__(self, db):
        self.db = db
    
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
                'list_date': '',  # akshare实时数据不包含上市日期
                'status': 'active',
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # 添加完整代码
            stock_list['full_code'] = stock_list['market'] + '.' + stock_list['code']
            
            # 保存到数据库
            self.db.save_stock_list(stock_list)
            
            logger.info(f"✅ 获取股票列表成功: {len(stock_list)} 只")
            return stock_list
            
        except Exception as e:
            logger.error(f"❌ 获取股票列表失败: {e}")
            raise
    
    def fetch_market_snapshot(self) -> pd.DataFrame:
        """获取市场快照（实时行情）"""
        logger.info("获取市场快照...")
        
        try:
            df = ak.stock_zh_a_spot_em()
            
            # 重命名列
            snapshot = df.rename(columns=MARKET_INFO_COLUMNS)
            snapshot['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # 选择需要的字段
            columns = ['code', 'date', 'price', 'pct_chg', 'volume', 'amount', 
                      'pe_ttm', 'pb', 'total_cap', 'float_cap', 'turnover']
            snapshot = snapshot[[col for col in columns if col in snapshot.columns]]
            
            # 保存到数据库
            self.db.save_market_snapshot(snapshot)
            
            logger.info(f"✅ 市场快照保存成功: {len(snapshot)} 只股票")
            return snapshot
            
        except Exception as e:
            logger.error(f"❌ 获取市场快照失败: {e}")
            raise
    
    def fetch_history(self, code: str, start_date: str = START_DATE, 
                     end_date: str = END_DATE, retries: int = MAX_RETRIES) -> Optional[pd.DataFrame]:
        """获取单只股票历史数据"""
        
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
    
    def batch_fetch_all(self, start_date: str = START_DATE, force_update: bool = False):
        """批量下载全市场数据"""
        
        # 获取股票列表
        stock_list = self.db.get_stock_list()
        if stock_list.empty:
            logger.info("股票列表为空，先获取股票列表...")
            stock_list = self.fetch_stock_list()
        
        total = len(stock_list)
        success = 0
        failed = 0
        skipped = 0
        
        logger.info(f"🚀 开始批量下载，共 {total} 只股票")
        logger.info(f"📅 数据范围: {start_date} ~ {END_DATE}")
        
        # 使用进度条
        with tqdm(total=total, desc="下载进度") as pbar:
            for idx, row in stock_list.iterrows():
                code = row['code']
                full_code = row.get('full_code', f"{row['market']}.{code}")
                
                # 检查是否需要更新
                if not force_update and self.db.table_exists(full_code):
                    last_date = self.db.get_last_date(full_code)
                    if last_date and last_date >= datetime.now().strftime('%Y-%m-%d'):
                        skipped += 1
                        pbar.update(1)
                        pbar.set_postfix({'成功': success, '失败': failed, '跳过': skipped})
                        continue
                
                # 获取数据
                df = self.fetch_history(code, start_date)
                
                if df is not None and not df.empty:
                    self.db.save_daily_data(full_code, df)
                    success += 1
                else:
                    failed += 1
                
                # 更新进度条
                pbar.update(1)
                pbar.set_postfix({'成功': success, '失败': failed, '跳过': skipped})
                
                # 限速
                if idx % BATCH_SIZE == 0 and idx > 0:
                    time.sleep(SLEEP_INTERVAL)
        
        logger.info(f"\n✨ 批量下载完成！")
        logger.info(f"📊 成功: {success} | 失败: {failed} | 跳过: {skipped}")
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'skipped': skipped
        }
    
    def detect_adjustment(self, code: str, full_code: str, new_data: pd.DataFrame) -> bool:
        """
        检测是否发生除权息（前复权数据变化）
        
        Args:
            code: 股票代码（不含市场前缀）
            full_code: 完整股票代码（含市场前缀）
            new_data: 新获取的数据
            
        Returns:
            True表示检测到除权息，需要全量刷新
        """
        if new_data.empty:
            return False
        
        # 获取数据库中的最新数据
        db_data = self.db.get_daily_data(full_code)
        
        if db_data.empty or len(db_data) < 2:
            return False
        
        # 获取最新日期的前一个交易日
        db_data = db_data.sort_values('date', ascending=False)
        
        # 找到新数据和数据库数据的重叠日期
        common_dates = set(new_data['date']) & set(db_data['date'])
        
        if not common_dates:
            return False
        
        # 检查重叠日期的价格是否有显著差异
        for date in common_dates:
            new_row = new_data[new_data['date'] == date]
            db_row = db_data[db_data['date'] == date]
            
            if new_row.empty or db_row.empty:
                continue
            
            new_price = new_row['close'].iloc[0]
            db_price = db_row['close'].iloc[0]
            
            # 如果价格差异超过5%，可能发生了除权息
            price_diff = abs(new_price - db_price) / db_price
            
            if price_diff > 0.05:
                logger.warning(
                    f"⚠️ {full_code} 检测到除权息: "
                    f"{date} 数据库价格 {db_price:.2f} vs 新价格 {new_price:.2f} "
                    f"(差异 {(new_price-db_price)/db_price:.2%})"
                )
                return True
        
        return False
    
    def refresh_history(self, code: str, full_code: str, reason: str = "除权息"):
        """
        全量刷新历史数据
        
        Args:
            code: 股票代码（不含市场前缀）
            full_code: 完整股票代码（含市场前缀）
            reason: 刷新原因
        """
        logger.info(f"🔄 {full_code} 触发全量刷新 (原因: {reason})")
        
        try:
            # 获取全部历史数据
            df = self.fetch_history(code, start_date=START_DATE, end_date=END_DATE)
            
            if df is not None and not df.empty:
                self.db.save_daily_data(full_code, df)
                logger.info(f"✅ {full_code} 全量刷新完成: {len(df)} 条记录")
                return True
            else:
                logger.error(f"❌ {full_code} 全量刷新失败: 无数据")
                return False
                
        except Exception as e:
            logger.error(f"❌ {full_code} 全量刷新失败: {e}")
            return False
    
    def update_daily(self, date: str = None, check_adjustment: bool = True):
        """
        增量更新（每日更新，带除权息检测）
        
        Args:
            date: 更新日期（None表示今天）
            check_adjustment: 是否检查除权息
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"🔄 开始增量更新: {date}")
        if check_adjustment:
            logger.info("📊 除权息检测: 已启用")
        
        stock_list = self.db.get_stock_list()
        total = len(stock_list)
        success = 0
        refreshed = 0
        
        with tqdm(total=total, desc="更新进度") as pbar:
            for idx, row in stock_list.iterrows():
                code = row['code']
                full_code = row.get('full_code', f"{row['market']}.{code}")
                
                # 获取最近几天的数据（用于除权息检测）
                # 获取最近5天数据，确保有重叠日期可以对比
                from datetime import datetime as dt, timedelta
                end_date_obj = dt.strptime(date, '%Y%m%d')
                start_date_obj = end_date_obj - timedelta(days=7)
                start_date_str = start_date_obj.strftime('%Y%m%d')
                
                df = self.fetch_history(code, start_date=start_date_str, end_date=date)
                
                if df is not None and not df.empty:
                    # 除权息检测
                    if check_adjustment and self.detect_adjustment(code, full_code, df):
                        # 触发全量刷新
                        if self.refresh_history(code, full_code):
                            refreshed += 1
                            success += 1
                    else:
                        # 正常增量更新
                        self.db.append_daily_data(full_code, df)
                        success += 1
                
                pbar.update(1)
                pbar.set_postfix({'成功': success, '刷新': refreshed})
                
                # 限速
                if idx % BATCH_SIZE == 0:
                    time.sleep(SLEEP_INTERVAL)
        
        logger.info(f"✅ 增量更新完成: {success}/{total}")
        if refreshed > 0:
            logger.info(f"🔄 除权息刷新: {refreshed} 只股票")
        
        # 同时更新市场快照
        self.fetch_market_snapshot()
    
    @staticmethod
    def _get_market(code: str) -> str:
        """根据代码判断市场"""
        if code.startswith(('6', '68')):
            return 'sh'
        elif code.startswith(('0', '3')):
            return 'sz'
        elif code.startswith(('4', '8')):
            return 'bj'
        else:
            return 'unknown'
