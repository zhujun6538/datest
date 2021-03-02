#!/usr/bin/env/python3
# -*- coding:utf-8 -*-


import pytest
import os
import allure
import datetime
import shutil
# from .httprequest import TestCaseRequestWithFunctions

filepath = os.path.dirname(__file__)
testdata = f'{filepath}/test_api.py'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def pyrun(args='',reruns=0,reruns_delay=0):
    if not os.path.exists(f'{filepath}/allure-report/'):
        os.mkdir(f'{filepath}/allure-report/')
    shutil.rmtree(f'{filepath}/allure-report/')
    os.mkdir(f'{filepath}/allure-report')
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    datadir = f'{filepath}/allure-report/data{ts}'
    htmldir = f'{BASE_DIR}/data/report/html{ts}'
    testargs = []
    for arg in args:
        testargs.append(arg[0])
    testargs.append(testdata)
    testargs.append('--reruns')
    testargs.append(str(reruns))
    testargs.append('--reruns-delay')
    testargs.append(str(reruns_delay))
    testargs.append('--alluredir')
    testargs.append(datadir)
    pytest.main(testargs)
    os.system((f'allure generate {datadir} -o {htmldir} --clean'))
    return htmldir

# def hrun(datas):
#     sums = {}
#     for data in datas:
#         sum = TestCaseRequestWithFunctions(data).test_start().get_summary()
#         sums[data[0]] = sum
#     return sums

if __name__ == '__main__':
    pyrun('')