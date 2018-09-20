# -*- coding:utf-8 -*-
import os
import shutil
import uuid
from EngTextCaptcha.cnn.base import get_choices
from captcha.image import ImageCaptcha
import itertools


def _gen_captcha(img_dir, num_per_image, n, width, height, choices):
    """
    :param img_dir: 目录位置,相对于databases的位置
    :param num_per_image: 每个验证码图片的元素数量
    :param n: 生成多少个epoch的图片
    :param width: 图片的宽
    :param height: 图片的高
    :param choices: 图片的元素可选范围集合
    :return:
    """
    if os.path.exists(img_dir):
        shutil.rmtree(img_dir)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    image = ImageCaptcha(width=width, height=height)

    print('generating %s epoches of captchas in %s' % (n, img_dir))
    for _ in range(n):
        for i in itertools.permutations(choices, num_per_image):
            captcha = ''.join(i)
            fn = os.path.join(img_dir, '%s_%s.png' % (captcha, uuid.uuid4()))
            image.write(captcha, fn)


def build_file_path(x, img_dir):
    return os.path.join(img_dir, x)


def gen_dataset(meta):
    CAPTCHA_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'databases')
    img_dir = os.path.join(CAPTCHA_BASE_DIR, meta[u"name"])
    n_epoch = meta.get("epochs", 1)
    num_per_image = meta.get("npi", 1)
    choices = get_choices(meta.get("choice", ["digit"]))
    width = meta["width"]
    height = meta["height"]
    print('%s choices: %s' % (len(choices), ''.join(choices) or None))
    _gen_captcha(build_file_path('img_train', img_dir), num_per_image, n_epoch, width, height, choices=choices)
    _gen_captcha(build_file_path('img_test', img_dir), num_per_image, max(1, int(n_epoch/10)), width, height, choices=choices)
