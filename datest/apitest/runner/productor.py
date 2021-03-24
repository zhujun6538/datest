"""
@project: datest
@author: MZM
@file: productor.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：测试过程中存储测试响应数据，通过&包围的字符根据jsonpath读取测试数据的对象字段值
"""

import json
import random
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
    '''
    运行测试session过程中保存临时数据的对象
    '''
    caseno = ''
    hist = {}
    testresult = {}
    testresult['result'] = 'N'
    testresult['passedcase'] = []
    testresult['failedcase'] = []

    @classmethod
    def save_request(cls, data,json):
        '''
        对指定测试用例保存临时请求数据
        :param data:
        :param json:
        :return:
        '''
        cls.hist[cls.caseno] = {}
        try:
            cls.hist[cls.caseno]['requestdata'] = data
        except Exception as e:
            cls.hist[cls.caseno] = data
        cls.hist[cls.caseno]['requestjson'] = json

    @classmethod
    def save_response(cls, value):
        '''
        对指定测试用例保存临时响应数据
        :param value:
        :return:
        '''
        try:
            cls.hist[cls.caseno]['response'] = json.loads(value)
        except Exception as e:
            cls.hist[cls.caseno]['response'] = value

    @classmethod
    def save_data(cls, key, value):
        '''
        对指定测试用例保存自定义的临时变量
        :param key:
        :param value:
        :return:
        '''
        try:
            cls.hist[cls.caseno][key] = json.loads(value)
        except Exception as e:
            cls.hist[cls.caseno][key] = value

    @classmethod
    def clear_data(cls):
        cls.hist.clear()
        cls.testresult.clear()
        cls.testresult['result'] = 'N'
        cls.testresult['passedcase'] = []
        cls.testresult['failedcase'] = []

    @classmethod
    def handle_params(cls, params):
        '''
        根据参数化取出的字符串查找历史数据中匹配路径的内容
        :param params:
        :return:
        '''
        if params is '':
            return
        handledata = extractor(params, cls.hist, expr='&(.*?)&')
        return handledata

    # @classmethod
    # def handle_datas(cls, params):
    #     if params[1] is '':
    #         return [None,'']
    #     handledata = extractor(params[1], cls.hist, expr='&(.*?)&')
    #     return [None,handledata]
