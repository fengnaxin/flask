from info import constants, db
from info.models import News, User, Comment, CommentLike
from info.untils.common import user_login_data
from . import news_blue
from flask import render_template, session, current_app, g, request, jsonify
from info.untils.response_code import RET


@news_blue.route("comment_like", methods=["POST", "GET"])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    news_id = request.json.get(" news_id")

    if not all([news_id, action, comment_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not action in ("add", "remove"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论数据不存在")
    #  判断点击事件是不是添加点赞
    if action == "add":
        comment_like = CommentLike.query.filter(Comment.comment_id == comment_id, Comment.user_id == user.id).first()

        # 如果为空，则是用户第一次点这条评论
        if not comment_like:
            comment_like = CommentLike()
            comment_like.id= comment_id
            comment_like.user_id = user.id
            comment_like.like_count +=1
            db.session.add(comment_like)

    else:
        comment_like = CommentLike.query.filter(Comment.comment_id == comment_id,Comment.user_id == user.id).first()
        if comment_like:
            db.session.delete(comment_like)
            comment_like.like_count -= 1
    db.session.commit()
    return jsonify(errno=RET.OK,errmsg="OK")




@news_blue.route("news_comment", methods=["POST", "GET"])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    news_id = request.json.get("news_id")
    comment = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    if not all([news_id, comment]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")
    comments = Comment()
    comments.user_id = user.id
    comments.news_id = news_id
    comments.content = comment
    if parent_id:
        comments.parent_id = parent_id

    # 保存到数据库
    try:
        db.session.add(comments)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comments.to_dict())


@news_blue.route("/news_collect", methods=["POST"])
@user_login_data
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="请登录用户")
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="新闻id参数错误")
    if not action in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="动作参数错误")
    try:
        new = News.query.get(news_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not new:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")
    if action == "collect":

        user.collection_news.append(new)
    else:
        user.collection_news.remove(new)
    try:

        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 登录网页详情
@news_blue.route("/<int:news_id>")
@user_login_data
def new_detail(news_id):
    news = News.query.order_by(News.clicks).limit(constants.CLICK_RANK_MAX_NEWS)

    news_content = News.query.get(news_id)
    user = g.user
    # user_id = session.get("user_id")
    # user = None
    # # 判断用户是否登录
    # if user_id:
    #     try:
    #         # 通过user_id获取到用户的所有信息
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    # 默认收藏为false
    is_collected = False
    if user:
        if news_content in user.collection_news:
            is_collected = True

    new_list = list()
    for temp in news:
        new_list.append(temp.to_dict())

    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()

    except Exception as e:
        current_app.logger.error(e)
    # comments_list = [comment.to_dict() for comment in comments]
    comments_list = list()

    for comment in comments:
        comment_dict = comment.to_dict()
        comments_list.append(comment_dict)


    data = {
        "user_info": user.to_dict() if user else None,
        "click_new_list": new_list,
        "is_collected": is_collected,
        "news": news_content,
        "comments": comments_list
    }

    return render_template("news/detail.html", data=data)
