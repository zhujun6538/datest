import json
import logging
import os


import allure
from productor import Saver


def prerequest(request):
    @allure.step('请求参数')
    def newpost(url, params, data,jsondata,headers):
        logging.info(f'url:{url},headers:{headers},params:{params},data:{str(data)},json:{json.dumps(jsondata)}')
    newpost(url=request['url'], headers=request['headers'],data = request['data'], params=request['params'],jsondata=request['req_json'])

def afterresponse(response):
    @allure.step('响应数据')
    def getresp(status_code, responsedata):
        logging.info("响应码：" + str(status_code))
        logging.info("响应数据：" + responsedata)
    getresp(response.status_code, response.text)
    allure.attach(response.text, 'response.txt', allure.attachment_type.TEXT)
    Saver.save_response(response.text)

