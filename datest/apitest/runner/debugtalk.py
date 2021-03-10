"""
@project: datest
@author: MZM
@file: debugtalk.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：测试用例进行发送请求前后对请求和响应的默认调用方法，可添加在前台定义的请求前置方法
"""

import json
import logging
import os
import time
from urllib.parse import quote
import hashlib
import logging
import hmac
import base64


import allure
from productor import Saver


def prerequest(request):
    @allure.step('请求参数')
    def newpost(url, params, data,jsondata,headers):
        '''
        测试用例进行发送请求前对请求对象的默认调用方法
        :param url:
        :param params:
        :param data:
        :param jsondata:
        :param headers:
        :return:
        '''
        logging.info(f'url:{url},headers:{headers},params:{params},data:{str(data)},json:{json.dumps(jsondata)}')
        Saver.save_request(data,json)
    newpost(url=request['url'], headers=request['headers'],data = request['data'], params=request['params'],jsondata=request['req_json'])

def afterresponse(response):
    @allure.step('响应数据')
    def getresp(status_code, responsedata):
        '''
        测试用例进行发送请求后响应对象的默认调用方法
        :param status_code:
        :param responsedata:
        :return:
        '''
        logging.info("响应码：" + str(status_code))
        logging.info("响应数据：" + responsedata)
    getresp(response.status_code, response.text)
    allure.attach(response.text, 'response.txt', allure.attachment_type.TEXT)
    Saver.save_response(response.text)
