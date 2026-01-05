# -*- coding: utf-8 -*-
"""
股票综合诊断引擎 (Stock Diagnosis Engine)

核心协调器，整合所有分析维度：
1. 技术面分析 (Technical Analysis)
2. 基本面分析 (Fundamental Analysis)
3. 行业面分析 (Sector Analysis)
4. 资金面分析 (Capital Analysis)
5. 大盘对比分析 (Market Comparison)

生成综合诊断报告，包括：
- 综合评分 (0-100)
- 综合评级 (优秀/良好/一般/较差/很差)
- 优势/劣势分析
- 投资建议
"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.business.diagnosis.models import (
    DiagnosisReport, DimensionAnalysis,
    calculate_overall_score, get_rating_from_score, get_status_from_score
)
from src.business.diagnosis.technical_analyzer import TechnicalAnalyzer
from src.business.diagnosis.fundamental_analyzer import FundamentalAnalyzer
from src.business.diagnosis.market_comparison import MarketComparisonAnalyzer
from src.business.post_market.sector_analysis import SectorAnalyzer
from src.business.post_market.capital_analysis import CapitalAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDiagnosisEngine:
    """股票综合诊断引擎"""
    
    def __init__(self, db_path: str = "data/a_share.db", cache_ttl: int = 3600):
        """
        初始化诊断引擎
        
        Args:
            db_path: 数据库路径
            cache_ttl: 缓存过期时间（秒），默认1小时
        """
        self.db_path = db_path
        self.cache_ttl = cache_ttl
        
        # 初始化所有分析器
        self.technical_analyzer = TechnicalAnalyzer(db_path)
        self.fundamental_analyzer = FundamentalAnalyzer(db_path)
        self.sector_analyzer = SectorAnalyzer(db_path)
        self.capital_analyzer = CapitalAnalyzer(db_path)
        self.market_comparison_analyzer = MarketComparisonAnalyzer(db_path)
        
        # 简单的内存缓存（生产环境应使用Redis等）
        self._cache = {}
        
        # 默认权重
        self.default_weights = {
            'technical': 0.20,
            'fundamental': 0.30,
            'sector': 0.15,
            'capital': 0.20,
            'market_comparison': 0.15
        }
    
    def diagnose(self, code: str, use_cache: bool = True) -> DiagnosisReport:
        """
        对单只股票进行综合诊断
        
        Args:
            code: 股票代码 (如: 600519 或 sh.600519)
            use_cache: 是否使用缓存
        
        Returns:
            DiagnosisReport: 完整的诊断报告
        """
        # 处理代码格式
        clean_code = code.split('.')[-1] if '.' in code else code
        
        # 1. 检查缓存
        if use_cache:
            cached = self._get_from_cache(clean_code)
            if cached:
                logger.info(f"从缓存获取诊断报告: {clean_code}")
                return cached
        
        # 2. 获取股票名称
        stock_name = self._get_stock_name(clean_code)
        
        # 3. 并行调用所有分析器
        dimensions = self._run_all_analyzers(clean_code)
        
        # 4. 计算综合评分
        overall_score = calculate_overall_score(dimensions, self.default_weights)
        
        # 5. 生成评级和状态
        overall_rating = get_rating_from_score(overall_score)
        overall_status = get_status_from_score(overall_score)
        
        # 6. 识别优势和劣势
        strengths, weaknesses = self._identify_strengths_weaknesses(dimensions)
        
        # 7. 生成投资建议
        suggestions = self._generate_suggestions(dimensions, overall_score, overall_status)
        
        # 8. 生成综合总结
        summary = self._generate_summary(stock_name, overall_rating, strengths, weaknesses)
        
        # 9. 创建诊断报告
        report = DiagnosisReport(
            code=clean_code,
            name=stock_name,
            overall_score=overall_score,
            overall_rating=overall_rating,
            overall_status=overall_status,
            dimensions=dimensions,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            summary=summary,
            updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 10. 缓存结果
        if use_cache:
            self._save_to_cache(clean_code, report)
        
        logger.info(f"完成诊断: {clean_code} - {stock_name} - 评分: {overall_score}")
        
        return report
    
    def diagnose_batch(self, codes: List[str], use_cache: bool = True, 
                      max_workers: int = 5) -> List[DiagnosisReport]:
        """
        批量诊断（并行处理）
        
        Args:
            codes: 股票代码列表
            use_cache: 是否使用缓存
            max_workers: 最大并行数
        
        Returns:
            List[DiagnosisReport]: 诊断报告列表
        """
        reports = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_code = {
                executor.submit(self.diagnose, code, use_cache): code 
                for code in codes
            }
            
            # 收集结果
            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    report = future.result()
                    reports.append(report)
                except Exception as e:
                    logger.error(f"诊断 {code} 失败: {e}")
        
        return reports
    
    def _run_all_analyzers(self, code: str) -> Dict[str, DimensionAnalysis]:
        """并行运行所有分析器"""
        dimensions = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有分析任务
            futures = {
                'technical': executor.submit(self._run_technical_analysis, code),
                'fundamental': executor.submit(self._run_fundamental_analysis, code),
                'sector': executor.submit(self._run_sector_analysis, code),
                'capital': executor.submit(self._run_capital_analysis, code),
                'market_comparison': executor.submit(self._run_market_comparison, code)
            }
            
            # 收集结果
            for dimension_name, future in futures.items():
                try:
                    result = future.result()
                    if result:
                        dimensions[dimension_name] = result
                except Exception as e:
                    logger.warning(f"{dimension_name} 分析失败: {e}")
        
        return dimensions
    
    def _run_technical_analysis(self, code: str) -> Optional[DimensionAnalysis]:
        """运行技术面分析"""
        try:
            result = self.technical_analyzer.analyze(code)
            return DimensionAnalysis(
                score=result['score'],
                status=result['status'],
                message=result['message'],
                details=result['details']
            )
        except Exception as e:
            logger.error(f"技术面分析失败: {e}")
            return None
    
    def _run_fundamental_analysis(self, code: str) -> Optional[DimensionAnalysis]:
        """运行基本面分析"""
        try:
            result = self.fundamental_analyzer.analyze(code)
            return DimensionAnalysis(
                score=result['score'],
                status=result['status'],
                message=result['message'],
                details=result['details']
            )
        except Exception as e:
            logger.error(f"基本面分析失败: {e}")
            return None
    
    def _run_sector_analysis(self, code: str) -> Optional[DimensionAnalysis]:
        """运行行业面分析"""
        try:
            result = self.sector_analyzer.generate_sector_report(code)
            
            # 转换为标准格式
            score = self._convert_sector_score(result)
            
            return DimensionAnalysis(
                score=score,
                status=result.get('status', 'yellow'),
                message=result.get('message', ''),
                details=result
            )
        except Exception as e:
            logger.error(f"行业面分析失败: {e}")
            return None
    
    def _run_capital_analysis(self, code: str) -> Optional[DimensionAnalysis]:
        """运行资金面分析"""
        try:
            result = self.capital_analyzer.generate_capital_report(code)
            
            # 转换为标准格式
            score = self._convert_capital_score(result)
            
            return DimensionAnalysis(
                score=score,
                status=result.get('status', 'yellow'),
                message=result.get('message', ''),
                details=result
            )
        except Exception as e:
            logger.error(f"资金面分析失败: {e}")
            return None
    
    def _run_market_comparison(self, code: str) -> Optional[DimensionAnalysis]:
        """运行大盘对比分析"""
        try:
            result = self.market_comparison_analyzer.analyze(code, days=30)
            return DimensionAnalysis(
                score=result['score'],
                status=result['status'],
                message=result['message'],
                details=result['details']
            )
        except Exception as e:
            logger.error(f"大盘对比分析失败: {e}")
            return None
    
    def _convert_sector_score(self, result: Dict) -> int:
        """将行业面分析结果转换为0-100评分"""
        status = result.get('status', 'yellow')
        
        # 基于状态给分
        if status == 'green':
            base_score = 75
        elif status == 'yellow':
            base_score = 55
        else:
            base_score = 35
        
        # 基于行业排名调整
        industry_rank = result.get('industry_rank')
        if industry_rank:
            if industry_rank <= 5:
                base_score += 15
            elif industry_rank <= 10:
                base_score += 10
            elif industry_rank <= 20:
                base_score += 5
        
        return max(0, min(100, base_score))
    
    def _convert_capital_score(self, result: Dict) -> int:
        """将资金面分析结果转换为0-100评分"""
        status = result.get('status', 'yellow')
        
        # 基于状态给分
        if status == 'green':
            return 75
        elif status == 'yellow':
            return 55
        else:
            return 35
    
    def _identify_strengths_weaknesses(self, dimensions: Dict[str, DimensionAnalysis]) -> tuple:
        """识别优势和劣势"""
        strengths = []
        weaknesses = []
        
        dimension_names = {
            'technical': '技术面',
            'fundamental': '基本面',
            'sector': '行业面',
            'capital': '资金面',
            'market_comparison': '大盘对比'
        }
        
        for dim_key, dim_analysis in dimensions.items():
            dim_name = dimension_names.get(dim_key, dim_key)
            
            if dim_analysis.score >= 75:
                # 优势
                strengths.append(f"{dim_name}{dim_analysis.message}")
            elif dim_analysis.score < 50:
                # 劣势
                weaknesses.append(f"{dim_name}{dim_analysis.message}")
        
        return strengths, weaknesses
    
    def _generate_suggestions(self, dimensions: Dict[str, DimensionAnalysis], 
                            overall_score: int, overall_status: str) -> List[str]:
        """生成投资建议"""
        suggestions = []
        
        # 1. 基于综合评分的建议
        if overall_score >= 80:
            suggestions.append("综合表现优秀，可以考虑买入或持有")
        elif overall_score >= 65:
            suggestions.append("综合表现良好，适合中长期持有")
        elif overall_score >= 50:
            suggestions.append("综合表现一般，建议观望或小仓位试探")
        else:
            suggestions.append("综合表现较弱，建议回避或减仓")
        
        # 2. 基于技术面的建议
        if 'technical' in dimensions:
            tech = dimensions['technical']
            if tech.score < 50:
                suggestions.append("技术面偏弱，等待技术指标改善后再介入")
            elif tech.details.get('rsi', 50) < 30:
                suggestions.append("RSI超卖，可能存在短期反弹机会")
        
        # 3. 基于基本面的建议
        if 'fundamental' in dimensions:
            fund = dimensions['fundamental']
            if fund.score >= 75:
                suggestions.append("基本面优秀，适合长期投资")
            elif fund.score < 50:
                suggestions.append("基本面较弱，不建议长期持有")
        
        # 4. 基于资金面的建议
        if 'capital' in dimensions:
            cap = dimensions['capital']
            if cap.status == 'red':
                suggestions.append("资金持续流出，注意风险")
            elif cap.status == 'green':
                suggestions.append("资金流入积极，可关注短期机会")
        
        # 5. 基于大盘对比的建议
        if 'market_comparison' in dimensions:
            market = dimensions['market_comparison']
            if market.details.get('relative_strength') == 'strong':
                suggestions.append("相对大盘表现强势，可重点关注")
        
        return suggestions
    
    def _generate_summary(self, stock_name: str, overall_rating: str, 
                         strengths: List[str], weaknesses: List[str]) -> str:
        """生成综合总结"""
        summary_parts = [f"{stock_name}综合评级为{overall_rating}"]
        
        if strengths:
            summary_parts.append(f"主要优势：{strengths[0]}")
        
        if weaknesses:
            summary_parts.append(f"主要风险：{weaknesses[0]}")
        
        # 投资建议
        if overall_rating in ['优秀', '良好']:
            summary_parts.append("建议投资者关注并适时介入")
        elif overall_rating == '一般':
            summary_parts.append("建议投资者谨慎观望")
        else:
            summary_parts.append("建议投资者回避或减仓")
        
        return "。".join(summary_parts) + "。"
    
    def _get_stock_name(self, code: str) -> str:
        """获取股票名称"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT name FROM stock_basic WHERE code = ?"
        cursor.execute(query, (code,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else code
    
    def _get_from_cache(self, code: str) -> Optional[DiagnosisReport]:
        """从缓存获取"""
        if code in self._cache:
            cached_data, timestamp = self._cache[code]
            # 检查是否过期
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
            else:
                # 过期，删除
                del self._cache[code]
        return None
    
    def _save_to_cache(self, code: str, report: DiagnosisReport):
        """保存到缓存"""
        self._cache[code] = (report, datetime.now())
    
    def clear_cache(self, code: Optional[str] = None):
        """清除缓存"""
        if code:
            if code in self._cache:
                del self._cache[code]
                logger.info(f"清除缓存: {code}")
        else:
            self._cache.clear()
            logger.info("清除所有缓存")


if __name__ == "__main__":
    # 测试代码
    engine = StockDiagnosisEngine()
    
    # 测试1: 单股诊断
    print("=== 测试1: 贵州茅台 (600519) ===")
    report = engine.diagnose("600519")
    print(f"股票: {report.name} ({report.code})")
    print(f"综合评分: {report.overall_score}")
    print(f"综合评级: {report.overall_rating}")
    print(f"综合状态: {report.overall_status}")
    print(f"\n各维度评分:")
    for dim_name, dim_analysis in report.dimensions.items():
        print(f"  {dim_name}: {dim_analysis.score}分 - {dim_analysis.message}")
    print(f"\n优势: {report.strengths}")
    print(f"劣势: {report.weaknesses}")
    print(f"建议: {report.suggestions}")
    print(f"总结: {report.summary}")
    
    # 测试2: 批量诊断
    print("\n\n=== 测试2: 批量诊断 ===")
    codes = ["600519", "000001", "000858"]
    reports = engine.diagnose_batch(codes)
    for report in reports:
        print(f"{report.name} ({report.code}): {report.overall_score}分 - {report.overall_rating}")
