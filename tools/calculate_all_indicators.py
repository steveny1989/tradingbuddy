#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量计算所有股票的技术指标

从Cleaned Layer读取数据，计算指标后存入Aggregated Layer
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from src.data.layers import CleanedLayer, AggregatedLayer
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """指标批量计算器"""
    
    def __init__(self, max_workers: int = 4):
        """
        初始化
        
        Args:
            max_workers: 并行线程数
        """
        self.cleaned = CleanedLayer()
        self.aggregated = AggregatedLayer()
        self.max_workers = max_workers
    
    def get_all_stock_codes(self) -> list:
        """获取所有股票代码"""
        with sqlite3.connect(self.cleaned.daily_db) as conn:
            cursor = conn.execute("SELECT DISTINCT code FROM daily_cleaned ORDER BY code")
            codes = [row[0] for row in cursor.fetchall()]
        return codes
    
    def calculate_single_stock(self, code: str) -> dict:
        """
        计算单只股票的指标
        
        Args:
            code: 股票代码
            
        Returns:
            结果字典
        """
        try:
            # 读取清洗后的数据
            df = self.cleaned.get_daily_data(code, only_valid=True)
            
            if df is None or df.empty:
                return {'code': code, 'status': 'no_data', 'count': 0}
            
            # 计算并保存指标
            count = self.aggregated.calculate_and_save_indicators(code, df)
            
            return {'code': code, 'status': 'success', 'count': count}
            
        except Exception as e:
            logger.error(f"计算失败 {code}: {e}")
            return {'code': code, 'status': 'error', 'count': 0, 'error': str(e)}
    
    def calculate_all(self, limit: int = None, test_mode: bool = False):
        """
        批量计算所有股票
        
        Args:
            limit: 限制处理的股票数量
            test_mode: 测试模式
        """
        logger.info("\n" + "="*60)
        logger.info("批量计算技术指标")
        logger.info("="*60)
        
        # 获取所有股票代码
        all_codes = self.get_all_stock_codes()
        
        if test_mode:
            logger.info("测试模式：只处理10只股票")
            codes = all_codes[:10]
        elif limit:
            logger.info(f"限制模式：只处理{limit}只股票")
            codes = all_codes[:limit]
        else:
            codes = all_codes
        
        logger.info(f"找到 {len(codes)} 只股票需要计算")
        
        # 统计信息
        start_time = time.time()
        success_count = 0
        no_data_count = 0
        error_count = 0
        total_records = 0
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            futures = {executor.submit(self.calculate_single_stock, code): code 
                      for code in codes}
            
            # 处理结果
            for idx, future in enumerate(as_completed(futures), 1):
                result = future.result()
                
                if result['status'] == 'success':
                    success_count += 1
                    total_records += result['count']
                elif result['status'] == 'no_data':
                    no_data_count += 1
                elif result['status'] == 'error':
                    error_count += 1
                
                # 每100只股票打印一次进度
                if idx % 100 == 0:
                    elapsed = time.time() - start_time
                    speed = idx / elapsed
                    eta = (len(codes) - idx) / speed if speed > 0 else 0
                    logger.info(f"进度: {idx}/{len(codes)} ({idx/len(codes)*100:.1f}%) | "
                              f"成功: {success_count} | 速度: {speed:.1f}股/秒 | "
                              f"预计剩余: {eta/60:.1f}分钟")
        
        # 打印总结
        elapsed = time.time() - start_time
        logger.info("\n" + "="*60)
        logger.info("计算完成")
        logger.info("="*60)
        logger.info(f"总股票数: {len(codes)}")
        logger.info(f"成功: {success_count}")
        logger.info(f"无数据: {no_data_count}")
        logger.info(f"失败: {error_count}")
        logger.info(f"总记录数: {total_records:,}")
        logger.info(f"总耗时: {elapsed/60:.1f} 分钟")
        logger.info(f"平均速度: {len(codes)/elapsed:.1f} 股/秒")
        
        # 验证结果
        self.verify_calculation()
    
    def verify_calculation(self):
        """验证计算结果"""
        logger.info("\n" + "="*60)
        logger.info("验证计算结果")
        logger.info("="*60)
        
        stats = self.aggregated.get_stats()
        
        logger.info(f"\nAggregated Layer:")
        logger.info(f"  总记录: {stats['indicators']['total_records']:,}")
        logger.info(f"  股票数: {stats['indicators']['total_stocks']}")
        
        # 对比Cleaned Layer
        cleaned_stats = self.cleaned.get_stats()
        logger.info(f"\nCleaned Layer:")
        logger.info(f"  总记录: {cleaned_stats['daily']['total_records']:,}")
        logger.info(f"  股票数: {cleaned_stats['daily']['total_stocks']}")
        
        # 计算覆盖率
        if cleaned_stats['daily']['total_records'] > 0:
            coverage = stats['indicators']['total_records'] / cleaned_stats['daily']['total_records'] * 100
            logger.info(f"\n指标覆盖率: {coverage:.1f}%")
            
            if coverage > 95:
                logger.info("✅ 覆盖率正常")
            else:
                logger.warning("⚠️  覆盖率低于95%")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量计算技术指标')
    parser.add_argument('--test', action='store_true', help='测试模式（只处理10只股票）')
    parser.add_argument('--limit', type=int, help='限制处理的股票数量')
    parser.add_argument('--workers', type=int, default=4, help='并行线程数（默认4）')
    parser.add_argument('--verify-only', action='store_true', help='只验证，不计算')
    
    args = parser.parse_args()
    
    calculator = IndicatorCalculator(max_workers=args.workers)
    
    if args.verify_only:
        # 只验证
        calculator.verify_calculation()
    else:
        # 执行计算
        calculator.calculate_all(
            limit=args.limit,
            test_mode=args.test
        )
    
    logger.info("\n✅ 完成！")


if __name__ == "__main__":
    main()
