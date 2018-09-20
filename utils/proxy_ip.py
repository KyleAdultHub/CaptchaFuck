# -*- coding: utf-8 -*-
import json
import random
import re
import requests
from redis import *
import time


class ProxyProducer(object):
    def __init__(self, host=None, proxy_key=None, passwd=None, db=0, port=6379):
        if host:
            self.proxy_key = proxy_key
            try:
                self.cursor = StrictRedis(host=host, password=passwd, db=db, port=port)
                self.cursor.delete(proxy_key)
            except Exception as e:
                print(u'Failed to initialize a redis_proxy_pool, {}'.format(e))

    def get_proxy_5u(self, order):
        """
        无忧代理，获取结果为单个代理 XX.XX.XX.XX:80
        """
        api = u'http://api.ip.data5u.com/dynamic/get.html?order={}&ttl=1&sep=3'.format(order)
        while True:
            try:
                response = requests.get(api).content.decode()
                if not re.search(r'too many requests', response):
                    response_ip = response.split('\n')[0].split(',')[0]
                    return response_ip
                time.sleep(3)
            except Exception as e:
                print(u'Failed to get proxy_ip from 《5u》:{}'.format(e))
                time.sleep(100)
                continue

    def get_proxy_mimvp(self, order, scheme='HTTP', number=500):
        """
        米扑代理，需要文件作为中间件，获取代理的结果为 XX.XX.XX.XX:80
        返回列表，列表中包含所有提取到的代理ip
        """
        scheme = 2 if scheme == 'HTTPS' else 1
        api = u'https://proxyapi.mimvp.com/api/fetchopen.php?orderid={}&num={}&country_group=1&http_type={}&anonymous=5&request_method=2&result_fields=1,2&result_format=json'.format(order, number, scheme)
        result_list = []
        while True:
            try:
                response = requests.get(api)
                if re.search(r'result', response.content.decode(), re.S):
                    ip_list = json.loads(response.content.decode())[u'result']
                    if ip_list:
                        for ip_dict in ip_list:
                            if ip_dict:
                                result_list.append(ip_dict[u'ip:port'])
                        return result_list
            except Exception as e:
                print(u'Failed to get proxy_ip from 《mimvp》:{}'.format(e))
                time.sleep(200)
                continue

    def get_proxy_qiproxy(self, url):
        """
        从公司代理池获取ip
        """
        result_list = []
        while True:
            try:
                response = requests.get(url)
                if re.search(r'20000', response.content.decode(), re.S):
                    ip_list = json.loads(response.content.decode(u'utf-8'))[u'data'][u'ips']
                    if ip_list:
                        for ip_dict in ip_list:
                            if ip_dict:
                                result_list.append(ip_dict[u'ip'] + ":" + str(ip_dict[u'port']))
                        return result_list
            except Exception as e:
                print(u'Failed to get proxy_ip from 《qi_proxy》:{}'.format(e))
                time.sleep(20)
                continue

    def _get_proxy_from_redis(self):
        """
        从redis的队列中取出一条代理ip，阻塞模式 (set类型)
        """
        try:
            ip_port = self.cursor.spop(self.proxy_key).decode()
            return ip_port
        except Exception as e:
            print(u'Failed to get a ip from the redis queue {}'.format(e))
            return None

    def _put_proxy_into_redis(self, ip_port):
        """
        将一个ip字符串推入到redis中(set 类型)
        """
        try:
            self.cursor.sadd(self.proxy_key, ip_port)

        except Exception as e:
            print(u'Failed to insert a ip into the redis queue {}'.format(e))

    def get_proxy_redis_by_mivip(self, order, scheme='HTTP', number=500):
        """
        从redis中获取代理，返回的格式为:XX.XX.XX.XX:80
        """
        get_by_mimvp = False
        while True:
            try:
                proxy_pool_length = self.cursor.scard(self.proxy_key)
            except Exception as e:
                print(u'Failed to get the number from the redis queue {}'.format(e))
                time.sleep(60 * 2)
                continue
            if proxy_pool_length > 5:  # 从代理队列中取出一条数据返回
                return self._get_proxy_from_redis()
            else:
                if get_by_mimvp:
                    get_by_mimvp = False
                    # 调用接口获取
                    ip_list = self.get_proxy_mimvp(order, scheme=scheme, number=number)
                    if ip_list:
                        for ip in ip_list:
                            self._put_proxy_into_redis(ip)
                        continue
                else:
                    time.sleep(random.randint(0, 10))
                    get_by_mimvp = True
                    continue

    def get_proxy_redis_by_qiproxy(self, api):
        """从redis中获取代理ip，返回给爬虫"""
        get_by_qiproxy = False
        while True:
            try:
                proxy_pool_length = self.cursor.scard(self.proxy_key)
            except Exception as e:
                print(u'Failed to get the number from the redis queue {}'.format(e))
                time.sleep(60*2)
                continue
            if proxy_pool_length > 5:
                # 从代理队列中取出一条数据返回
                return self._get_proxy_from_redis()
            else:
                if get_by_qiproxy:
                    get_by_qiproxy = False
                    # 调用接口获取
                    ip_list = self.get_proxy_qiproxy(api)
                    if ip_list:
                        for ip in ip_list:
                            self._put_proxy_into_redis(ip)
                        continue

                else:
                    time.sleep(random.randint(0, 10))
                    get_by_qiproxy = True
                    continue


if __name__ == '__main__':
    proxy_producer = ProxyProducer("127.0.0.1", proxy_key="test", passwd=None, db=0, port=6379)
    while True:
        print(proxy_producer.get_proxy_redis_by_qiproxy(u"http://10.0.110.228:9105/proxyGateway/getIp?user=wenshu&count=100"))
        time.sleep(2)