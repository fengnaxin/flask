import redis
from flask import logging


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:@127.0.0.1:3306/information_20"
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


# 开发模式
class Development(Config):
    DEBUG = True
    # LOG_LEVEL = logging.DEBUG


# 上线模式
class Production(Config):
    DEBUG = False
    # LOG_LEVEL = logging.ERROR


config_map = {
    "develop": Development(),
    "production": Production()
}
