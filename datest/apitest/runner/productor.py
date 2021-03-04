"""
@project: datest
@author: MZM
@file: productor.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：测试过程中存储测试响应数据，通过&包围的字符根据jsonpath读取测试数据的对象字段值
"""

import json
import re
import jsonpath



def extractor(data, dics, expr):
    for s in re.findall(expr, data):
        try:
            exs = jsonpath.jsonpath(dics, s)[0]
        except Exception as e:
            exs = None
        data = data.replace(f'&{s}&', str(exs))
    return data

class Saver:
    caseno = ''
    httphist = {}
    testresult = {}
    testresult['result'] = 'N'
    testresult['passedcase'] = []
    testresult['failedcase'] = []


    @classmethod
    def save_response(cls, value):
        try:
            cls.httphist[cls.caseno] = json.loads(value)
            print(cls.httphist)
        except Exception as e:
            cls.httphist[cls.caseno] = value

    @classmethod
    def handle_params(cls, params):
        if params is '':
            return
        handledata = extractor(params, cls.httphist, expr='&(.*?)&')
        return eval(handledata)

