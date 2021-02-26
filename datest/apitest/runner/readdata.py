#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import json
import yaml
import xlrd
import jsonpath
from ruamel import yaml

class Reader:

    @classmethod
    def write_case(cls,filepath,data):
        with open(filepath,'w',encoding='utf-8') as f:
            yaml.dump(data,f,Dumper=yaml.RoundTripDumper)


    @classmethod
    def read_case(cls,filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            r =  yaml.load(f,Loader=yaml.Loader)
            d = []
            for suite in r:
                for case in suite:
                    d.append(case)
        return d

# data = {'P1040007': {'baseurl': 'https://112.65.144.19:9179', 'teststeps': [{'moduleid': 'P1040007', 'caseid': 'P1040007-1', 'casename': 'P1040007测试用例1', 'isrun': 'Y', 'url': '/ectcispserver/api/perscreditapi/query', 'baseurl': 'https://112.65.144.19:9179', 'params': {'prodCode': 'P1040007', 'entName': '北京普思投资有限公司', 'persName': '王思聪', 'idNo': '210203198801034012'}, 'headers': {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}, 'asserts': {'$.status_code': '200', '$..resultCode': '00000', '$..resultDesc': '成功', '$..legRepInfoList[0].ryName': '王思聪'}}, {'moduleid': 'P1040007', 'caseid': 'P1040007-2', 'casename': 'P1040007测试用例2', 'isrun': 'Y', 'url': '/ectcispserver/api/perscreditapi/query', 'baseurl': 'https://112.65.144.19:9179', 'params': {'prodCode': 'P1040007', 'entName': '北京普思投资有限公司', 'persName': '王思聪'}, 'headers': {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}, 'asserts': {'$.status_code': '200', '$..resultCode': '00000', '$..resultDesc': '成功', '$..legRepInfoList[0].ryName': '王思聪'}}]}}

# write_case('./test.yaml',data)
# r = read_case('./test.yaml')
# assert r == data



# r = get_exceldata('./testdat.xls')
# d = jsonpath.jsonpath(r,"$..casename")
# print(d)