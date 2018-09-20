# -*- coding: utf-8 -*-

import time
import datetime


def get_second_long(time_str=None):
    if time_str is None:
        return long(time.time())
    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return long(time.mktime(time_array))


def get_curtime_str():
    return datetime.datetime.now()


def get_curtimestamp():
    return int(time.time() * 1000)


def get_curdatetime_format():
    return get_curtime_str().strftime("%Y-%m-%d %H:%M:%S")


def get_curdate_format():
    return get_curtime_str().strftime("%Y-%m-%d")


def get_curmonth_format():
    return get_curtime_str().strftime("%Y-%m")


def get_curhour_str():
    return get_curtime_str().hour


def get_curminuter_str():
    return get_curtime_str().minute


def get_curday_str():
    return get_curtime_str().day


def get_curdate_str():
    return get_curtime_str().strftime("%Y%m%d")


def get_curdatetime_str():
    return get_curtime_str().strftime("%Y%m%d%H%M%S")


def get_curminuter_str():
    return get_curtime_str().strftime("%Y%m%d%H%M")





