import scrapy
import random
from scrapy import log
import requests
import re
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware


class ProxyHttpRequest(HttpProxyMiddleware):

    def __init__(self, ip=""):
        self.ip = ip
        # ip_poll_url = 'http://www.66ip.cn/mo.php?sxb=%D6%D0%B9%FA&tqsl=10&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea='
        # ip_poll_url = 'https://proxyapi.mimvp.com/api/fetchopen.php?orderid=864070911814155014&num=20&http_type=1&ping_time=0.3&transfer_time=1&result_fields=1,2'
        # ip_poll_url = 'https://ltq.im/wp-content/uploads/2018/02/ips.txt'
        ip_poll_url = 'http://39.108.140.232:7070/get/'
        r = requests.get(ip_poll_url)
        p = r'(?:((?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5]))\D+?(6[0-5]{2}[0-3][0-5]|[1-5]\d{4}|[1-9]\d{1,3}|[0-9]))'
        p1 = r'\d+.\d+.\d+.\d+:+\d+'
        self.ip_list = re.findall(p1, r.text)
        print(self.ip_list)

    def process_request(self, request, spider):
        ip = random.choice(self.ip_list)
        print("Now Ip is:" + ip)
        request.meta["proxy"] = "http://" + ip
