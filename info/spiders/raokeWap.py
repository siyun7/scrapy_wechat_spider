# -*- coding: utf-8 -*-
import scrapy
import os
import time
import re
import requests
from scrapy.conf import settings
from info.items import NewsSpiderItem


class RaoKeWapSpider(scrapy.Spider):
    name = 'raokeWap'

    allowed_domains = ['www.raoke.net']
    # start_urls = ['http://www.raoke.net/f_93_1.shtml']
    start_urls = ['http://www.raoke.net/forum.php?mod=forumdisplay&fid=93&mobile=1&orderby=dateline&page=1']
    # base_url = 'http://www.raoke.net/f_93_'
    base_url = 'http://www.raoke.net/forum.php?mod=forumdisplay&fid=93&mobile=1&orderby=dateline&page='
    domian = 'http://www.raoke.net/'
    domian_len = len(domian)

    path = os.path.dirname(__file__)

    def parse(self, response):
        last_page = (response.xpath('//a[@class="last"]/text()').extract())
        last_page = 20
        for i in range(1, last_page):
            # url = self.base_url + str(i) + '.shtml'
            url = self.base_url + str(i)
            yield scrapy.Request(url, self.parse_raoke_news_list)

    def parse_raoke_news_list(self, response):
        page_num = int(response.xpath('//input[@name="custompage"]/@value').extract()[0])
        if page_num == 1:
            normal_thread_hrefs = response.xpath('//div[@class="bm_c bt"]/following-sibling::*/a/@href').extract()
        else:
            normal_thread_hrefs = response.xpath('//div[@class="bm_c"]/a/@href').extract()

        for normal_thread_href in normal_thread_hrefs:
            normal_thread_href = self.domian + normal_thread_href
            # normal_thread_href = "http://www.raoke.net/forum.php?mod=viewthread&tid=99964&extra=&mobile=1"
            yield scrapy.Request(normal_thread_href, self.parse_news)

    def parse_news(self, response):

        content_element = '//div[@class="postmessage"]'
        content = response.xpath(content_element)

        images_tmp_urls = response.xpath(content_element + '//a/@href').extract()
        images_urls = []
        for images_tmp_url in images_tmp_urls:
            if "attachment" in images_tmp_url:
                images_urls.append(images_tmp_url)
        images_index = 0

        title = response.xpath('//title/text()').extract()[0].split(' ')[0].strip(' ')
        url = response.xpath('//a[@id="thread_subject"]/@href').extract()[0]
        author = response.xpath('//div[@class="bm_user"][1]/a/text()').extract()[0].strip(' ')
        type = 'raoke'
        source = '饶客网'
        status = 0

        publish_time = response.xpath('//font[@class="xs0 xg1"][1]/text()').extract()[0].strip(' ')
        created_at = updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if settings['DEV'] == 1:
            web_domain = settings['DEV_WEB_DOMAIN']
        else:
            web_domain = settings['PRO_WEB_DOMAIN']

        common_style = web_domain + "style.css"

        url_params = url.split('&')
        for url_param in url_params:
            if 'tid' in url_param:
                news_id = url_param.split("=")[1] + '_1_1'
        imgs_urls = []

        content_nodes = content.extract()[0]
        content_nodes = content_nodes.replace("<font", "<span")
        content_nodes = content_nodes.replace("style=", "style-old=")
        content_nodes = content_nodes.replace("color=", "color-old=")
        content_nodes = content_nodes.replace("size=", "size-old=")
        content_nodes = content_nodes.replace("</font>", "</span>")
        content_nodes = content_nodes.replace("><", ">\n<")
        content_str = content.xpath('string(.)').extract()

        # text = '<html xmlns="http://www.w3.org/1999/xhtml">' \
        #        '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">' \
        #        '<meta http-equiv="Cache-control" content="no-cache">' \
        #        '<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">' \
        #        '<meta name="format-detection" content="telephone=no">' \
        #        '<link rel="stylesheet" href="' + common_style + '" type="text/css" media="all"></head><body>'
        text = ''

        for line in content_nodes.splitlines():
            # line = "".join(line.split())
            if line == '</iframe>':
                continue
            if line == '':
                continue
            if '本帖最后由' in line:
                line = '<div class=postmessage>'
            if '<iframe' in line:
                url_pattern = r'.+?src="(\S+)"'  # url的正则式

                try:
                    iframe_url = re.findall(url_pattern, line)[0]
                except Exception as e:
                    print(e)
                    continue
                iframe_url = iframe_url.replace("amp;", "")
                req = requests.get(iframe_url)
                req_content = req.content.decode(encoding='utf-8')
                # iframe_pattern = '<iframe(.*?)><\/iframe>'
                iframe_pattern = '<iframe[^>]*?(?:\/>|>[^<]*?<\/iframe>)'
                try:
                    iframe_tag = re.findall(iframe_pattern, req_content)[0]
                except Exception as e:
                    print(e)
                    continue
                ori_height = 'height="240px"'
                height = 'height="440px"'
                iframe_tag = iframe_tag.replace("height=240", "height=440")
                iframe_tag = iframe_tag.replace(ori_height, height)
                # iframe_tag = iframe_tag.replace("/iframe/player", "/txp/iframe/player")
                line = iframe_tag
            if 'attachment' in line:
                image_name = images_urls[images_index].split('/')[-1]
                image_path = web_domain + news_id + '/'
                img_url = image_path + image_name
                line = '<img src="' + img_url + '" title="' + image_name + '">'
                imgs_urls.append(img_url)
                images_index += 1
            if 'forum.php' in line:
                continue

            text += line
        # text += '</body></html>'
        item = NewsSpiderItem()
        item['news_id'] = news_id
        item['title'] = title
        item['text'] = text
        item['imgs'] = imgs_urls[0:3]
        item['images'] = images_urls
        item['author'] = author
        item['source'] = source
        item['origin_url'] = response.url
        item['type'] = type
        item['status'] = status
        item['publish_time'] = publish_time
        item['created_at'] = created_at
        item['updated_at'] = updated_at
        yield item
