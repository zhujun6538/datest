import json
import logging
import os
from readdata import Reader
import pytest
from productor import Saver

filepath = os.path.dirname(__file__)

@pytest.fixture(scope='session', autouse=True)
def getlogger():
    logging.info('开始测试')
    yield
    logging.info('结束测试')

@pytest.fixture(params=Reader.read_case(filepath + './data/test.yaml'))
def testdata(request):
    logging.info('---------------------------------------' + request.param['caseno'] + '---------------------------------------')
    return request.param
    logging.info('---------------------------------------' + request.param['caseno'] + '---------------------------------------')

@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(session):
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
    result = yield
    if call.when is 'call':
        if result.get_result().outcome == 'passed':
            Saver.testresult['passedcase'].append(item.funcargs['testdata']['caseno'])
        else:
            Saver.testresult['failedcase'].append(item.funcargs['testdata']['caseno'])

@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter,exitstatus,config):
    result = yield
    os.environ.setdefault('TESTRESULT', json.dumps(Saver.testresult))