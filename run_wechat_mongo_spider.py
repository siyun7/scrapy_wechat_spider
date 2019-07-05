from scrapy import cmdline

cmd_str = 'scrapy crawl wechat_mongo'
cmdline.execute(cmd_str.split(' '))
