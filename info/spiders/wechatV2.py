import requests
import time
import json
import scrapy
from scrapy import Request

class WechatSpiderV2(scrapy.Spider):
    name = 'wechatV2'
    allowed_domains = ["mp.weixin.qq.com"]
    start_urls = ['https://mp.weixin.qq.com/cgi-bin/appmsg']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'pgv_pvid=9683465940; RK=XbQFHwZkdv; ptcz=bcf105c75a473964ad70b25949aff639801d1245c27816622fc55cfeeee4c075; tvfe_boss_uuid=c607a1bab633771e; pgv_pvi=8448654336; eas_sid=m1x5R2W1y136P6b4G9H5q4A4x1; pac_uid=1_527030700; msuid=jhsr7fso7kvv3igalc5sfkw9ijv3r2vxalaly9ot; _ga=amp-PDuiFkVU5YnCPjPA0TPSNg; noticeLoginFlag=1; ptui_loginuin=2856445454; pt2gguin=o0527030700; o_cookie=527030700; luin=o0527030700; lskey=00010000b59c7bcc45dc285202644ecb3dd95c6bc7e332cae8ff7a505dbf1289bbc746c9ebd3bce7d409122e; rewardsn=; pgv_info=ssid=s4746941888; pgv_si=s5878515712; _qpsvr_localtk=0.4797875074302642; ptisp=ctc; uin=o0527030700; skey=@u7jAg0PMk; IED_LOG_INFO2=userUin%3D527030700%26nickName%3DJulius%26userLoginTime%3D1537855453; sig=h0186d2bc8a00b162af930963357da9cb79c6a683e183b2f2250f255c65a3ec99c12c7d896368190f6a; wxtokenkey=777',
        'DNT': 1,
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': 1,
        'Referer': 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=python&ie=utf8&_sug_=n&_sug_type_=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    searchURl = "http://weixin.sogou.com/weixin?type=1&s_from=input&query={keyword}&ie=utf8&_sug_=n&_sug_type_="
    wechatPub = []
    wechatID = []

    def start_requests(self):
        # keyword = input("关键词输入:")
        keyword = 'python'
        yield Request(url=self.searchURl.format(keyword=keyword), dont_filter=True, callback=self.parse,
                      headers=self.headers)

    def parse(self, response):
        pass
