#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
import re
import sys

import pytest
import os
import shutil

filepath = os.path.dirname(__file__)
datadir = f'{filepath}/jenkins-report/data'
testdata = f'{filepath}/test_api.py'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(*args):
    try:
        shutil.rmtree(f'{filepath}/jenkins-report/')
    except Exception as e:
        pass
    testargs = []
    pyargs = args[0][0].split(',')
    for arg in pyargs:
        testargs.append(arg)
    for exarg in args[0][1:]:
        testargs.append(exarg.split('=')[0])
        testargs.append(exarg.split('=')[1])
    testargs.append(testdata)
    testargs.append('--alluredir')
    testargs.append(datadir)
    pytest.main(testargs)

if __name__ == '__main__':
    run(sys.argv[1:])