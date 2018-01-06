# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import ConfigParser
from weibospider.Pedoo import Pedoo


class WeibospiderPipeline(object):
    """ data pipline """

    def __init__(self):
        configreader = ConfigParser.ConfigParser()
        configreader.read("scrapy.cfg")
        mysqlconfig = {}

        for config in configreader.items('mysql'):
            mysqlconfig[config[0]] = config[1]

        self.mysql = Pedoo(mysqlconfig)

    def process_item(self, item, spider):
        return item