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
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project,on_delete=models.SET_NULL,null=True)
    group = models.ForeignKey('ApiGroup',on_delete=models.SET_NULL,null=True)
    header = models.ManyToManyField('Header',related_name='header_apis')
    method = models.CharField(choices=[('GET', "GET"),('POST', "POST"),('DELETE', "DELETE")],max_length=10)
    description = models.TextField(max_length=1000)
    isValid = models.BooleanField(default=True)
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.name

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
    caseno = models.CharField(max_length=100)
    casename = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey('TestcaseGroup', on_delete=models.SET_NULL, null=True)
    isrun = models.CharField('是否运行', choices=[('Y', "是"), ('N', "否")], max_length=10,default='Y')
    baseurl = models.ForeignKey('BASEURL',on_delete=models.SET_NULL,null=True,default=1)
    api = models.ForeignKey('API',on_delete=models.SET_NULL,null=True)
    datamode = models.CharField(choices=[('JSON', "JSON"), ('FORM-DATA', "FORM-DATA")], max_length=10)
    requestdata = models.TextField(max_length=1000,null=True,blank=True)
    stfunc = models.ManyToManyField('FUNC',related_name='testcase_stfunc',blank=True)
    tdfunc = models.ManyToManyField('FUNC',related_name='testcase_tdfunc',blank=True)
    responsedata = models.TextField(max_length=10000,null=True,blank=True)
    createtime = models.DateTimeField(auto_now_add=True,null=True)
    runtime = models.DateTimeField(null=True,blank=True)
    creater = models.ForeignKey('auth.user', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.group)  + '-' + self.casename

    class Meta:
        verbose_name_plural = '测试用例'

class BASEURL(models.Model):
    name = models.CharField('环境', max_length=100)
    url = models.CharField('url', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '测试环境'

class FUNC(models.Model):
    name = models.CharField(max_length=100)
    args = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '调用方法'

class HeaderParam(models.Model):
    testcase = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    paramkey = models.ForeignKey('Headerkey', on_delete=models.SET_NULL,null=True)
    paramval = models.ForeignKey('Headerval', on_delete=models.SET_NULL,null=True)
    description = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.paramkey.value + '-' + self.paramval.value

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
    paramkey = models.ForeignKey('Reqquestkey', on_delete=models.SET_NULL,null=True)
    paramval = models.ForeignKey('Reqquestval', on_delete=models.SET_NULL,null=True)
    description = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.paramkey.value + '-' + self.paramval.value

class AssertParam(models.Model):
    testcase = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    paramkey = models.ForeignKey('Assertkey', on_delete=models.SET_NULL, null=True)
    paramval = models.ForeignKey('Assertval', on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    mode = models.CharField('模式', choices=[('eq', "equils"), ('in', "contains")], max_length=10,default='eq')

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
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    baseurl = models.ForeignKey('BASEURL',on_delete=models.SET_NULL,null=True)
    case = models.ManyToManyField('Testcase', related_name='case_suites',null=True,blank=True)
    ctime = models.DateTimeField(auto_now_add=True)
    runtime = models.DateTimeField(null=True)
    creater = models.ForeignKey('auth.user',on_delete=models.CASCADE)
    # failgoon = models.CharField('失败继续', choices=[('Y', "是"), ('N', "否")], max_length=10,default='Y')
    # failrerun = models.CharField('失败重跑', choices=[('Y', "是"), ('N', "否")], max_length=10,default='Y')
    # failreruntime = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '测试集合'

class Testbatch(models.Model):
    batchno = models.CharField(max_length=100)
    batchobs = models.ManyToManyField('TESTSUITE', related_name='TESTSUITE_batch')
    ctime = models.DateTimeField(auto_now_add=True)
    runtime = models.DateTimeField(null=True)

    def __str__(self):
        return self.batchno

class Runparam(models.Model):
    case = models.ForeignKey('Testcase', on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField(max_length=100000,null=True)

    def __str__(self):
        return self.key

class TESTREPORT(models.Model):
    reportname = models.CharField(max_length=100)
    testtime = models.DateTimeField(auto_now_add=True)
    testnum = models.IntegerField()
    testsuite = models.ManyToManyField('Testsuite', related_name='suite_report')
    testcases = models.ManyToManyField('Testcase', related_name='case_report')
    result = models.CharField('运行结果', choices=[('Y', "成功"), ('N', "失败")], max_length=10)
    succase = models.ManyToManyField('Testcase', related_name='case_succase',blank=True)
    failcase = models.ManyToManyField('Testcase', related_name='case_failcase',blank=True)
    suc = models.IntegerField(null=True,blank=True)
    fail = models.IntegerField(null=True,blank=True)
    runner = models.ForeignKey('auth.user',on_delete=models.CASCADE)
    # file = models.FileField(upload_to='report',default='report/html/index.html',)

    def __str__(self):
        return self.reportname

    class Meta:
        verbose_name_plural = '测试报告'