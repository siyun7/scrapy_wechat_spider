# -*- coding: utf-8 -*-
import scrapy
import os
import time
from scrapy.conf import settings
from info.items import NewsSpiderItem


class RaoKeSpider(scrapy.Spider):
    name = 'raoke'

    allowed_domains = ['www.raoke.net']
    # start_urls = ['http://www.raoke.net/f_93_1.shtml']
    start_urls = ['http://www.raoke.net/forum.php?mod=forumdisplay&fid=93&filter=author&orderby=dateline&page=1']
    # base_url = 'http://www.raoke.net/f_93_'
    base_url = 'http://www.raoke.net/forum.php?mod=forumdisplay&fid=93&filter=author&orderby=dateline&page='
    domian = 'http://www.raoke.net/'
    domian_len = len(domian)

    path = os.path.dirname(__file__)

    def parse(self, response):
        last_page = int(response.xpath('//a[@class="last"]/text()').extract()[0].split(" ")[1])
        last_page = 10
        for i in range(1, last_page):
            # url = self.base_url + str(i) + '.shtml'
            url = self.base_url + str(i)
            yield scrapy.Request(url, self.parse_raoke_news_list)

    def parse_raoke_news_list(self, response):
        normal_thread_hrefs = response.xpath('//tbody[contains(@id,"normalthread")]//a[@class="xi2"]/@href').extract()
        for normal_thread_href in normal_thread_hrefs:
            yield scrapy.Request(normal_thread_href, self.parse_news)

    def parse_news(self, response):

        content_element = '//div[@id="postlist"]/div[1]//td[@class="t_f"]'
        content = response.xpath(content_element)

        images_urls = response.xpath(content_element + '//img[@class="zoom"]/@zoomfile').extract()
        images_index = 0

        title = response.xpath('//span[@id="thread_subject"]/text()').extract()[0].strip(' ')
        url = response.xpath('//link[@rel="canonical"]/@href').extract()[0].strip(' ')
        author = response.xpath('//a[@class="xi2"]/text()').extract()[0].strip(' ')
        type = 1
        source = '饶客网'
        status = 0

        publish_time = response.xpath('//em[contains(@id,"authorposton")]/text()').extract()[0].split('于')[1].strip(' ')
        created_at = updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        news_id = url[self.domian_len:].strip(' ').strip('.shtml')
        imgs_urls = []

        content_nodes = content.extract()
        content_str = content.xpath('string(.)').extract()
        text = ""

        for line in content_nodes[0].splitlines():
            # line = "".join(line.split())
            if line == '':
                continue
            if self.allowed_domains[0] in line or '下载附件' in line or '保存到相册' in line or '上传' in line or '.com' in line or '.net' in line or '.cn' in line:
                continue
            if 'ignore_js_op' in line:
                line = line.replace('ignore_js_op', 'div')

            if '/static/image/common/none.gif' in line:
                image_name = images_urls[images_index].split('/')[-1]

                if settings['DEV'] == 1:
                    web_domain = settings['DEV_WEB_DOMAIN']
                else:
                    web_domain = settings['PRO_WEB_DOMAIN']

                image_path = web_domain + news_id + '/'
                img_url = image_path + image_name
                line = line.replace('/static/image/common/none.gif', image_path + image_name)
                imgs_urls.append(img_url)
                images_index += 1

            text += line

        item = NewsSpiderItem()
        item['news_id'] = news_id
        item['title'] = title
        item['text'] = text
        item['imgs'] = imgs_urls[0:3]
        item['images'] = images_urls
        item['author'] = author
        item['source'] = source
        item['type'] = type
        item['status'] = status
        item['publish_time'] = publish_time
        item['created_at'] = created_at
        item['updated_at'] = updated_at
        yield item
