"""
Flask应用主入口
"""
from flask import Flask
from flask_cors import CORS
import os
import logging

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置
    app.config['JSON_AS_ASCII'] = False  # 支持中文
    app.config['JSON_SORT_KEYS'] = False
    
    # CORS配置
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # 日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 注册蓝图
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from src.web.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 全局错误处理器
    from src.web.utils.errors import APIError
    from src.web.utils.response import error_response
    
    @app.errorhandler(APIError)
    def handle_api_error(e):
        """处理自定义API错误"""
        return error_response(e.message, e.error_code, e.status_code)
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return error_response('资源未找到', 'NOT_FOUND', 404)
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.error(f'Internal server error: {str(e)}', exc_info=True)
        return error_response('服务器内部错误', 'INTERNAL_ERROR', 500)
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # 不处理HTTP异常，让Flask默认处理
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return e
        
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return error_response('服务器内部错误', 'INTERNAL_ERROR', 500)
    
    @app.route('/')
    def index():
        return {'message': 'TradingBuddy API Server', 'version': '1.0.0'}
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
