import re, random, string
from flask import request, current_app, make_response, jsonify, session,render_template

from info.passport import passport_blu
from info.untils.response_code import RET
from info import store_redis, db
from info.models import User
from info.untils.captcha.captcha import captcha
from info.lib.yuntongxun.sms import CCP
from info import constants
from datetime import datetime


@passport_blu.route("/logout")
def logout():
    session.pop("user_id",None)
    session.pop("nick_name",None)
    session.pop("mobile",None)
    return jsonify(errno=RET.OK, errmsg="OK")


@passport_blu.route("/login", methods=["GET", "POST"])
def login():
    mobile = request.json.get("mobile")
    print(mobile)
    password = request.json.get("password")
    # 获取数据库手机号码
    user = User.query.filter(User.mobile == mobile).first()
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    # 获取到与手机号码匹配的密码 user.check_password(password)
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")
    # 保存用户登录信息
    last_login = datetime.now()
    db.session.commit()
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route("/register", methods=["GET", "POST"])
def register():
    mobile = request.json.get("mobile")
    smscode = request.json.get("smscode")
    password = request.json.get("password")
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的参数")
    real_sms_code = store_redis.get("smscode_" + mobile)
    if not real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码已经过期")

    if smscode != real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的短信验证码")
    #
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    db.session.add(user)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route("/image_code", methods=["GET", "POST"])
def get_code():
    # 1 获取到当前图片的uuid
    code_id = request.args.get("code_id")
    # 2 生成验证码
    name, text, image = captcha.generate_captcha()
    print("图片验证码为", text)

    try:
        # 3 把生成的验证码保存到redis数据库，过期时间为IMAGE_CODE_REDIS_EXPIRE = 300s
        #   key为"ImageCode_" + code_id，value为text
        store_redis.setex("ImageCode_" + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg="图片保存是失败"))
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'

    return resp


@passport_blu.route("/sms_code", methods=["GET", "POST"])
def sms_code():
    mobile = request.json.get("mobile")
    image_code = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的参数")

    if not re.match(r"^1[3-9]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的手机号")
    # 获取redis的值的类型为byte类型，前端获取到的值是字符串类型，不能比较
    # 需要在创建store_redis象的第三个参数设置为decode_responses="True
    #  redis.StrictRedis(host=Config.REDIS_IP, port=Config.REDIS_PORT,decode_responses="True")
    real_image_code = store_redis.get("ImageCode_" + image_code_id)
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")
    # lower(),忽略用户输入大小写问题
    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的图片验证码")

    result = random.randint(0, 999999)
    smscode = "%06d" % result
    store_redis.setex("smscode_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, smscode)
    print(smscode)
    # status_code = CCP().send_template_sms(mobile, [send_msg_code, 3], 1)
    # print(status_code)
    # if status_code == -1:
    #     return jsonify(errno=RET.THIRDERR, errmsg="第三方错误")

    return jsonify(errno=RET.OK, errmsg="短信发送成功")
