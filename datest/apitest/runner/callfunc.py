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

import jsonpath

from httpfunc import PostWithFunctions
from productor import Saver


class Callfunc(object):
    def default_func(self,testdata):
        '''
        不选择自定义运行方法时调用此默认方法
        :param testdata:
        :return:
        '''
        # 使用根据输入值构建的对象发送请求数据、进行前置后置处理，根据断言校验响应报文等
        PostWithFunctions(testdata).test_start()

    def yb(self,testdata):
        '''
        自定义测试方法，可自己添加
        :param testdata:
        :return:
        '''
        testdata1 = testdata.copy()
        testdata2 = testdata.copy()
        testdata1['asserts'] = [['assert_equal', 'body.resultCode', '00000'], ['assert_equal', 'body.resultDesc', '成功']]
        PostWithFunctions(testdata1).run()
        orderno = f"&$.{Saver.caseno}..orderNo&"
        testdata2['data'] = eval(Saver.handle_params('{"orderNo":"%s"}' % (orderno)))
        testdata2['url'] = testdata2['url'].replace('Apply', 'Result')
        for i in range(3):
            try:
                time.sleep(1)
                PostWithFunctions(testdata2).run()
                break
            except Exception as e:
                if i == 2:
                    raise e
            # if jsonpath.jsonpath(Saver.httphist,):
            #     break