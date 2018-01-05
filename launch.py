# -*- coding: utf-8 -*-

""" start up """

from WeiboSpider import WeiboSpider
from commentid import COMMENT_ID as c_ids
from bloggerid import BLOGGER_ID as b_ids

def setUp():
    """ 运行 """

    for cid in c_ids:
        WeiboSpider.process_comment(cid)

if __name__ == '__main__':
    setUp()
