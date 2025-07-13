# config.py

class Config:
    SECRET_KEY                = 'test2335'  # 生产环境请改为强随机值
    SQLALCHEMY_DATABASE_URI   = 'mysql+pymysql://app_user:secure_password@localhost/psych_eval'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY            = 'your_jwt_secret'        # JWT 用密钥
    JWT_ACCESS_TOKEN_EXPIRES  = 3600                     # 令牌过期时间（秒）

    CORS_ORIGINS              = ['http://localhost:5173']  # 允许跨域的前端地址
