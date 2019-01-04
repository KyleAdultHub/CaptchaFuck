# coding=utf-8
from io import BytesIO
from flask import Flask, request
from PIL import Image
from uuid import uuid4
from EngTextCaptcha.meta import ModelConfig
from utils.log import Logger
from EngTextCaptcha.crack import crack_captcha
from flask.json import jsonify
from copy import deepcopy
import os

app = Flask(__name__)
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log", "app")
logger = Logger(__file__, log_dir)

logger.logger.info('start app for EngTextCaptcha project.')


class Msg(object):

    NO_USER = {"status": "error", "reason": "user not found"}
    NO_IMG = {"status": "error", "reason": "no image"}
    INVALID_IMG = {"status": "error", "reason": "Image invalid"}
    SERVER_ERROR = {"status": "error", "reason": "server error"}
    SUCCESS = {"status": "success"}

    @classmethod
    def no_user(cls, data=""):
        msg = deepcopy(cls.NO_USER)
        msg.update({"data": data})
        return msg

    @classmethod
    def no_img(cls, data=""):
        msg = deepcopy(cls.NO_IMG)
        msg.update({"data": data})
        return msg

    @classmethod
    def invalid_img(cls, data=""):
        msg = deepcopy(cls.INVALID_IMG)
        msg.update({"data": data})
        return msg

    @classmethod
    def server_error(cls, data=""):
        msg = deepcopy(cls.SERVER_ERROR)
        msg.update({"data": data})
        return msg

    @classmethod
    def success(cls, data=""):
        msg = deepcopy(cls.SUCCESS)
        msg.update({"data": data})
        return msg


@app.route('/captcha/crack', methods=['GET', 'POST'])
def captcha_crack():
    user = request.args.get('user')
    if not ModelConfig.get(user):
        logger.logger.info('/captcha/crack: can not find user of {}.'.format(user))
        return jsonify(Msg.no_user())
    image = request.get_data()
    if image is None or image == "":
        logger.logger.info('/captcha/crack:receive wrong data of image None.'.format(user))
        return jsonify(Msg.no_img())
    try:
        img = Image.open(BytesIO(image))
    except:
        logger.logger.info('/captcha/crack:receive wrong data of image, the bytes data can not trans to Image obj.'.format(user))
        return jsonify(Msg.invalid_img())
    try:
        text = crack_captcha(ModelConfig[user], img)
        logger.logger.info('/captcha/crack:successfully crack captcha for {}.'.format(text))
        return jsonify(Msg.success(text))
    except Exception as e:
        logger.logger.info('/captcha/crack:Failed to crack captcha, the server has some error.'.format(e))
        return jsonify(Msg.server_error())


@app.route('/captcha/save', methods=['POST'])
def save_captcha():
    user = request.args.get('user')
    img_text = request.args.get('text')
    test_data = request.args.get('test')
    if not ModelConfig.get(user):
        logger.logger.info('/captcha/save: can not find user of {}.'.format(user))
        return jsonify(Msg.no_user())
    image = request.get_data()
    if image is None or image == "":
        logger.logger.info('/captcha/save: receive wrong data of image None.'.format(user))
        return jsonify(Msg.no_img())
    try:
        Image.open(BytesIO(image))
    except:
        logger.logger.info('/captcha/save: receive wrong data of image, the bytes data can not trans to Image obj.'.format(user))
        return jsonify(Msg.invalid_img())
    try:
        if not test_data:
            img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", user, "img_train")
        else:
            img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", user, "img_test")
        img_file_name = os.path.join(img_dir, img_text + "_" + str(uuid4()) + ".png")
        with open(img_file_name, 'wb') as f:
            f.write(image)
        logger.logger.info('/captcha/save: successfully save captcha for {}.'.format(img_text))
        return jsonify(Msg.success())
    except Exception as e:
        logger.logger.info('/captcha/save: Failed to save captcha, the server has some error.'.format(e))
        return jsonify(Msg.server_error())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=11005)