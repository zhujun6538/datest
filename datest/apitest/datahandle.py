"""
@project: datest
@author: MZM
@file: datahandle.py
@ide: PyCharm
@time: 2021/3/4 16:14
@desc：本文件根据数据库的数据生成测试用例等数据，供后台脚本调用
"""

import json
import os
import random
import re

import xlrd
from django.urls import reverse
from ruamel import yaml



def toint(value):
    # 导入时指定格式字符串转换成int
    return int(re.findall("{I(\d*?)}", value)[0])

def get_paramval(s,type):
    # 根据校验参数值的值和类型生成数据
    if type == 'int':
        return int(s)
    elif type == 'str':
        return s
    elif type == 'True':
        return True
    elif type == 'False':
        return False

def write_case(filepath, data):
    '''
    写入yaml文件
    :param filepath:
    :param data:
    :return:
    '''
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=yaml.RoundTripDumper)

def clean(value):
    # 根据输入字符串转换成对应类型的值
    if re.search("{I(\d*?)}", value):
        value = toint(value)
    elif re.search("{T}", value):
        value = True
    elif re.search("{F}", value):
        value = False
    return value


    return value

def get_casedata(suitename,case,baseurl='',setupfunc='',teardownfunc='',callfunc='',sleeptime=0):
    '''
    根据Testcase对象生成测试用例字典
    :param suitename:
    :param case: 测试用例模块选中的所有用例
    :param baseurl:
    :param setupfunc:
    :param callfunc:
    :param sleeptime:
    :return:
    '''
    testcase = {}
    data = {}
    formdata = {}
    caselink = reverse('admin:apitest_testcase_change',args=(case.id,))
    if case.datamode == 'JSON':
        data = json.loads(case.requestdata,encoding='utf-8')
        for key,value in data.items():
            data[key] = clean(value)
    elif case.datamode == 'FORM-DATA':
        try:
            for line in case.requestdata.splitlines():
                formdata[line.split(':')[0]] = (None, clean(line.split(':')[1].lstrip(' ')))
        except Exception as e:
            formdata = {}
            for fdata in case.formdataparam_set.all():
                formdata[fdata.paramkey.value] = (None, fdata.paramval.value)
    headers = {}
    if baseurl != '':
        testcase['baseurl'] = baseurl
    else:
        testcase['baseurl'] = case.baseurl.url
    if setupfunc != '':
        testcase['setupfunc'] = setupfunc
    else:
        if case.setupfunc == None:
            testcase['setupfunc'] = ''
        else:
            testcase['setupfunc'] = case.setupfunc.name
    if teardownfunc != '':
        testcase['teardownfunc'] = teardownfunc
    else:
        if case.teardownfunc == None:
            testcase['teardownfunc'] = ''
        else:
            testcase['teardownfunc'] = case.teardownfunc.name
    if callfunc != '':
        testcase['callfunc'] = callfunc
    else:
        if case.callfunc == None:
            testcase['callfunc'] = 'default_func'
        else:
            testcase['callfunc'] = case.callfunc.name
    for header in case.api.header.all():
        headers[header.key] = header.value
    for exheader in case.headerparam_set.all():
        headers[exheader.paramkey.value] = exheader.paramval.value
    params = {}
    for pdata in case.requestparam_set.all():
        params[pdata.paramkey.value]= pdata.paramval.value
    asserts = []
    for adata in case.assertparam_set.all():
        asserts.append([adata.mode, adata.paramkey.value, get_paramval(adata.paramval.value,adata.paramval.type)])

    testcase['suitename'] ,testcase['group'] ,testcase['caseno'], testcase['casename'], \
    testcase['isValid'], testcase['method'],testcase['url'], testcase['data'], \
    testcase['params'], testcase['formdata'], testcase['headers'], testcase['asserts'], \
    testcase['sleeptime'] ,testcase['caselink'] ,testcase['project'] ,testcase['jsonschema']= \
        suitename,case.group.name, case.caseno, case.casename, \
        case.isValid, case.api.method , case.api.url, data, \
        params, formdata, headers, asserts, \
        sleeptime, caselink,case.project.name, case.api.jsonschema

    return testcase

def get_suitedata(obj,baseurl='',sleeptime=0):
    '''
    根据测试套件对象获取所有测试用例列表
    :param obj:
    :return:
    '''
    testsuite = []
    # 可覆盖测试用例的功能
    suitename = obj.name
    try:
        setupfunc = obj.setupfunc.name
        teardownfunc = obj.teardownfunc.name
    except Exception as e:
        setupfunc = ''
        teardownfunc = ''
    try:
        callfunc = obj.callfunc.name
    except Exception as e:
        callfunc = ''

    if obj.isorder is False:
        # 未勾选是否顺序运行
        cases = obj.case.all()
        for case in cases:
            testcase = get_casedata(suitename, case, baseurl, setupfunc,teardownfunc, callfunc,sleeptime)
            testsuite.append(testcase)
    else:
        # 勾选是否顺序运行
        cases = obj.testcaselist_set.all().order_by('runno')
        for case in cases:
            testcase = get_casedata(suitename, case.testcase, baseurl, setupfunc, teardownfunc,callfunc,sleeptime)
            testsuite.append(testcase)

    return testsuite

def get_faildata(obj):
    '''
    根据测试套件对象获取所有测试用例列表
    :param obj:
    :return:
    '''
    testsuite = []
    # 可覆盖测试用例的功能
    suitename = obj.reportname + '重跑失败用例'
    cases = obj.failcase.all()
    for case in cases:
        testcase = get_casedata(suitename, case)
        testsuite.append(testcase)
    return testsuite


def get_exceldata(filepath):
    '''
    导入时从保存的文件中读取数据
    :param filepath:
    :return:
    '''
    data = xlrd.open_workbook(filepath)
    sheet = data.sheet_by_index(0)
    sheetkeys = sheet.row_values(0)
    rnum = sheet.nrows
    cnum = sheet.ncols
    l = []
    for row in range(rnum):
        d = {}
        if row > 0:
            rowvalue = sheet.row_values(row)
            for col in range(cnum):
                d[sheetkeys[col]] = rowvalue[col]
            l.append(d)
    return l