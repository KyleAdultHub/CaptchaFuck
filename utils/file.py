# -*- coding: utf-8 -*-

import os


def check_file_path(filename):
    """
    检测文件上级目录是否存在，不存在则创建
    """
    filepath = os.path.dirname(filename)
    if not os.path.exists(filepath):
        os.makedirs(filepath)


def get_dir_files(dir_path):
    if not isinstance(dir_path, str):
        dir_path = dir_path
    for root, dirs, files in os.walk(dir_path):
        for fl in files:
            yield os.path.join(root, fl)


def read_file(filename, mode="r"):
    with open(filename, mode) as f:
        content = f.read()
        f.close()
        return content


def read_lines(filename, mode="r"):
    with open(filename, mode) as f:
        lines = f.readlines()
        f.close()
        return (line.strip() for line in lines)


def write_file(filename, content="", mode="w"):
    with open(filename, mode) as f:
        f.write(content.encode("utf-8"))
        f.close()


def write_lines(filename, lines=None, mode="w"):
    if lines is None:
        lines = []
    with open(filename, mode) as f:
        f.writelines(["%s\n" % line.encode("utf-8") for line in lines])
        f.close()
