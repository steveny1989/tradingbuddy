"""
A股选股应用主入口
"""
from flask import Flask, render_template
from flask_cors import CORS
from routes import api
from database import DatabaseManager
import os

app = Flask(__name__)
CORS(app)

# 注册蓝图
app.register_blueprint(api)

# 确保data目录存在
if not os.path.exists('data'):
    os.makedirs('data')


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

