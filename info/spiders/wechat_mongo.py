import scrapy
from scrapy import Request
import pymongo
import base64
import time
import re
import requests
from scrapy.conf import settings
from info.items import WechatSpiderItem


class WechatMongoSpider(scrapy.Spider):
    name = 'wechat_mongo'

    allowed_domains = ["mp.weixin.qq.com"]
    start_urls = ['https://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd']

    cookie = "rewardsn=; wxtokenkey=777; wxuin=483682415; devicetype=Windows10; version=62060426; lang=zh_CN; pass_ticket=eBjsgmUiPiBamdRCtpXQ+evK4PYQcrjC84pgB5pN6SyGk1kIW8TAX/BXWUOvCF8S; wap_sid2=CO/Q0eYBElw3T2ZMaGtmWlBxbnotSDhoX3U3WUV6MHVrRGhFOG92NGY2SGg2U1g1VzlSYjVJS29ERndHT2wyZlBPUzRKX3lKWlVKQ3ZWc3VQOXR4ZU5HRjBmM2h1dEFEQUFBfjCdwLLdBTgNQAE="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/69.0.3497.100 Safari/537.36",
        "Cookie": cookie
    }

    test_url = "https://mp.weixin.qq.com/s?__biz=MjM5MDQ4MzU5NQ==&mid=2658974975&idx=1&sn=3dde7fcdc4d36df940dee6b0683a003f&chksm=bdcc091b8abb800dbd39ef74b824e055a6a9dfbebcf90a8d7a9741b4d20b672f7aa98df00636#rd"

    # 获取数据库连接信息
    host = settings['MONGO_HOST']
    port = settings['MONGO_PORT']
    dbname = settings['MONGO_WECHAT_DB']
    client = pymongo.MongoClient(host=host, port=port)
    # 定义数据库
    db = client[dbname]
    table = db[settings['MONGO_WECHAT_TABLE']]
    datas = table.find({"usage": 0}).limit(10).skip(0)

    def start_requests(self):
        for data in self.datas:
            url = data["url"]
            # time.sleep(1)
            try:
                yield Request(url=url, dont_filter=True, callback=self.parse,
                              headers=self.headers)
            except Exception as e:
                print(e)
                continue

    def parse(self, response):

        # 获取数据库连接信息
        host = settings['MONGO_HOST']
        port = settings['MONGO_PORT']
        dbname = settings['MONGO_WECHAT_DB']
        client = pymongo.MongoClient(host=host, port=port)
        # 定义数据库
        db = client[dbname]
        table = db[settings['MONGO_WECHAT_TABLE']]

        if settings['DEV'] == 1:
            web_domain = settings['DEV_WEB_DOMAIN']
        else:
            web_domain = settings['PRO_WEB_DOMAIN']

        item = WechatSpiderItem()
        url_parse = response.url.split("&", 3)
        if len(url_parse) < 3:
            print(response.url)
            table.delete_one({"url": response.url})
            return

        biz = url_parse[0].replace('https://mp.weixin.qq.com/s?__biz=', '')
        mid = url_parse[1].replace('mid=', '')
        idx = url_parse[2].replace('idx=', '')
        str = biz+'_'+mid+'_'+idx
        news_id = base64.b64encode(str.encode("utf-8"))
        news_id_str = news_id.decode("utf-8")
        content_list = response.xpath('//div[@id="js_content"]').extract()
        if len(content_list) == 0:
            table.delete_one({"_id": news_id_str})
            return
        content = content_list[0]

        content = content.replace("data-src=", "src=")
        content = content.replace("style=", "old-style=")
        try:
            title = response.xpath('//h2[@id="activity-name"]/text()').extract()[0].strip("")
        except Exception as e:
            print(e)
            table.delete_one({"_id": news_id_str})
            return
        author = response.xpath('//a[@id="js_name"]/text()').extract()[0].strip("")
        title = "".join(title.split())

        origin_imgs = response.xpath('//div[@id="js_content"]//img/@data-src').extract()
        imgs = []
        for img in origin_imgs:
            if "mmbiz.qpic.cn" in img:
                params = img.split('mmbiz.qpic.cn/')[1].split('/')
                img_params0_sp = params[0].split('_')
                if len(img_params0_sp) == 2:
                    img_name = params[1] + "." + params[0].split('_')[1]
                else:
                    img_name = params[1] + "." + "jpg"
                img_path = web_domain + news_id_str + "/" + params[0] + "/" + img_name
                if "jpg" in img_path:
                    imgs.append(img_path)
            else:
                continue
        # content = content.replace("https://mmbiz.qpic.cn/", web_domain+news_id.decode("utf-8")+"/")
        content = content.replace("><", ">\n<")
        html = ""
        for line in content.splitlines():
            if line.strip() == '':
                continue
            if "https://v.qq.com/iframe/preview.html" in line:
                iframe_heights = re.findall("height=[\d]+", line)
                iframe_heights = ' '.join(iframe_heights)
                iframe_heights = iframe_heights.split("=")
                try:
                    iframe_height = iframe_heights[1]
                except Exception as e:
                    print(e)
                    iframe_height = "500"

                iframe_widths = re.findall("width=[\d]+", line)
                iframe_widths = ' '.join(iframe_widths)
                origin_i_w = iframe_widths
                iframe_widths = iframe_widths.split("=")
                try:
                    iframe_width = iframe_widths[1]
                except Exception as e:
                    print(e)
                    iframe_width = "375"

                iframe_style = "width:100%;height:"+iframe_height+"px;"

                line = line.replace("<iframe", "<iframe style="+iframe_style)
                line = line.replace("https", "http")
                line = line.replace(origin_i_w, "width=100%25")

            if "<img" in line and "mmbiz.qpic.cn" in line:
                matches = re.findall(r'\ssrc="([^"]+)"', line)
                matches = ' '.join(matches)
                if matches.strip() == '':
                    continue
                try:
                    tag_params = matches.split('mmbiz.qpic.cn/')[1].split('/')
                except Exception as e:
                    exit(e)
                    continue
                tag_params0_sp = tag_params[0].split('_')
                if len(tag_params0_sp) == 2:
                    tag_name = tag_params[1] + "." + tag_params[0].split('_')[1]
                else:
                    tag_name = tag_params[1] + "." + "jpg"
                tag_url = web_domain + news_id_str + "/" + tag_params[0] + "/" + tag_name
                line = line.replace(matches, tag_url)
                if "data-w" in line:
                    data_w = re.findall('data-w="[\d]+"', line)
                    if len(data_w) == 1:
                        data_w = ' '.join(data_w)
                        tmp = data_w.split("data-w=")
                        data_ws = eval(tmp[1])
                        if int(data_ws) <= 100:
                            line = line.replace('<img', '<img style="display:none;"')

            html += line

        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        type = "wechat"
        status = 0
        item['news_id'] = news_id_str
        item['title'] = title
        item['text'] = html
        item['imgs'] = imgs[0:3]
        item['images'] = origin_imgs
        item['author'] = "".join(author.split())
        item['source'] = "".join(author.split())+"公众号"
        item['origin_url'] = response.url
        item['type'] = type
        item['status'] = status
        item['publish_time'] = date
        item['created_at'] = date
        item['updated_at'] = date
        yield item


