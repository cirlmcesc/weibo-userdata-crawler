# -*- coding: utf-8 -*-

""" weibo spider """

import scrapy
import requests
import re
import datetime
import logging


class WeiboSpider(scrapy.Spider):
    """ weibo spider """

    name = 'weiboSpider'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['http://m.weibo.cn/']
    logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

    def parse(self, response):
        """ parse func """
        print response
