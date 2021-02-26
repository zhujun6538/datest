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
    request.param['headers']= Saver.handle_params(json.dumps(request.param['headers'],ensure_ascii=False))
    request.param['data'] = Saver.handle_params(json.dumps(request.param['data'], ensure_ascii=False))
    return request.param
    logging.info('---------------------------------------' + request.param['caseno'] + '---------------------------------------')
