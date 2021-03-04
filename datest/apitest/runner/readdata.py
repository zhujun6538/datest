#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: datest
@author: MZM
@file: readdata.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：读取yaml文件生成测试数据
"""

import json
import yaml
import xlrd
import jsonpath
from ruamel import yaml

class Reader:
    @classmethod
    def write_case(cls,filepath,data):
        '''
        :param filepath:
        :param data:
        :return:
        '''
        with open(filepath,'w',encoding='utf-8') as f:
            yaml.dump(data,f,Dumper=yaml.RoundTripDumper)


    @classmethod
    def read_case(cls,filepath):
        '''
        :param filepath:
        :return:
        '''
        with open(filepath, 'r', encoding='utf-8') as f:
            r =  yaml.load(f,Loader=yaml.Loader)
            d = []
            for suite in r:
                for case in suite:
                    d.append(case)
        return d





# r = get_exceldata('./testdat.xls')
# d = jsonpath.jsonpath(r,"$..casename")
# print(d)