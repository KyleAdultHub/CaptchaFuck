# -*- coding: utf-8 -*-
import socket


def get_host_name():
    hostname = socket.gethostname()
    return hostname


def get_local_ip():
    try:
        ip = ([(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
               [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
        return ip
    except:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("baidu.com", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            pass
    return None


HOST_NAME = get_host_name()
LOCAL_IP = get_local_ip()

