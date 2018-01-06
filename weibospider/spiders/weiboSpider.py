# -*- coding: utf-8 -*-

""" weibo spider """

import logging
import scrapy
from weibospider.bloggerid import BLOGGER_ID as blogger_ids
from scrapy.http import Request


logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

class WeiboSpider(scrapy.Spider):
    """ weibo spider """

    name = 'WeiboSpider'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['http://m.weibo.cn/']
    blogger_ids = blogger_ids

    def start_requests(self):
        """ 发起请求 """

        for uid in self.blogger_ids:
            yield Request(
                url="https://weibo.cn/%s/info" % uid,
                callback=self.parse_bloggerinformation,
                meta={'blogger_id': uid}
            )

    def parse_bloggerinformation(self, response):
        """ 分析博主, 找到置顶帖 """

        print 123123123
        exit()

    def parse_comment(self, response):
        """ 抓取评论 """

        pass

    def parse_information(self, response):
        """ 抓取用户信息 """

        pass