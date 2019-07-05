#encoding=utf-8
import scrapy
from info.items import NewsSpiderItem
import json
import time
class TouTiaoSpider(scrapy.Spider):

    name = 'toutiao'
    allowed_domains = ["toutiao.com"]
    start_urls = ['http://toutiao.com/articles_news_society/p1']
    base_class_url = 'http://toutiao.com/articles_news_society'
    base_url = 'http://toutiao.com'
    maxpage = 5
    category = [
        'articles_news_society',
        # 'articles_news_entertainment',
        # 'articles_movie', 'articles_news_tech', 'articles_digital',
        # 'articels_news_sports', 'articles_news_finance', 'articles_news_military',
        # 'articles_news_culture', 'articles_science_all'
    ]

    def parse(self, response):
        for ctg in self.category:
            for page in range(0, self.maxpage):
                url = self.base_url + '/' + ctg + '/p' + str(page)
                yield scrapy.Request(url, self.parseNewsHref)

    def parseNewsHref(self, response):
        urls = response.xpath("//h2//a/@href").extract()
        for url in urls:
            newsUrl = self.base_url + url
            print(newsUrl)
            yield scrapy.Request(newsUrl, self.parseNews)

    def parseNews(self, response):
        item = NewsSpiderItem()
        jsStr = response.xpath("/html/body/script[4]/text()").extract()[0]
        jsStr = jsStr.strip(';').strip('var BASE_DATA = ').strip(' ')
        articleInfoFlag = 0
        for line in jsStr.splitlines():
            line = line.strip(' ').strip('{\'').strip(',')
            if line.find('articleInfo') != -1:
                articleInfoFlag = 1

            if articleInfoFlag == 1:
                if line.find('title') != -1:
                    title = line[6:]
                    print(title)

                if line.find('content') != -1:
                    content = line[8:]
                    print(content)

                if line.find('time') != -1:
                    tm = line[5:]
                    print(tm)

                if line.find('has_extern_link') != -1:
                    articleInfoFlag = 0
                    break


        # title = articles.xpath("/h1[@class='article-title']").extract()
        # tm = articles.xpath("//div[@class='article-sub']/span[2]").extract()
        # content = articles.xpath("//div[@class='article-content']").extract()

        if len(title) != 0 and len(tm) != 0 and len(content) != 0:
            item['title'] = title
            item['time'] = tm
            item['url'] = response.url
            cc = ''
            if len(content) != 0:
                # for c in content:
                #     cc = cc+c+'\n'
                # item['content'] = cc
                item['content'] = content
                yield item

    def printC(self, text):
        for t in text:
            print(t.encode('utf-8'))
