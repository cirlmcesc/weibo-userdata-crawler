# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeibospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BloggerItem(scrapy.Item):
    uid = scrapy.Field()
    nickname = scrapy.Field()

class InformationItem(scrapy.Item):
    uid = scrapy.Field()
    nickname = scrapy.Field()

class CommentItem(scrapy.Item):
    uid = scrapy.Field()
    bloggerid = scrapy.Field()
    comment_content = scrapy.Field()
