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
from productor import Saver


class Callfunc(object):
    def default_func(self,testdata):
        '''
        默认方法，不选择自定义运行方法时调用
        :param testdata:
        :return:
        '''
        PostWithFunctions(testdata).test_start()


