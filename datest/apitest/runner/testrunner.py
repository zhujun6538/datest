#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: datest
@author: MZM
@file: testrunner.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：根据参数运行pytest脚本，生成allure测试报告文件
"""

import pytest
import os
import allure
import datetime
import shutil

filepath = os.path.dirname(__file__)
testdata = f'{filepath}/test_api.py'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def pyrun(args='',reruns=0,reruns_delay=0):
    '''
    运行pytest脚本
    :param args: pytest运行参数
    :param reruns: 重跑次数
    :param reruns_delay: 重跑延迟
    :return:测试报告本地文件地址
    '''
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
    testargs.append('--alluredir')
    testargs.append(datadir)
    pytest.main(testargs)
    os.system((f'allure generate {datadir} -o {htmldir} --clean'))
    return htmldir

if __name__ == '__main__':
    pyrun('')