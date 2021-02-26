import json
import re

import allure
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