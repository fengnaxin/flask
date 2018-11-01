from . import passport_blu
from flask import current_app, jsonify
from flask import make_response
from flask import request

from info import constants
from info import store_redis
from info.untils.captcha.captcha import Captcha
from info.untils.response_code import RET
from . import passport_blu


@passport_blu.route("/")
def get_image_code():
    #  1. 获取到当前的图片编号id
    code_id = request.args.get("code_id")
    # 2. 生成验证码
    name, text, image = Captcha.generate_captcha()
    # 把验证码保存到redis数据库里面
    try:
        # redis数据库对象   （"ImageCode_" + code_id = key ）
        # code_id,constants.IMAGE_CODE_REDIS_EXPIRES = (过期时间)
        store_redis.setex("ImageCode_" + code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    resp = make_response(image)
    # 设置返回内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
