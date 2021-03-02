#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
import json
import os
from httprunner import HttpRunner, Config, Step, RunRequest
from loguru import logger
from productor import Saver
filedir = os.path.dirname(__file__)

class ZTPostWithFunctions(HttpRunner):
    def __init__(self,testdata):
        Saver.caseno = testdata['caseno']
        testdata['headers'] = Saver.handle_params(json.dumps(testdata['headers'], ensure_ascii=False))
        testdata['data'] = Saver.handle_params(json.dumps(testdata['data'], ensure_ascii=False))
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
        .with_params(**testdata['params'])\
        .with_headers(**testdata['headers']) \
        .teardown_hook('${afterresponse($response)}') \
        .validate() \

        for ast in testdata['asserts']:
            if ast[0] == 'eq':
                running = running.assert_equal(ast[1], ast[2])




        self.teststeps.append(Step(running
    ))