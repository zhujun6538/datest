"""
@project: datest
@author: MZM
@file: callfunc.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：不选择自定义运行方法时调用默认方法仅发送当前数据的请求，可添加供选择的自定义方法进行复杂的自定义流程
"""

import json
import time
from httpfunc import PostWithFunctions
from loguru import logger
from productor import Saver
from database import getSqldata


class Callfunc(object):
    def default_func(self,testdata):
        '''
        默认方法，不选择自定义运行方法时调用
        :param testdata:
        :return:
        '''
        PostWithFunctions(testdata).test_start()

    def adduser(self,testdata):
        PostWithFunctions(testdata).test_start()
        db = getSqldata(host='140.143.4.104',
                        port=3306,
                        user='shopxo',
                        password='z111111',
                        database='shopxo',
                        charset="utf8")
        username = Saver.hist[testdata['caseno']]['requestdata']['username'][1]
        sql = f"select id from s_user where username = \"{username}\""
        id = db.query(sql)[0][0]
        Saver.save_data('id',id)
        db.conn.close()

