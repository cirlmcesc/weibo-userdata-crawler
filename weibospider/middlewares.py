# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

""" middlewares """

import random
import logging
from weibospider.useragents import AGENTS as agents


LOGGER = logging.getLogger(__name__)

class UserAgentMiddleware(object):
    """ 随机更换User-Agent """

    def process_request(self, request, spider):
        """ process request """

        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
