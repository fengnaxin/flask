import logging
from info.models import News
from info import constants
from info.models import User, Category
from info.untils.response_code import RET
from . import index_blu
from flask import render_template, current_app, session, request,jsonify


@index_blu.route("/news_list")
def new_list():
    cid = request.args.get("cid", 1)
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(page)
    except Exception as e:
        cid = 1
        page = 1
        per_page = 10
    if cid == 1:
        paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
    # 查询出来的数据
    items = paginate.items
    # 数据的总页数
    total_page = paginate.pages
    # 获取到当前页
    current_page = paginate.page
    news_li = list()
    for item_temp in items:
        news_li.append(item_temp.to_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_li": news_li
    }

    return jsonify(errno=RET.OK,errmsg="ok",data=data)


@index_blu.route("/")
def index():
    # logging.debug("This is a debug log.")
    # logging.info("This is a info log.")
    # logging.warning("This is a warning log.")
    # logging.error("This is a error log.")
    # logging.critical("This is a critical log.")
    # return render_template("news/index.html")
    # 获取当前用户id
    user_id = session.get("user_id")
    user = None
    # 判断用户是否登录
    if user_id:
        try:
            # 通过user_id获取到用户的所有信息
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 首页最多点赞多新闻
    news = News.query.order_by(News.clicks).limit(constants.CLICK_RANK_MAX_NEWS)

    new_list = list()
    for temp in news:
        new_list.append(temp)
    # 首页标题
    category = Category.query.all()

    category_list = []

    for temp in category:
        category_list.append(temp.to_dict())



    data = {
        "user_info": user.to_dict() if user else None,
        "click_new_list": new_list,
        "categories": category_list
    }

    return render_template("news/index.html", data=data)


"""
    如果不用装饰器的话可以用这下面这句，直接调
    index_blu.add_url_rule("/", "index", index)
"""


@index_blu.route("/favicon.ico")
def favicon():

    return current_app.send_static_file("news/favicon.ico")
