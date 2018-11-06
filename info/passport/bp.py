import random
import re

from info.lib.yuntongxun.SMS import CCP
from info.models import User
from . import passport_blu
from flask import current_app, jsonify
from flask import make_response
from flask import request

from info import constants
from info import store_redis
from info.untils.captcha.captcha import captcha
from info.untils.response_code import RET


@passport_blu.route("/image_code")
def get_image_code():
    #  1. 获取到当前的图片编号id
    code_id = request.args.get("code_id")
    # 2. 生成验证码
    name, text, image = captcha.generate_captcha()
    # 把验证码保存到redis数据库里面
    try:
        # redis数据库对象   （"ImageCode_" + code_id = key ）
        # code_id,constants.IMAGE_CODE_REDIS_EXPIRES = (过期时间)
        # store_redis.set("ImageCode_" + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        store_redis.setex("ImageCode_" + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    resp = make_response(image)
    # 设置返回内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@passport_blu.route("/smscode")
def send_sms():
    """
    1. 接收参数并判断是否有值
    2. 校验手机号是正确
    3. 通过传入的图片编码去redis中查询真实的图片验证码内容
    4. 进行验证码内容的比对
    5. 生成发送短信的内容并发送短信
    6. redis中保存短信验证码内容
    7. 返回发送成功的响应
    :return:
    """
    # 1. 接收参数并判断是否有值
    # 取到请求值中的内容
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")

    if not all([mobile, image_code_id, image_code]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 校验手机号是正确
    if not re.match("^1[3-9]\\d{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")

    # 3. 通过传入的图片编码去redis中查询真实的图片验证码内容
    try:
        real_image_code = store_redis.get("ImageCode_" + image_code_id)
        # 如果能够取出来值，删除redis中缓存的内容
        if real_image_code:
            real_image_code = real_image_code.decode()
            store_redis.delete("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        # 获取图片验证码失败
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码失败")
    # 3.1 判断验证码是否存在，已过期
    if not real_image_code:
        # 验证码已过期
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    # 4. 进行验证码内容的比对
    if image_code.lower() != real_image_code.lower():
        # 验证码输入错误
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 4.1 校验该手机是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if user:
        # 该手机已被注册
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")

    # 5. 生成发送短信的内容并发送短信
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.debug("短信验证码的内容：%s" % sms_code)
    result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    if result != 0:
        # 发送短信失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 6. redis中保存短信验证码内容
    try:
        store_redis.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 7. 返回发送成功的响应
    return jsonify(errno=RET.OK, errmsg="发送成功")
