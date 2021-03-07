"""
@project: datest
@author: MZM
@file: conftest.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：pytest的自定义fixture函数和重写的hook函数
"""

import json
import logging
import os
from readdata import Reader
import pytest
from debugtalk import Saver

filepath = os.path.dirname(__file__)

@pytest.fixture(scope='session', autouse=True)
def getlogger():
    logging.info('开始测试')
    yield
    logging.info('结束测试')

@pytest.fixture(params=Reader.read_case(filepath + '/data/test.yaml'))
def testdata(request):
    '''
    根据文件的测试用例列表依次返回单条测试用例传给pytest脚本
    :param request:
    :return:
    '''
    logging.info('---------------------------------------' + request.param['caseno'] + '---------------------------------------')
    request.param['headers'] = json.loads(Saver.handle_params(json.dumps(request.param['headers'], ensure_ascii=False)))
    request.param['data'] = json.loads(Saver.handle_params(json.dumps(request.param['data'], ensure_ascii=False)))
    request.param['formdata'] = json.loads(Saver.handle_params(json.dumps(request.param['formdata'], ensure_ascii=False)))
    return request.param
    logging.info('---------------------------------------' + request.param['caseno'] + '---------------------------------------')

@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(session):
    '''
    存储测试结果和成功失败用例数量
    :param session:
    :return:
    '''
    result = yield
    if result.get_result() is True:
        Saver.testresult['result'] = 'Y'
    else:
        Saver.testresult['result'] = 'N'
    Saver.testresult['all'] = session.testscollected
    Saver.testresult['failed'] = session.testsfailed
    Saver.testresult['passed'] = session.testscollected - session.testsfailed

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    '''
    存储成功失败用例编号
    :param item:
    :param call:
    :return:
    '''
    result = yield
    if call.when is 'call':
        if result.get_result().outcome == 'passed':
            Saver.testresult['passedcase'].append(item.funcargs['testdata']['caseno'])
        else:
            Saver.testresult['failedcase'].append(item.funcargs['testdata']['caseno'])

@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter,exitstatus,config):
    '''
    将测试结果存入环境变量
    :param terminalreporter:
    :param exitstatus:
    :param config:
    :return:
    '''
    result = yield
    os.environ.setdefault('TESTRESULT', json.dumps(Saver.testresult))