from flask import session, current_app,g

from info.models import User
import functools


def do_classindex(index):
    if index == 1:
        return "first"
    if index == 2:
        return "second"
    if index == 3:
        return "third"


def do_data_cid(index):
    if index == 0:
        return "active"


def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id")
        user = None
        # 判断用户是否登录
        if user_id:
            try:
                # 通过user_id获取到用户的所有信息
                user = User.query.get(user_id)
                g.user = user
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args,**kwargs)
    return wrapper
