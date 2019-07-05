# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    desc = scrapy.Field()


class NewsSpiderItem(scrapy.Item):
    news_id = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    imgs = scrapy.Field()
    images = scrapy.Field()
    author = scrapy.Field()
    source = scrapy.Field()
    type = scrapy.Field()
    status = scrapy.Field()
    publish_time = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    origin_url = scrapy.Field()


class TitleSpiderItem(scrapy.Item):
    title = scrapy.Field()
    time = scrapy.Field()
    url = scrapy.Field()


class WechatSpiderItem(scrapy.Item):
    news_id = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    imgs = scrapy.Field()
    images = scrapy.Field()
    author = scrapy.Field()
    source = scrapy.Field()
    type = scrapy.Field()
    status = scrapy.Field()
    publish_time = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    origin_url = scrapy.Field()


class GetSessionSpiderItem(scrapy.Item):
    biz = scrapy.Field()
    wap_sid2 = scrapy.Field()
