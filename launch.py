# -*- coding: utf-8 -*-

""" start up from cmdline  """

from scrapy import cmdline


cmdline.execute("scrapy crawl weiboSpider".split())
