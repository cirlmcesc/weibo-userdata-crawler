# -*- coding: utf-8 -*-

""" weibo login """

import json
import os
import logging
import requests
from weibospider.WeiboAccounts import accounts


logger = logging.getLogger(__name__)

def getCookies(username, password):
    """ 单个账号登录 """

def getAllAccountsCookies(rconn):
    """ 将所有账号登录后把cookies存入reids """

    for account in accounts:
        key, username, password = "Spider:Cookies:%s--%s" % (account[0], account[1]), account[0], account[1]

        if rconn.get(key) is None:
            rconn.set(key), getCookies(username, password)

    if "".join(rconn.keys()).count("Spider:Cookies") == 0:
        logger.warning('None cookies, Stopping...')
        os.system("pause")

def resetCookies(rconn, accounttext):
    """ 重新获取cookies """

    username = accounttext.split("--")[0]
    password = accounttext.split("--")[1]
    rconn.set("Spider:Cookies:%s" % accounttext, getCookies(username, password))
    logger.warning("The cookie of %s has been updated successfully !" % accounttext)

def removeCookies(rconn, accounttext):
    """ 删除cookies """

    rconn.delete("Spider:Cookies:%s" % accounttext)
    logger.warning("The cookie of %s has been deleted successfully !" % accounttext)
