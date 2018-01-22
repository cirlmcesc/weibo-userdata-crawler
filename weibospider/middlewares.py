# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

""" middlewares """

import random
import logging
import redis
import json
import os
import ConfigParser
from weibospider.useragents import useragents
from weibospider.WeiboCookies import getAllAccountsCookies, resetCookies, removeCookies
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from scrapy.exceptions import IgnoreRequest


logger = logging.getLogger(__name__)
configreader = ConfigParser.ConfigParser()
configreader.read("scrapy.cfg")

class UserAgentMiddleware(object):
    """ 随机更换User-Agent """

    def process_request(self, request, spider):
        """ process request """

        request.headers["User-Agent"] = random.choice(useragents)

class CookiesMiddleware(object):
    """ 维护登录cookie """

    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)
        self.rconn = redis.Redis(configreader.get('redis', 'hosts'), configreader.get('redis', 'port'))
        getAllAccountsCookies(self.rconn)

    @classmethod
    def from_crawler(cls, crawler):
        """ from crawler """

        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        """ process request """

        accountcookies = self.rconn.keys()

        if accountcookies > 0:
            account = random.choice(accountcookies)

            if "Spider:Cookies" in account:
                request.cookies = json.loads(self.rconn.get(account))
                request.meta["accounttext"] = account.split("Cookies:")[-1]

    def process_repsonse(self, request, response, spider):
        """ process response """

        if response.status in [300, 301, 302, 303]:
            redirect_url = response.headers["location"]

            try:
                redirect_url = response.headers["location"]

                if "login.weibo" in redirect_url or "login.sina" in redirect_url:  # Cookie失效
                    logger.warning("One Cookie need to be updating...")
                    resetCookies(self.rconn, request.meta['accountText'])
                elif "weibo.cn/security" in redirect_url:  # 账号被限
                    logger.warning("One Account is locked! Remove it!")
                    removeCookies(self.rconn, request.meta["accountText"])
                elif "weibo.cn/pub" in redirect_url:
                    logger.warning("Redirect to 'http://weibo.cn/pub'!( Account:%s )" % request.meta["accountText"].split("--")[0])

                reason = response_status_message(response.status)

                return self._retry(request, reason, spider) or response  # 重试
            except Exception, e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            logger.error("%s! Stopping..." % response.status)
            os.system("pause")
        else:
            return response
