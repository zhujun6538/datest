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

import xlrd
from django.urls import reverse
from ruamel import yaml

def get_paramval(s,type):
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

def get_casedata(suitename,case,baseurl='',setupfunc='',callfunc='',sleeptime=0):
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
    caselink = reverse('admin:apitest_testcase_change',args=(case.id,))
    if case.api.method in ['POST','PUT'] and case.datamode == 'JSON':
        data = json.loads(case.requestdata,encoding='utf-8')
    headers = {}
    if baseurl != '':
        testcase['baseurl'] = baseurl
    if setupfunc != '':
        testcase['setupfunc'] = setupfunc
    else:
        if case.setupfunc == None:
            testcase['setupfunc'] = '${prerequest($request)}'
        else:
            testcase['setupfunc'] = case.setupfunc.name
    if callfunc != '':
        testcase['callfunc'] = callfunc
    else:
        if case.callfunc == None:
            testcase['callfunc'] = 'default_func'
        else:
            testcase['callfunc'] = case.callfunc.name
    for header in case.api.header.all():
        headers[header.key] = header.value
    asserts = []
    for exheader in case.headerparam_set.all():
        headers[exheader.paramkey.value] = exheader.paramval.value
    params = {}
    for pdata in case.requestparam_set.all():
        params[pdata.paramkey.value]= pdata.paramval.value
    for adata in case.assertparam_set.all():
        asserts.append([adata.mode, adata.paramkey.value, get_paramval(adata.paramval.value,adata.paramval.type)])
    testcase['extract'] = []
    for extdata in case.runparam_set.all():
        testcase['extract'].append(extdata.param)
    testcase['suitename'] ,testcase['group'] ,testcase['caseno'], testcase['casename'], \
    testcase['isValid'], testcase['method'],testcase['url'], \
    testcase['baseurl'],testcase['data'], testcase['params'], testcase['headers'], testcase['asserts'], testcase['sleeptime'] ,testcase['caselink']  = \
        suitename,case.group.name, case.caseno, case.casename, case.isValid, case.api.method , case.api.url, case.baseurl.url,data, params, headers, asserts, sleeptime, caselink
    if case.beforecase!=None:
        testcase['before'] = get_casedata(suitename,case.beforecase,baseurl)
    return testcase

def get_suitedata(obj):
    '''
    根据测试套件对象获取所有测试用例列表
    :param obj:
    :return:
    '''
    testdata = []
    suitename = obj.name
    baseurl = obj.baseurl.url
    sleeptime = obj.sleeptime
    try:
        setupfunc = obj.setupfunc.name
        callfunc = obj.callfunc.name
    except Exception as e:
        setupfunc = ''
        callfunc = ''
    if obj.isorder is False:
        cases = obj.case.all()
        for case in cases:
            testcase = get_casedata(suitename, case, baseurl, setupfunc, callfunc,sleeptime)
            testdata.append(testcase)
    else:
        cases = obj.testcaselist_set.all().order_by('runno')
        for case in cases:
            testcase = get_casedata(suitename, case.testcase, baseurl, setupfunc, callfunc,sleeptime)
            testdata.append(testcase)
    return testdata

def get_exceldata(filepath):
    '''
    导入时从xls文件读取数据
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