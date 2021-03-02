from django.db import models

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100)
    sonpj = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True)
    banben = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '测试项目'

class Api(models.Model):
    code = models.CharField('代码',max_length=100)
    name = models.CharField('名称',max_length=100)
    project = models.ForeignKey(Project,verbose_name='所属项目',on_delete=models.SET_NULL,null=True)
    group = models.ForeignKey('ApiGroup',verbose_name='所属分组',on_delete=models.SET_NULL,null=True)
    header = models.ManyToManyField('Header',verbose_name='请求头',related_name='header_apis',null=True,blank=True)
    method = models.CharField('请求方法',choices=[('GET', "GET"),('POST', "POST"),('DELETE', "DELETE")],max_length=10)
    description = models.TextField('描述',max_length=1000)
    isValid = models.BooleanField('是否有效',default=True)
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.code + '-' + self.name

    class Meta:
        verbose_name_plural = '接口名称'

class ApiGroup(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '接口分组'

class TestcaseGroup(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '用例分组'

class Header(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=1000)

    def __str__(self):
        return self.key + '-' + self.value

    class Meta:
        verbose_name_plural = '请求头'

class Testcase(models.Model):
    caseno = models.CharField('用例编号',max_length=100)
    casename = models.CharField('用例名称',max_length=100)
    project = models.ForeignKey(Project, verbose_name='所属项目', on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey('TestcaseGroup',verbose_name='所属分组', on_delete=models.SET_NULL, null=True)
    beforecase = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True)
    isrun = models.CharField('是否运行', choices=[('Y', "是"), ('N', "否")], max_length=10,default='Y')
    baseurl = models.ForeignKey('BASEURL',verbose_name='环境地址',on_delete=models.SET_NULL,null=True,default=1)
    api = models.ForeignKey('Api',verbose_name='测试接口',on_delete=models.SET_NULL,null=True)
    datamode = models.CharField('请求参数类型',choices=[('JSON', "JSON"), ('FORM-DATA', "FORM-DATA")], max_length=10)
    requestdata = models.TextField('请求报文',max_length=1000,null=True,blank=True)
    setupfunc = models.ForeignKey('FUNC',verbose_name='请求前置方法',on_delete=models.SET_NULL,null=True,blank=True)
    callfunc = models.ForeignKey('CALLFUNC',verbose_name='自定义运行方法',on_delete=models.SET_NULL,null=True,blank=True)
    responsedata = models.TextField('响应报文',max_length=10000,null=True,blank=True)
    createtime = models.DateTimeField('创建时间',auto_now_add=True,null=True)
    runtime = models.DateTimeField('运行时间',null=True,blank=True)
    creater = models.ForeignKey('auth.user', verbose_name='创建人',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.project.name)  + '-' + str(self.api.name)  + '-' + self.casename

    class Meta:
        verbose_name_plural = '测试用例'

class BASEURL(models.Model):
    name = models.CharField('环境', max_length=100)
    url = models.CharField('url', max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '测试环境'

class FUNC(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000,null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'setup调用方法'

class CALLFUNC(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000,null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'call调用方法'

class HeaderParam(models.Model):
    testcase = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    paramkey = models.ForeignKey('Headerkey', verbose_name='参数',on_delete=models.SET_NULL,null=True)
    paramval = models.ForeignKey('Headerval', verbose_name='值',on_delete=models.SET_NULL,null=True)
    description = models.CharField('描述',max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.paramkey.value + '-' + self.paramval.value

    class Meta:
        verbose_name_plural = '自定义请求头'

class Headerkey(models.Model):
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value

class Headerval(models.Model):
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value

class RequestParam(models.Model):
    testcase = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    paramkey = models.ForeignKey('Reqquestkey',verbose_name='参数', on_delete=models.SET_NULL,null=True)
    paramval = models.ForeignKey('Reqquestval',verbose_name='值', on_delete=models.SET_NULL,null=True)
    description = models.CharField('描述',max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.paramkey.value + '-' + self.paramval.value

    class Meta:
        verbose_name_plural = '请求参数'

class AssertParam(models.Model):
    testcase = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    paramkey = models.ForeignKey('Assertkey',verbose_name='参数', on_delete=models.SET_NULL, null=True)
    paramval = models.ForeignKey('Assertval',verbose_name='值', on_delete=models.SET_NULL, null=True)
    description = models.CharField('描述',max_length=1000, null=True, blank=True)
    mode = models.CharField('模式', choices=[('eq', "equils"), ('in', "contains")], max_length=10,default='eq')

    def __str__(self):
        return self.paramkey.value + '-' + self.paramval.value

    class Meta:
        verbose_name_plural = '校验参数'

class Reqquestkey(models.Model):
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value

class Reqquestval(models.Model):
    value = models.CharField(max_length=100)
    type = models.CharField('类型', choices=[('str', "string"), ('int', "int"), ('True', "True"), ('False', "False")], max_length=10,default='str')

    def __str__(self):
        return self.value

class Assertkey(models.Model):
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value

class Assertval(models.Model):
    value = models.TextField(max_length=100000)
    type = models.CharField('类型', choices=[('str', "string"), ('int', "int"), ('True', "True"), ('False', "False")], max_length=10,default='str')


    def __str__(self):
        if len(self.value) > 20:
            return self.value[0:20] + '...'
        return self.value

class TESTSUITE(models.Model):
    name = models.CharField('套件名称',max_length=100)
    project = models.ForeignKey(Project,verbose_name='所属项目', on_delete=models.SET_NULL, null=True)
    baseurl = models.ForeignKey('BASEURL',verbose_name='环境地址',on_delete=models.SET_NULL,null=True)
    setupfunc = models.ForeignKey('FUNC', verbose_name='请求前置方法',on_delete=models.SET_NULL, null=True, blank=True)
    callfunc = models.ForeignKey('CALLFUNC', verbose_name='自定义运行方法',on_delete=models.SET_NULL, null=True, blank=True)
    case = models.ManyToManyField('Testcase',verbose_name='用例集', related_name='case_suites',null=True,blank=True)
    ctime = models.DateTimeField('创建时间',auto_now_add=True)
    runtime = models.DateTimeField('运行时间',null=True)
    creater = models.ForeignKey('auth.user',verbose_name='创建人',on_delete=models.CASCADE)
    args = models.ManyToManyField('Argument',verbose_name='pytest运行参数', related_name='Argument_suites',null=True,blank=True)
    reruns = models.IntegerField('失败重跑次数',null=True,blank=True,default=0)
    reruns_delay = models.IntegerField('重跑间隔时间',null=True, blank=True,default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '测试集合'

class Argument(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

class Testbatch(models.Model):
    batchno = models.CharField(max_length=100)
    testsuite = models.ManyToManyField('TESTSUITE', related_name='TESTSUITE_batch')
    ctime = models.DateTimeField(auto_now_add=True)
    runtime = models.DateTimeField(null=True)

    def __str__(self):
        return self.batchno

    class Meta:
        verbose_name_plural = '测试批次'

class Runparam(models.Model):
    case = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    param = models.CharField('参数',max_length=100)
    description = models.TextField('描述',max_length=100000,null=True)

    def __str__(self):
        return self.param

    class Meta:
        verbose_name_plural = '响应保存'

class TESTREPORT(models.Model):
    reportname = models.CharField('报告名称',max_length=100)
    testtime = models.DateTimeField('测试时间',auto_now_add=True)
    testnum = models.IntegerField('用例数量')
    testsuite = models.ManyToManyField('Testsuite',verbose_name='测试套件', related_name='suite_report')
    testcases = models.ManyToManyField('Testcase',verbose_name='测试用例', related_name='case_report')
    result = models.CharField('运行结果', choices=[('Y', "成功"), ('N', "失败")], max_length=10)
    succase = models.ManyToManyField('Testcase', verbose_name='成功用例',related_name='case_succase',blank=True)
    failcase = models.ManyToManyField('Testcase', verbose_name='失败用例',related_name='case_failcase',blank=True)
    suc = models.IntegerField('成功用例数量',null=True,blank=True)
    fail = models.IntegerField('失败用例数量',null=True,blank=True)
    runner = models.ForeignKey('auth.user',verbose_name='运行人',on_delete=models.CASCADE)
    file = models.FileField(upload_to='report',default='report/html/index.html',verbose_name='报告文件')
    errors = models.TextField('异常信息',max_length=10000,null=True)

    def __str__(self):
        return self.reportname

    class Meta:
        verbose_name_plural = '测试报告'

class Jenkinsreport(models.Model):
    testno = models.IntegerField()
    url = models.URLField(max_length=100,null=True)
    result = models.CharField('运行结果', choices=[('Y', "成功"), ('N', "失败")], max_length=10,null=True)
    output = models.TextField(max_length=10000,null=True)

    def __str__(self):
        return self.testno

    class Meta:
        verbose_name_plural = 'Jenkins测试结果'

class Postdata(models.Model):
    apiurl = models.CharField(max_length=100)
    reqdata = models.CharField(max_length=100,null=True)
    repdata = models.CharField(max_length=10000,null=True)
    reqtime = models.DateTimeField(auto_now_add=True)