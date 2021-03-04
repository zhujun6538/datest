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





# r = get_exceldata('./testdat.xls')
# d = jsonpath.jsonpath(r,"$..casename")
# print(d)