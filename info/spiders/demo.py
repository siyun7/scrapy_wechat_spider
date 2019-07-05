# -*- coding: utf-8 -*-
import scrapy
from info.items import InfoItem

class DemoSpider(scrapy.Spider):
    name = 'demo'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/chart']

    def parse(self, response):
        print('start crawl sites douban.com');
        courses = response.xpath('//div[@class="indent"]//table')
        for course in courses:
            item = InfoItem();
            item['name'] = course.xpath('.//div[@class="pl2"]//a/text()').extract_first().replace("\n", "").replace(' ', '').strip('/')
            item['desc'] = course.xpath('.//p[@class="pl"]/text()').extract_first().strip()
            yield item
