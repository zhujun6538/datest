import json
import os
import time
from urllib.parse import quote
# import allure
import hashlib
import logging
import hmac
import requests
import base64

def apipost(url,data):
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

    org_cnf = {"orgCode": '4894300008',  # 机构号
               "accessKeyId": '0XURN39JJ9DSJBZZP2M6',  # AK
               "secretAccessKey": 'xKPzuNhd0E+GuBGHET4ZAXdfGgzYSYhagoNi3UIVGX8=',  # SK
               }


        # 请求头
        #请求头
    headers ={
        "Accept":"application/json, text/plain, */*",
        "Accept-Encoding":"gzip, deflate",
        "Content-Type":"application/json",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
     }
    #请求方式
    httpMethod = "POST"

    # url host

    # 生产环境都是https://cisp.ect888.com
    #
    # 测试环境都是https://112.65 .144.19:9179

    endpoint="https://112.65.144.19:9179"

    #请求路径Uri同步请求地址

    # requestUri = "/ectcispserver/api/entcreditapi/asyncQueryApply"

    requestUri = url

    # requestUri = "/ectcispserver/api/entcreditapi/asyncQueryResult"

    #版本号

    version = "1.0"

    #生成指定格式的timestamp

    t = time.localtime(int(time.time()))

    timestamp = time.strftime("%Y%m%d%H%M%S", t) #查询参数字符串格式

    args = data

    # args = '{"orderNo":"01401420210201521000004719"}'

    msgId = org_cnf['orgCode'] + timestamp

    # F FЙtoSign

    toSign = httpMethod + "\n" + endpoint + "\n" + requestUri + "\n" + version + "\n" + msgId + "\n" + org_cnf['orgCode'] + "\n" + org_cnf['accessKeyId'] + "\n" + timestamp + "\n" + args
    # #JÄsignature

    signature = sign(toSign, org_cnf['secretAccessKey'])#对signature进行编码

    signature = quote(signature)

    #生成请求表单

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
    req = requests.post(endpoint + requestUri,params=formdata, headers=headers, verify=False)
    print(req.status_code)
    print(req.text)
    return req