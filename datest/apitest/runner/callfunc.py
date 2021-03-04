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


class Callfunc(object):
    def default_func(self,testdata):
        '''
        默认方法，不选择自定义运行方法时调用
        :param testdata:
        :return:
        '''
        PostWithFunctions(testdata).test_start()

    def yb(self,testdata):
        '''
        自定义测试方法，可自己添加
        :param testdata:
        :return:
        '''
        testdata1 = testdata.copy()
        testdata2 = testdata.copy()
        testdata1['asserts'] = [['eq', 'body.resultCode', '00000'], ['eq', 'body.resultDesc', '成功']]
        PostWithFunctions(testdata1).run()
        orderno = f"&$.{Saver.caseno}..orderNo&"
        testdata2['data'] = Saver.handle_params('{"orderNo":"%s"}' % (orderno))
        testdata2['url'] = testdata2['url'].replace('Apply', 'Result')
        issuc = False
        for i in range(3):
            time.sleep(2)
            issuc = PostWithFunctions(testdata2).run()
            if issuc:
                break