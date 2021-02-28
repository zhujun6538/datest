#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
import json
import os
from httprunner import HttpRunner, Config, Step, RunRequest
from loguru import logger


filedir = os.path.dirname(__file__)

class TestCasePostWithFunctions(HttpRunner):
    def __init__(self,testdata):
        logger.add(filedir + '/logs/httprunner-log.txt', enqueue=True, encoding='utf-8')
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
        .setup_hook('${prerequest($request)}') \
        .setup_hook(testdata['setup_hook']) \
        .post(testdata['url'])\
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

class TestCaseGetWithFunctions(HttpRunner):
    def __init__(self,testdata):
        logger.add(filedir + '/logs/httprunner-log.txt', enqueue=True, encoding='utf-8')

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
        .setup_hook('${prerequest($request)}') \
        .get(testdata['url'])\
        .with_json(testdata['data'])\
        .with_params(**testdata['params'])\
        .with_headers(**testdata['headers']) \
        .teardown_hook('${afterresponse($response)}') \
        .validate()\

        for ast in testdata['asserts']:
            if ast[0] == 'eq':
                running = running.assert_equal(ast[1], ast[2])




        self.teststeps.append(Step(running
    ))

class TestCaseDeleteWithFunctions(HttpRunner):
    def __init__(self,testdata):
        logger.add(filedir + '/logs/httprunner-log.txt', enqueue=True, encoding='utf-8')

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
        .setup_hook('${prerequest($request)}') \
        .delete(testdata['url'])\
        .with_json(testdata['data'])\
        .with_params(**testdata['params'])\
        .with_headers(**testdata['headers']) \
        .teardown_hook('${afterresponse($response)}') \
        .validate()\

        for ast in testdata['asserts']:
            if ast[0] == 'eq':
                running = running.assert_equal(ast[1], ast[2])




        self.teststeps.append(Step(running
    ))
