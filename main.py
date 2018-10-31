from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import redis
import pymysql
pymysql.install_as_MySQLdb()
from flask_migrate import Migrate, MigrateCommand
from flask_wtf import CSRFProtect
from flask_session import Session
# 创建flask对象
app = Flask(__name__)
# 创建角本对象
manger = Manager(app)


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/test20"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 设置redis主机
    REDIS_IP = "localhost"
    REDIS_PORT = 6379
    # 设置密钥
    SECRET_KEY = "dsdsdsdsd"
    # 设置session的类型redis，用redis存session的值
    SESSION_TYPE = "redis"
    # 使用session的签名
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT)
    # 设置session的有效期 单位为秒
    SESSION_PERMANENT = 86400


# 从对象加载配置
app.config.from_object(Config)
# 创建mysql数据库对象
db = SQLAlchemy(app)
# 创建redis对象
store_redis = redis.StrictRedis(host=Config.REDIS_IP, port=Config.REDIS_PORT)
# 开启CSRF保护，避免视图函数收到攻击
CSRFProtect(app)
# 设置Session
Session(app)
# 创建数据库迁移对象
Migrate(app, db)
manger.add_command("main", MigrateCommand)


@app.route("/")
def index():
    return "index222"


if __name__ == '__main__':
    manger.run()
