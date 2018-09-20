# -*- coding: utf-8 -*-
import logging
from .localhost import get_local_ip
from .date import get_curdate_format
from .file import check_file_path
import os
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    def __init__(self, name, log_folder=""):
        self.log_folder = log_folder
        self.cur_day = get_curdate_format()
        self.name = name
        self.logger = logging.getLogger(name)
        self.formatter = self.get_formatter()
        self.file_holder = self.get_file_handler()
        self.stream_handler = self.get_stream_handler()
        self.setting_logger()

    def check_file_path(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

    @staticmethod
    def get_formatter():
        return logging.Formatter('%(asctime)s : %(name)s : %(levelname)s :[%(lineno)d]: %(message)s')

    @staticmethod
    def get_stream_handler():
        return logging.StreamHandler()  # log输入到控制台的等级开关

    def get_file_handler(self):
        self.check_file_path()
        file_name = self.log_folder + "/ip_{}_pid_{}".format(get_local_ip(), os.getpid())
        file_handler = TimedRotatingFileHandler(filename=file_name, when="D", interval=1, backupCount=7)
        file_handler.suffix = "%Y-%m-%d.log"
        return file_handler

    def setting_logger(self):
        self.logger.setLevel(logging.DEBUG)
        self.file_holder.setLevel(logging.INFO)
        self.file_holder.setFormatter(self.formatter)
        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_holder)
        self.logger.addHandler(self.stream_handler)

    def __del__(self):
        self.file_holder.close()
        self.stream_handler.close()


if __name__ == '__main__':
    pass