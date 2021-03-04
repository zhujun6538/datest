#!/usr/bin/env/python3
# -*- coding:utf-8 -*-


import pytest
import os
import shutil

filepath = os.path.dirname(__file__)
testdata = f'{filepath}/test_api.py'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pyrun():
    try:
        shutil.rmtree(f'{filepath}/jenkins-report/')
    except Exception as e:
        pass
    os.mkdir(f'{filepath}/jenkins-report')
    datadir = f'{filepath}/jenkins-report/data'
    pytest.main(['-s',testdata,'--alluredir',datadir])

if __name__ == '__main__':
    pyrun()