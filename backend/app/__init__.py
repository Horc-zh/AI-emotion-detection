# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 全局实例化扩展（不绑定任何 app）
db      = SQLAlchemy()    # ORM 实例
migrate = Migrate()       # 迁移工具实例
jwt     = JWTManager()    # JWT 管理器实例


def create_app(config_object: str = 'config.Config') -> Flask:
    """应用工厂：创建并配置 Flask 实例"""
    # 1. 创建 Flask 实例
    app = Flask(__name__)
    # 2. 加载配置
    app.config.from_object(config_object)

    # 3. 绑定并初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(
        app,
        origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
        supports_credentials=True,
        automatic_options=True
    )  # 允许跨域并携带 Cookie

    # 4. 注册认证蓝图（登录、注册）
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 5. 注册其他功能蓝图
    from .routes.chat     import chat_bp
    from .routes.survey   import survey_bp
    from .routes.image    import image_bp
    from .routes.evaluate import evaluate_bp

    app.register_blueprint(chat_bp,       url_prefix='/api/chat')
    app.register_blueprint(survey_bp,     url_prefix='/api/survey')
    app.register_blueprint(image_bp,      url_prefix='/api/image')
    app.register_blueprint(evaluate_bp,   url_prefix='/api/evaluate')

    return app
