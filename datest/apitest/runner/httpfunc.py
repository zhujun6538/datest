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
import logging
import os
from httprunner import HttpRunner, Config, Step, RunRequest
from httprunner.loader import load_project_meta
from productor import Saver

filedir = os.path.dirname(__file__)

class PostWithFunctions(HttpRunner):
    def __init__(self,testdata):
        '''
        根据用户在django系统操作的选中数据使用httprunner发送请求数据、进行前置后置处理，根据断言校验响应报文等
        :param testdata: 单条测试用例数据
        '''

        Saver.caseno = testdata['caseno']
        # 请求的基本配置
        self.config = (
            Config(testdata['caseno'] + '-' + testdata['casename'])
                .variables(
                **{}
            )
                .base_url(testdata['baseurl'])
                .verify(False)
        )

        self.with_project_meta(load_project_meta(filedir + '/projects/' +testdata['project'] + '/'))


        self.teststeps = []

        # 根据输入值构建请求信息
        running = RunRequest(testdata['casename'])\
        .with_variables() \
        .setup_hook('${prerequest($request)}') \
        .setup_hook(testdata['setupfunc']) \
        .__getattribute__(testdata['method'].lower())(testdata['url']) \
        .with_json(testdata['data'])\
        .with_data(testdata['formdata'])\
        .with_params(**testdata['params'])\
        .with_headers(**testdata['headers']) \
        .teardown_hook('${afterresponse($response)}') \
        .teardown_hook(testdata['teardownfunc']) \
        .validate() \

        # 根据校验参数输入值构建断言
        for ast in testdata['asserts']:
            running = running.__getattribute__(ast[0].lower())(ast[1], ast[2])
        self.teststeps.append(Step(running
    ))