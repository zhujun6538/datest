#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: datest
@author: MZM
@file: httpfunc.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：根据用户在django系统操作的选中数据进行发送请求，存储响应，对响应结果进行断言
"""

import json
import os
from httprunner import HttpRunner, Config, Step, RunRequest
from loguru import logger
from productor import Saver
filedir = os.path.dirname(__file__)

class PostWithFunctions(HttpRunner):
    def __init__(self,testdata):
        '''
        根据用户在django系统操作的选中数据进行发送请求，存储响应，对响应结果进行断言
        :param testdata: 单条测试用例数据
        '''
        Saver.caseno = testdata['caseno']
        self.config = (
            Config(testdata['caseno'] + '-' + testdata['casename'])
                .variables(
                **{}
            )
                .base_url(testdata['baseurl'])
                .verify(False)
        )

        self.teststeps = []

        running = RunRequest(testdata['casename'])\
        .with_variables() \
        .setup_hook(testdata['setupfunc']) \
        .__getattribute__(testdata['method'].lower())(testdata['url']) \
        .with_json(testdata['data'])\
        .with_data(testdata['formdata'])\
        .with_params(**testdata['params'])\
        .with_headers(**testdata['headers']) \
        .teardown_hook('${afterresponse($response)}') \
        .validate() \

        for ast in testdata['asserts']:
            if ast[0] == 'eq':
                running = running.assert_equal(ast[1], ast[2])
        self.teststeps.append(Step(running
    ))