# -*- coding:utf-8 -*-
import argparse
from EngTextCaptcha.cnn.cnn_lenet import main
from EngTextCaptcha.meta import ModelConfig


def train(meta):
    main(meta)


if __name__ == "__main__":
    meta = None
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m', '--meta',
        default='test',
        type=str,
        help='choose the meta config name that have set in the meta.py .')
    Flag, unparsed = parser.parse_known_args()
    try:
        meta = ModelConfig[Flag.meta]
    except:
        print('can not find meta name of %s from meta.py.' % Flag.meta)
        exit(1)
    train(meta)