"""
@project: datest
@author: MZM
@file: testapi.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：pytest测试脚本文件
"""

import os
import time
import allure
import pytest
from productor import *
from callfunc import *
import logging

filepath = os.path.dirname(__file__)


class Test_Openapi(object):
    @pytest.mark.work
    def test_api(self, testdata):
        '''
        测试脚本
        :param testdata:
        :return:
        '''
        # 进行测试报告分组
        allure.dynamic.link(testdata['caselink'],name=testdata['casename'])
        allure.dynamic.feature(testdata['suitename'])
        allure.dynamic.story(testdata['group'])
        allure.dynamic.title(testdata['casename'])
        time.sleep(testdata['sleeptime'])
        # 可运行自定义方法
        try:
            Callfunc().__getattribute__(testdata['callfunc'])(testdata)
        except Exception as e:
            logging.info(str(e))
            raise e



# if __name__=="__main__":
#     pytest.main(['-v'])



