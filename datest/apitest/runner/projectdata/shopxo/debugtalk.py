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
import random

import time

from urllib.parse import quote

import hashlib

import logging

import hmac

import base64





import allure
from conftest import Saver

def getrand(num):
    return ''.join([str(random.randint(1, 9)) for i in range(int(num))])


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

import pymysql


class getSqldata():
    def __init__(self,host='127.0.0.1',
                        port=3306,
                        user='root',
                        password='',
                        database='shopxo',
                        charset="utf8"):
        self.conn = pymysql.connect(host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        charset=charset)

    def query(self,s):
        cursor = self.conn.cursor()
        cursor.execute(s)
        res = cursor.fetchall()
        cursor.close()
        return res

    def exec(self,s):
        cursor = self.conn.cursor()
        try:
            cursor.execute(s)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
        cursor.close()

def save_user_id():
    db = getSqldata()
    username = Saver.hist[Saver.caseno]['requestdata']['username'][1]
    sql = f"select id from s_user where username = '{username}'"
    id = db.query(sql)[0][0]
    Saver.save_data('id',id)
    db.conn.close()