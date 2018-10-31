from flask import Flask
from flask_session import Session
from config import Config, Developement, Production, config_map
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
# 创建mysql数据库对象
db = SQLAlchemy()


def create_app(config):
    config = config_map.get(config)
    # 创建flask对象
    app = Flask(__name__)
    # 从对象加载配置
    app.config.from_object(config)
    # 初始化数据库
    db.init_app(app)
    # 创建redis对象
    store_redis = redis.StrictRedis(host=Config.REDIS_IP, port=Config.REDIS_PORT)
    # 开启CSRF保护，避免视图函数收到攻击
    CSRFProtect(app)
    # 设置Session
    Session(app)
    from .index import index_blu
    app.register_blueprint(index_blu)
    return app
