"""
个股诊断 API 路由
"""
from flask import Blueprint, jsonify, request
from src.data.database import StockDatabase
from src.business.diagnosis import StockDiagnosisEngine
from src.web.utils.errors import APIError
import logging

logger = logging.getLogger(__name__)

diagnosis_bp = Blueprint('diagnosis', __name__, url_prefix='/api/diagnosis')

# 初始化数据库和诊断引擎
db = StockDatabase("data/a_share.db")
diagnosis_engine = StockDiagnosisEngine(data_fetcher=db)


@diagnosis_bp.route('/<code>', methods=['GET'])
def diagnose_stock(code):
    """
    诊断单只股票
    
    Args:
        code: 股票代码（支持 sh.600000 或 600000 格式）
        
    Returns:
        JSON: 诊断报告
    """
    try:
        logger.info(f"诊断股票: {code}")
        
        # 调用诊断引擎
        report = diagnosis_engine.diagnose_stock(code)
        
        # 转换为 JSON 格式
        result = {
            'code': report.code,
            'name': report.name,
            'current_price': report.current_price,
            'change_pct': report.change_pct,
            'overall_score': report.overall_score,
            'technical_score': {
                'value': report.technical_score.value,
                'reasons': report.technical_score.reasons
            },
            'liquidity_score': {
                'value': report.liquidity_score.value,
                'reasons': report.liquidity_score.reasons
            },
            'market_score': {
                'value': report.market_score.value,
                'reasons': report.market_score.reasons
            },
            'signal_light': {
                'color': report.signal_light.color,
                'label': report.signal_light.label,
                'confidence': report.signal_light.confidence,
                'reason': report.signal_light.reason
            },
            'risk_info': {
                'current_price': report.risk_info.current_price,
                'stop_loss_price': report.risk_info.stop_loss_price,
                'stop_loss_pct': report.risk_info.stop_loss_pct,
                'take_profit_price': report.risk_info.take_profit_price,
                'take_profit_pct': report.risk_info.take_profit_pct,
                'risk_reward_ratio': report.risk_info.risk_reward_ratio,
                'volatility': report.risk_info.volatility,
                'risk_level': report.risk_info.risk_level,
                'warnings': report.risk_info.warnings
            },
            'diagnosis_text': report.diagnosis_text,
            'disclaimer': report.disclaimer,
            'data_source': report.data_source,
            'data_coverage': report.data_coverage,
            'data_update_time': report.data_update_time.strftime('%Y-%m-%d') if report.data_update_time else None,
            'timestamp': report.timestamp.isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"诊断失败: {code}, 错误: {e}")
        return jsonify({
            'error': str(e),
            'code': code
        }), 400


@diagnosis_bp.route('/search', methods=['GET'])
def search_stocks():
    """
    搜索股票（支持代码和名称模糊搜索）
    
    Query params:
        q: 搜索关键词
        
    Returns:
        JSON: 股票列表
    """
    try:
        keyword = request.args.get('q', '').strip()
        
        logger.info(f"搜索股票: keyword='{keyword}'")
        
        if not keyword:
            logger.info("搜索关键词为空")
            return jsonify({'stocks': []})
        
        # 从数据库搜索
        stocks = db.get_stock_list()
        logger.info(f"数据库中共有 {len(stocks)} 只股票")
        
        # 模糊匹配
        keyword_upper = keyword.upper()
        matched = stocks[
            stocks['code'].str.contains(keyword_upper, case=False, na=False) |
            stocks['name'].str.contains(keyword, case=False, na=False)
        ]
        
        logger.info(f"匹配到 {len(matched)} 只股票")
        
        # 限制返回数量
        matched = matched.head(10)
        
        result = []
        for _, row in matched.iterrows():
            result.append({
                'code': row['code'],
                'name': row['name'],
                'market': row.get('market', '')
            })
        
        logger.info(f"返回 {len(result)} 只股票")
        return jsonify({'stocks': result})
        
    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
