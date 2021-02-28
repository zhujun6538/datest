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

