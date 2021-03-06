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

def apipost(httpMethod='GET',endpoint="https://112.65.144.19:9179",requestUri='',params = '',data='',json ={},files='',headers={},allow_redirects=False):
    # 发送报文
    res = requests.request(method=httpMethod,url=endpoint + requestUri,params=params, headers=headers, data=data, json = json,files=files,allow_redirects=allow_redirects,verify=False)
    print(res.status_code)
    print(res.text)
    return res