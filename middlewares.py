# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

""" middlewares """

import random
from useragents import AGENTS as agents


class RequestMiddleware():
    """ 请求中间件 """

    headers = {}

    def __init__(self):
        """ init """

        self.headers = self._choiceRandomUserAgent()

    def _choiceRandomUserAgent(self):
        """ process request """

        return random.choice(agents)

class ResponseMiddleware():
    """ 返回中间件 """

    def __init__(self):
        """ init """

        pass

    def processResponse(self):
        """ process response """

        pass
