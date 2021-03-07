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

def ztrequest(request):
    '''
    自定义方法
    :param request:
    :return:
    '''
    # @Time:  2021/1/19 16:11
    # @Authon: wanggang
    # @File: case.py

    # /
    #
    # 同步请求的例子
    #
    # #特别注意该处的requestUri
    #
    # #同步与异步请求，在请求方式上，只在这里存在区别。 *通常同步请求的requestUri 有这么几种
    #
    # * requestUri = "/ectcispserver/api/entcredit/query" * requestUri = "/ectcispserver/api/assQry/query
    #
    # *具体还要参考接口文档
    #
    # *j

    def sign(value, key):
        j = hmac.new(base64.b64decode(key), value.encode(), digestmod=hashlib.sha256)
        ret = (base64.b64encode(j.digest()).decode())

        return ret

    prerequest(request)

    org_cnf = {"orgCode": '4894300008',  # 机构号
               "accessKeyId": '0XURN39JJ9DSJBZZP2M6',  # AK
               "secretAccessKey": 'xKPzuNhd0E+GuBGHET4ZAXdfGgzYSYhagoNi3UIVGX8=',  # SK
               }

    # 请求头
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
    }
    request['headers'] = headers
    # 请求方式
    httpMethod = "POST"

    # url host

    # 生产环境都是https://cisp.ect888.com
    #
    # 测试环境都是https://112.65 .144.19:9179

    endpoint = "https://112.65.144.19:9179"

    # 请求路径Uri同步请求地址

    requestUri = request['url']

    # 版本号

    version = "1.0"

    # 生成指定格式的timestamp

    t = time.localtime(int(time.time()))

    timestamp = time.strftime("%Y%m%d%H%M%S", t)  # 查询参数字符串格式

    args = json.dumps(request['req_json'], ensure_ascii=False)

    logging.info("请求参数" + args)

    msgId = org_cnf['orgCode'] + timestamp

    # F FЙtoSign

    toSign = httpMethod + "\n" + endpoint + "\n" + requestUri + "\n" + version + "\n" + msgId + "\n" + org_cnf[
        'orgCode'] + "\n" + org_cnf['accessKeyId'] + "\n" + timestamp + "\n" + args
    # #JÄsignature

    signature = sign(toSign, org_cnf['secretAccessKey'])  # 对signature进行编码

    signature = quote(signature)

    # 生成请求表单

    # 生成请求表单
    formdata = dict()
    formdata['version'] = version
    formdata['msgId'] = msgId
    formdata['orgCode'] = org_cnf['orgCode']
    formdata['accessKeyId'] = org_cnf['accessKeyId']
    formdata['transTime'] = timestamp
    formdata['timestamp'] = timestamp
    formdata['args'] = quote(args)
    formdata['queryMode'] = "0"
    formdata['signature'] = signature
    # 发送报文
    request['params'] = formdata

    @allure.step('zt请求参数')
    def newpost(url, args, headers):
        logging.info('请求参数' + args)
    newpost(url=endpoint + requestUri, args=args, headers=headers)
