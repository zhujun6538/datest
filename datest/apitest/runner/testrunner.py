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
ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def pyrun():
    workpath = os.getcwd()
    shutil.rmtree(f'{filepath}/allure-report/')
    os.mkdir(f'{filepath}/allure-report')
    datadir = f'{filepath}/allure-report/data{ts}'
    htmldir = f'{BASE_DIR}/data/report/html{ts}'
    pytest.main(['-m','work','--cache-clear',testdata,'--alluredir',datadir])
    os.system((f'allure generate {datadir} -o {htmldir} --clean'))
    return htmldir

# def hrun(datas):
#     sums = {}
#     for data in datas:
#         sum = TestCaseRequestWithFunctions(data).test_start().get_summary()
#         sums[data[0]] = sum
#     return sums

if __name__ == '__main__':
    pyrun()