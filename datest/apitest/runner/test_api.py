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
        allure.dynamic.title(testdata['caseno'] + '-' + testdata['casename'])
        time.sleep(int(testdata['sleeptime']))
        # 可运行自定义方法
        try:
            summary = Callfunc().__getattribute__(testdata['callfunc'])(testdata)
            with open(summary.log, 'r') as f:
                logs = f.read()
            logging.info('\r\n')
            logging.info(
                '--------------------------------------- httprunnerlog start ---------------------------------------')
            logging.info(logs)
            logging.info(
                '--------------------------------------- httprunnerlog end ---------------------------------------')
            logging.info('\r\n')
        except Exception as e:
            logging.info(str(e))
            raise e



# if __name__=="__main__":
#     pytest.main(['-v'])



