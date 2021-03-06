from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import generate_csrf
from flask import Flask, g,render_template

import logging
from flask_session import Session
from config import Config, Development, Production, config_map
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# from info.untils.common import user_login_data

logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

# 创建mysql数据库对象
db = SQLAlchemy()
store_redis = None  # type:redis.StrictRedis


def create_app(config):
    config = config_map.get(config)
    # 创建flask对象
    app = Flask(__name__)
    # 从对象加载配置
    app.config.from_object(config)
    # 初始化数据库
    db.init_app(app)
    # 创建redis对象
    global store_redis
    store_redis = redis.StrictRedis(host=Config.REDIS_IP, port=Config.REDIS_PORT, decode_responses="True")
    CSRFProtect(app)
    # 设置Session
    Session(app)

    # 开启CSRF保护，避免视图函数收到攻击
    @app.after_request
    def after_request(response):
        # 调用函数生成 csrf_token
        csrf_token = generate_csrf()
        # 通过 cookie 将值传给前端
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 不存在的页面都指向404页面
    from info.untils.common import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(error):
        user = g.user
        data = {"user_info": user.to_dict() if user else None}
        return render_template('news/404.html', data=data)


    # 导入自定义过滤器，并添加到模版中
    from info.untils.common import do_classindex, do_data_cid
    app.add_template_filter(do_classindex, "class_index")
    app.add_template_filter(do_data_cid, "class_name")

    from .index import index_blu
    app.register_blueprint(index_blu)

    from .passport import passport_blu
    app.register_blueprint(passport_blu)

    from .news import news_blue
    app.register_blueprint(news_blue)

    return app
