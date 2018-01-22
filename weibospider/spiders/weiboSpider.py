# -*- coding: utf-8 -*-

""" weibo spider """

import logging
import scrapy
from weibospider.bloggerid import BLOGGER_ID as blogger_ids
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.http import HtmlResponse


logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

class WeiboSpider(scrapy.Spider):
    """ weibo spider """

    name = 'WeiboSpider'
    allowed_domains = ['weibo.com']
    start_urls = []
    blogger_ids = blogger_ids

    def start_requests(self):
        """ 发起请求 """

        for uid in self.blogger_ids:
            yield Request(
                url="https://weibo.com/u/%s" % uid,
                callback=self.parse_bloggerinformation,
            )

    def parse_bloggerinformation(self, response):
        """ 分析博主, 找到置顶帖 """
        print response.xpath("//html").extract()

    def parse_comment(self, response):
        """ 抓取评论 """

    def parse_information(self, response):
        """ 抓取用户信息 """