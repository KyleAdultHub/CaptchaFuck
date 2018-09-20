import argparse
from EngTextCaptcha.cnn.cnn_lenet import crack
from EngTextCaptcha.meta import ModelConfig
from PIL import Image


def crack_captcha(meta, img):
    text = crack(meta, img)
    return text


if __name__ == "__main__":
    meta = None
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m', '--meta',
        default='test',
        type=str,
        help='choose the meta config name that have set in the meta.py .')
    parser.add_argument(
        '-f', '--file_path',
        type=str,
        help='the path of image captcha.')
    Flag, unparsed = parser.parse_known_args()
    try:
        meta = ModelConfig[Flag.meta]
    except:
        print('can not find meta name of %s from meta.py.' % Flag.file_path)
        exit(1)
    if not Flag.file_path:
        print('the path of image captcha must input')
        exit(1)
    crack_captcha(meta, Image.open(Flag.file_path))