import csv
import datetime
import random
import re
import shutil
import time
from lxml import etree
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET

import jenkins
import jsonpath
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import MultipleObjectsReturned
from django.core.files import File
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from openpyxl import Workbook
from rest_framework.reverse import reverse as rvs
from simpleui.admin import AjaxAdmin
from import_export import resources, fields
from .forms import CsvImportForm, ApiImportForm, ApiConfirmImportForm, TestcaseImportForm, TestcaseConfirmImportForm
from .models import *
from .datahandle import *
from .postmail import postmail
from .views import run_data
# Register your models here.
from .runner import testrunner


# admin.site.unregister(User)
# admin.site.unregister(Group)
from .runner.scheduler import scheduler
AdminSite.site_header = "证通接口自动化测试平台"
AdminSite.index_title = "api测试"
filedir = os.path.dirname(__file__)

class ApiResource(resources.ModelResource):
    class Meta:
        model = Api
        exclude = ('updatetime','createtime')

    def import_row(self,row, instance_loader, using_transactions, dry_run, raise_errors, **kwargs):
        jsonschema = row['jsonschema'].replace('$schema','*schema')
        row.move_to_end('jsonschema')
        row.popitem()
        row.update({'jsonschema':jsonschema})
        row.update({'project': kwargs['project']})
        row.update({'group': kwargs['group']})
        row.update({'creater': kwargs['user'].id})
        return super().import_row(row, instance_loader, using_transactions, dry_run, raise_errors, **kwargs)


@admin.register(Api)
class ApiAdmin(ImportExportModelAdmin,AjaxAdmin):
    resource_class = ApiResource
    list_display = ['code','name','creater','project','group','requesttype','isValid','get_casenum','edit']
    search_fields = ['name','code']
    filter_horizontal = ['header']
    list_filter = ['group','project','isValid']
    actions = ['get_excel','daoru']
    save_on_top = True
    exclude = ('creater',)
    list_editable = ('isValid',)
    list_per_page = 10
    fields_options = {
        'edit': {
            'fixed': 'left'
        }
    }

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.creater = request.user
        super().save_model(request, obj, form, change)

    def get_search_results(self, request, queryset, search_term):
        '''
        get_search_results方法将显示的对象列表修改为与提供的搜索词匹配的对象。它接受请求，应用当前过滤器的查询集以及用户提供的搜索词。它返回一个元组，该元组包含为实现搜索而进行修改的queryset和一个布尔值，指示结果是否可能包含重复项。
        :param request:
        :param queryset:
        :param search_term:
        :return:
        '''
        if request.path == '/admin/apitest/api/autocomplete/':
            queryset = queryset.filter(isValid=True)
        return super().get_search_results(request, queryset, search_term)

    def edit(self,obj):
        return format_html('<button type="button" class="el-button el-button--default el-button--mini"><a href="{}">{}</a></button>',\
                           rvs('api-detail',args=[obj.id]) + 'runapi','调试')
    edit.short_description = '测试'

    def get_casenum(self,obj):
        casenum = obj.testcase_set.count()
        return format_html('<a href="{}" style="text-decoration:underline">{}',f'/admin/apitest/testcase/?api__id__exact={obj.id}' , str(casenum))
    get_casenum.short_description = '用例数'

    def get_import_form(self):
        return ApiImportForm

    def get_confirm_import_form(self):
        return ApiConfirmImportForm

    def get_import_data_kwargs(self,request, form, *args, **kwargs):
        if isinstance(form, (ApiImportForm,ApiConfirmImportForm)):
            if form.is_valid():
                project = form.cleaned_data['project']
                group = form.cleaned_data['group']
                kwargs.update({'project': project.id,'group': group.id})
                return kwargs
        return super().get_import_data_kwargs(request, form=form, *args, **kwargs)

    def get_form_kwargs(self, form, *args, **kwargs):
        # pass on `author` to the kwargs for the custom confirm form
        if isinstance(form, (ApiImportForm,ApiConfirmImportForm)):
            if form.is_valid():
                project = form.cleaned_data['project']
                group = form.cleaned_data['group']
                kwargs.update({'project': project.id,'group': group.id})
        return kwargs



    def get_excel(self, request, query_set):
        '''
        导出xls文件
        :param request:
        :param query_set:
        :return:
        '''
        fieldsname = [field.name for field in self.model._meta.fields] #表字段名列表
        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment ; filename = "api.xlsx"'
        wb = Workbook()
        ws = wb.active
        ws.append(fieldsname)
        for obj in query_set:
            rowvalue = []
            for field in fieldsname:
                rowvalue.append(f'{getattr(obj,field)}')
            ws.append(rowvalue)
        wb.save(response)
        return response
    get_excel.short_description = '导出选中对象'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','creater', 'banben']
    exclude = ('creater',)

    def save_model(self, request, obj, form, change):
        # 同时创建存放自定义函数文件的项目目录
        projectpath = filedir + '/runner/projects/'
        if not os.path.exists(projectpath):
            os.mkdir(projectpath)
        if not change:
            obj.creater = request.user
            super().save_model(request, obj, form, change)
            # 同时创建存放自定义函数文件的项目目录
            if not os.path.exists(projectpath + obj.name):
                os.mkdir(projectpath + obj.name)
            # 复制默认函数到项目文件夹
            shutil.copyfile(filedir + '/runner/debugtalk.py', projectpath + obj.name + '/debugtalk.py')
            with open(projectpath + obj.name + '/debugtalk.py', 'r+', encoding='utf-8') as f:
                content = f.read()
            # 将自定义函数文件信息存入表
            DebugTalk.objects.create(project=obj,file='/runner/projects/' + obj.name + '/debugtalk.py',content=content)
        super().save_model(request, obj, form, change)


@admin.register(DebugTalk)
class DebugTalkAdmin(admin.ModelAdmin):
    list_display = ['project','file','edit']

    def edit(self,obj):
        return format_html('<button type="button" class="el-button el-button--default el-button--mini"><a href="{}">{}</a></button> ',rvs('debugtalk-detail',args=[obj.id]) + 'edit','编辑')
    edit.short_description = '操作'

    def delete_model(self,request,obj):
        '''删除对象同时删除本地文件'''
        super().delete_model(request,obj)
        debugtalkfile = obj.file.rsplit('/',1)[0]
        if os.path.exists(filedir+debugtalkfile):
            shutil.rmtree(filedir+debugtalkfile)

@admin.register(ApiGroup)
class ApiGroupAdmin(admin.ModelAdmin):
    '''
    接口分组
    '''
    list_display = ['name']

@admin.register(TestcaseGroup)
class TestcaseGroupAdmin(admin.ModelAdmin):
    '''
    测试用例分组
    '''
    exclude = ['creater',]

    def save_model(self, request, obj, form, change):
        obj.creater = request.user
        super().save_model(request, obj, form, change)

@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ['key','value']

@admin.register(BASEURL)
class BASEURLAdmin(admin.ModelAdmin):
    list_display = ['name','url']

class HeaderParaminline(admin.TabularInline):
    '''
    测试用例中的自定义请求头内联关系
    '''
    model = HeaderParam
    extra = 0

    @admin.register(Headerkey)
    class HeaderkeyAdmin(admin.ModelAdmin):
        '''
        自定义请求头参数名
        '''
        search_fields = ['value']

        def has_module_permission(self,request):
            return False

    @admin.register(Headerval)
    class HeadervalAdmin(admin.ModelAdmin):
        '''
        自定义请求头参数值
        '''
        search_fields = ['value']

        def has_module_permission(self, request):
            return False

class FormdataParaminline(admin.TabularInline):
    '''
    测试用例中的formdata内联关系
    '''
    model = FormdataParam
    extra = 0
    autocomplete_fields = ['paramkey','paramval']

    @admin.register(Formdatakey)
    class FormdatakeyAdmin(admin.ModelAdmin):
        search_fields = ['value']

        def has_module_permission(self,request):
            return False

    @admin.register(Formdataval)
    class FormdatavalAdmin(admin.ModelAdmin):
        search_fields = ['value']

        def has_module_permission(self,request):
            return False

class AssertParaminline(admin.TabularInline):
    '''
    测试用例中的校验参数内联关系
    '''
    model = AssertParam
    extra = 0
    autocomplete_fields = ['paramkey','paramval']

    @admin.register(Assertkey)
    class AssertkeyAdmin(admin.ModelAdmin):
        search_fields = ['value']

        def has_module_permission(self, request):
            return False

        def get_changeform_initial_data(self, request):
            return {'value': 'body.'}

    @admin.register(Assertval)
    class AssertvalAdmin(admin.ModelAdmin):
        search_fields = ['value']

        def has_module_permission(self, request):
            return False

class RequestParaminline(admin.TabularInline):
    '''
    测试用例中的URL请求参数内联关系
    '''
    model = RequestParam
    extra = 0
    autocomplete_fields = ['paramkey', 'paramval']

    @admin.register(Reqquestkey)
    class ReqquestkeyAdmin(admin.ModelAdmin):
        search_fields = ['value']

        def has_module_permission(self,request):
            return False

    @admin.register(Reqquestval)
    class ReqquestvalAdmin(admin.ModelAdmin):
        search_fields = ['value']

        def has_module_permission(self,request):
            return False

@admin.register(FUNC)
class FUNCAdmin(admin.ModelAdmin):
    '''
    自定义请求前置后置方法名
    '''
    list_display = ['name','description']

    def has_module_permission(self,request):
        return False

@admin.register(CALLFUNC)
class CALLFUNCAdmin(admin.ModelAdmin):
    '''
    自定义运行方法名
    '''
    list_display = ['name','description']

    def has_module_permission(self,request):
        return False


def run_case(query_set,baseurl,sleeptime):
    '''依次运行query_set中的所有测试用例'''
    for obj in query_set:
        testdata = get_casedata('运行测试用例',obj,baseurl=baseurl,sleeptime=sleeptime)
        testreport = run_data(data = [[testdata]])
        testreport.testcases.add(obj)
        testreport.save()
        obj.runtime = timezone.now()
        obj.save()

class TestcaseResource(resources.ModelResource):

    class Meta:
        model = Testcase
        exclude = ('responsedata','baseurl','isValid','runtime','updatetime','createtime')

    def import_row(self,row, instance_loader, using_transactions, dry_run, raise_errors, **kwargs):
        caseno = row['api'] + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1, 10000))
        apiobj = Api.objects.filter(code = row['api'])[0]
        row.move_to_end('api')
        row.popitem()
        row.update({'api':apiobj.id})
        row.update({'project': kwargs['project']})
        row.update({'group': kwargs['group']})
        row.update({'creater': kwargs['user'].id})
        row.update({'caseno': caseno})
        return super().import_row(row, instance_loader, using_transactions, dry_run, raise_errors, **kwargs)

@admin.register(Testcase)
class TestcaseAdmin(ImportExportModelAdmin, AjaxAdmin):
    resource_class = TestcaseResource
    list_display = ['caseno','casename','creater','isValid', 'group', 'api', 'edit']
    search_fields = ['caseno','casename']
    radio_fields = {"datamode": admin.HORIZONTAL}
    autocomplete_fields = ['api']
    inlines = [HeaderParaminline,RequestParaminline,FormdataParaminline, AssertParaminline,]
    save_on_top = True
    list_filter = ['group', 'project','callfunc','isValid','api']
    actions = ['copy','get_caseyml','runcase']
    fields = ('casename','group','baseurl','api','datamode','requestdata','setupfunc','teardownfunc','callfunc','isValid',)
    list_per_page = 10
    readonly_fields = ('responsedata',)
    list_editable = ['isValid','api']
    ordering = ('-createtime',)
    fields_options = {
        'edit': {
            'fixed': 'left'
        }
    }


    def get_search_results(self, request, queryset, search_term):
        # API中筛选有效的API
        if request.path == '/admin/apitest/testcase/autocomplete/':
            queryset = queryset.filter(isValid=True)
        return super().get_search_results(request, queryset, search_term)

    def edit(self,obj):
        reportlink = ''
        reporturl = ''
        lastreports = TESTREPORT.objects.filter(testcases=obj).order_by('-testtime')
        if len(lastreports) != 0:
            reportlink = '查看报告'
            reporturl = lastreports[0].file.url
            return format_html('<a href="{}"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a> \
            <a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a>',\
                               rvs('testcase-detail',args=[obj.id]) + 'postcase','发送',reporturl,reportlink)
        return format_html('<a href="{}"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a>',\
                               rvs('testcase-detail',args=[obj.id]) + 'postcase','发送')
    edit.short_description = '操作'

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.caseno = obj.api.code + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1,1000))
            obj.casename = obj.api.name + '-' + obj.casename
            obj.project = obj.api.project
            obj.creater = request.user
        super().save_model(request, obj, form, change)

    def copy(self,request,query_set):
        for obj in query_set:
            oid = obj.id
            obj.id = None
            obj.caseno = obj.api.code + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1, 1000))
            obj.save()
            # 将原对象的外联对象与新对象关联
            oldobj = Testcase.objects.get(id = oid)
            for par in list(oldobj.headerparam_set.all()):
                HeaderParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.formdataparam_set.all()):
                FormdataParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.requestparam_set.all()):
                RequestParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.assertparam_set.all()):
                AssertParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval,mode=par.mode)
    copy.short_description = '复制'

    def get_excel(self, request, query_set):
        '''
        导出xls
        :param request:
        :param query_set:
        :return:
        '''
        fieldsname = [field.name for field in self.model._meta.fields]
        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment ; filename = "testcase.xlsx"'
        wb = Workbook()
        ws = wb.active
        ws.append(fieldsname)
        for obj in query_set:
            rowvalue = []
            # 行加入对应字段值
            for field in fieldsname:
                if getattr(obj,field) is not None:
                    rowvalue.append(f'{getattr(obj,field)}')
                else:
                    rowvalue.append('')
            # 行末尾加入所有校验参数
            for assdata in obj.assertparam_set.all():
                rowvalue.append(assdata.paramkey.value + '|' + assdata.paramval.value)
            row = ws.append(rowvalue)
        wb.save(response)
        return response
    get_excel.short_description = '导出选中对象'

    def get_import_form(self):
        return TestcaseImportForm

    def get_confirm_import_form(self):
        return TestcaseConfirmImportForm

    def get_import_data_kwargs(self,request, form, *args, **kwargs):
        if isinstance(form, (TestcaseImportForm,TestcaseConfirmImportForm)):
            if form.is_valid():
                project = form.cleaned_data['project']
                group = form.cleaned_data['group']
                kwargs.update({'project': project.id, 'group': group.id})
                return kwargs
        return super().get_import_data_kwargs(request, form=form, *args, **kwargs)

    def get_form_kwargs(self, form, *args, **kwargs):
        # pass on `author` to the kwargs for the custom confirm form
        if isinstance(form, (TestcaseImportForm,TestcaseConfirmImportForm)):
            if form.is_valid():
                project = form.cleaned_data['project']
                group = form.cleaned_data['group']
                kwargs.update({'project': project.id,'group': group.id})
        return kwargs

    def runcase(self,request,query_set):
        '''
        通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
        :param request:
        :param query_set:
        :return:
        '''
        post = request.POST
        baseurl = BASEURL.objects.get(id=post.get('baseurl'))
        sleeptime = post.get('sleeptime')
        try:
            run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
            # scheduler添加任务异步在后台运行测试用例
            scheduler.add_job(run_case, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[query_set,baseurl.url,int(sleeptime)])
        except Exception as e:
            return JsonResponse(data={
                'status': 'error',
                'msg': f'异常！{e}'
            })
        return JsonResponse(data={
            'status': 'success',
            'msg': '处理成功！'
        })
    runcase.short_description = '运行选中用例'
    runcase.layer = {
        # 这里指定对话框的标题
        'title': '运行用例',
        # 提示信息
        'tips': '待编辑',
        # 确认按钮显示文本
        'confirm_button': '确定',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",

        'params': [
            {
                'type': 'select',
                'key': 'baseurl',
                'label': '测试环境',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'options': [{'key': obj['id'], 'label': obj['name']} for obj in BASEURL.objects.all().values()]
            },
            {
                'type': 'input',
                'key': 'sleeptime',
                'label': '运行延时',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'}
        ]
    }

class Testcaselistinline(admin.TabularInline):
    '''
    排序运行测试用例的内联关系
    '''
    model = Testcaselist
    extra = 0
    autocomplete_fields = ['testcase']

def run_suite(query_set,baseurl,sleeptime,runargs,reruns,reruns_delay):
    '''
    通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
    :param query_set:
    :return:
    '''
    for obj in query_set:
        # 获取套件所有的测试用例，结果为[[{套件1用例},...],[{套件2用例},...]]
        testdata = get_suitedata(obj,baseurl,sleeptime)
        casenum = obj.case.count()
        testreport = run_data(num=casenum, data=[testdata],args=runargs,reruns=reruns,reruns_delay=reruns_delay)
        testreport.testsuite.add(obj)
        for case in obj.case.all():
            testreport.testcases.add(case)
            case.runtime = timezone.now()
            case.save()
        testreport.save()
        obj.runtime = timezone.now()
        obj.save

class TESTSUITEResource(resources.ModelResource):
    class Meta:
        model = TESTSUITE
        exclude = ('updatetime','createtime')

@admin.register(TESTSUITE)
class TESTSUITEAdmin(ImportExportActionModelAdmin, AjaxAdmin):
    resource_class = TESTSUITEResource
    list_display = ['name','createtime','creater','get_testcase','isorder','edit']
    actions = ['gen_yaml','runsuite']
    filter_horizontal = ['case']
    exclude = ['creater','runtime']
    inlines = [Testcaselistinline,]
    list_editable = ('isorder',)
    fields_options = {
        'edit': {
            'fixed': 'left'
        }
    }


    def formfield_for_manytomany(self, db_field, request, **kwargs):
        '''
        用例集多选框仅展示有效的测试用例
        :param db_field:
        :param request:
        :param kwargs:
        :return:
        '''
        if db_field.name == "case":
            kwargs["queryset"] = Testcase.objects.filter(isValid=True).order_by('api__code')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.creater = request.user
        super().save_model(request, obj, form, change)

    def get_testcase(self,obj):
        if obj.isorder is False:
            return obj.case.all().count()
        else:
            return obj.testcaselist_set.all().count()
    get_testcase.short_description = '用例数量'

    def edit(self,obj):
        # 获取测试套件内的用例对象列表拼接成字符串
        if obj.isorder == False:
            caselist = obj.case.all()
        else:
            caselist = obj.testcaselist_set.all()
        cids = ''
        for case in caselist:
            cids = cids + str(case.id) + ','
        caselisturl = reverse('admin:apitest_testcase_changelist') + '?id__in=' + cids[:-1]
        # 获取最后一次运行的测试报告
        if obj.suite_report.count() != 0:
            lastreports = TESTREPORT.objects.filter(testsuite=obj).latest('testtime')
            reporturl = lastreports.file.url
            logurl = lastreports.logfile.url
            reporthtml = format_html('<a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a> \
            <a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a> \
        <a href="{}"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a></div>', \
                                     reporturl, '查看报告', \
                                     logurl, '查看日志', \
                                     caselisturl, '查看用例')
        else:
            reporthtml = ''
        return reporthtml
    edit.short_description = '操作'

    def gen_yaml(self,request,query_set):
        '''
        获取选中测试集合中的用例数据拼接为数组
        :param request:
        :param query_set:
        :return:
        '''
        testcases = []
        for obj in query_set:
            # 获取套件所有的测试用例，结果为[[{套件1用例},...],[{套件2用例},...]]
            rundatas = get_suitedata(obj)
            testcases.append(rundatas)
        try:
            write_case(f'{filedir}/runner/data/test.yaml', testcases)
        except Exception as e:
            self.message_user(request,'发生异常' + str(e))
        self.message_user(request, '测试文件已生成')
    gen_yaml.short_description = '生成文件'

    def runsuite(self,request,query_set):
        '''
        后台按照排序依次运行所有测试套件，并生成测试报告及测试报告对象
        :param request:
        :param query_set:
        :return:
        '''
        try:
            post = request.POST
            baseurl = BASEURL.objects.get(id=post.get('baseurl'))
            runargs = [arg.split(' ')[0] for arg in post.get('runargs').split(',')]
            run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
            # scheduler添加任务异步在后台运行测试用例
            scheduler.add_job(run_suite, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[query_set,baseurl.url,post.get('sleeptime'),runargs,post.get('reruns'),post.get('reruns_delay')])
        except Exception as e:
            return JsonResponse(data={
                'status': 'error',
                'msg': f'异常！{e}'
            })
        return JsonResponse(data={
            'status': 'success',
            'msg': '处理成功！'
        })
    runsuite.short_description = '运行选中套件'
    runsuite.layer = {
            # 这里指定对话框的标题
            'title': '运行套件',
            # 提示信息
            'tips': '待编辑',
            # 确认按钮显示文本
            'confirm_button': '确定',
            # 取消按钮显示文本
            'cancel_button': '取消',

            # 弹出层对话框的宽度，默认50%
            'width': '40%',

            # 表单中 label的宽度，对应element-ui的 label-width，默认80px
            'labelWidth': "80px",

            'params': [
                {
                    'type': 'select',
                    'key': 'baseurl',
                    'label': '测试环境',
                    'width': '200px',
                    # size对应elementui的size，取值为：medium / small / mini
                    'size': 'small',
                    'options': [{'key': obj['id'], 'label': obj['name']} for obj in BASEURL.objects.all().values()]
                },
                {
                    'type': 'input',
                    'key': 'sleeptime',
                    'label': '运行延时',
                    'width': '200px',
                    # size对应elementui的size，取值为：medium / small / mini
                    'size': 'small',
                    'value': '0'},
                {
                    'type': 'checkbox',
                    'key': 'runargs',
                    # 必须指定默认值
                    'value': [],
                    'label': '运行参数',
                    'options': [{'key': obj['id'], 'label': obj['name'] + ' ' + obj['description']} for obj in Argument.objects.all().values()]
                },
                {
                    'type': 'input',
                    'key': 'reruns',
                    'label': '失败重跑次数',
                    'width': '200px',
                    # size对应elementui的size，取值为：medium / small / mini
                    'size': 'small',
                    'value': '0'},
                {
                    'type': 'input',
                    'key': 'reruns_delay',
                    'label': '重跑间隔时间',
                    'width': '200px',
                    # size对应elementui的size，取值为：medium / small / mini
                    'size': 'small',
                    'value': '0'}
            ]
        }

def run_batch(query_set,baseurl,sleeptime,runargs,reruns,reruns_delay,ispostmail):
    for batch in query_set:
        testbatch = []
        for obj in batch.testsuite.all():
            testsuite = get_suitedata(obj,baseurl,sleeptime)
            testbatch.extend(testsuite)
        casenum = len(testbatch)
        testreport = run_data(num=casenum, data=[testbatch],args=runargs,reruns=reruns,reruns_delay=reruns_delay)
        for suite in batch.testsuite.all():
            testreport.testsuite.add(suite)
            if suite.isorder == False:
                runcases = suite.case.all()
            else:
                runcases = suite.testcaselist_set.all()
                runcases = [case.testcase for case in runcases]
            for case in runcases:
                testreport.testcases.add(case)
                case.runtime = timezone.now()
                case.save()
        testreport.testbatch = batch
        testreport.save()
        obj.runtime = timezone.now()
        obj.save()
        if ispostmail == 'true':
            postmail('127.0.0.1','605662545@qq.com','605662545@qq.com',testreport)

class TestbatchResource(resources.ModelResource):
    class Meta:
        model = Testbatch
        exclude = ('updatetime','createtime')

@admin.register(Testbatch)
class TestbatchAdmin(ImportExportActionModelAdmin, AjaxAdmin):
    resource_class = TestbatchResource
    list_display = ['name','creater','createtime','runtime','edit']
    filter_horizontal = ['testsuite']
    actions = ['gen_yaml','runbatch','jenkinsrun']
    exclude = ('runtime','creater',)
    fields_options = {
        'edit': {
            'fixed': 'left'
        }
    }

    def save_model(self, request, obj, form, change):
        if change is not True:
            obj.creater = request.user
        super().save_model(request, obj, form, change)

    def gen_yaml(self,request,query_set):
        '''
        获取选中测试集合中的用例数据拼接为数组
        :param request:
        :param query_set:
        :return:
        '''
        testcases = []
        for batch in query_set:
            for obj in batch.testsuite.all():
                rundatas = get_suitedata(obj)
                testcases.append(rundatas)
        try:
            write_case(f'{filedir}/runner/data/test.yaml', testcases)
        except Exception as e:
            self.message_user(request,'发生异常' + str(e))
        self.message_user(request, '测试文件已生成')
    gen_yaml.short_description = '生成文件'

    def edit(self,obj):
        # 获取所有测试套件列表拼接字符串
        suitelist = obj.testsuite.all()
        sids = ''
        for suite in suitelist:
            sids = sids + str(suite.id) + ','
        suitelisturl = reverse('admin:apitest_testsuite_changelist') + '?id__in=' + sids[:-1]
        # 获取测试报告文件路径
        if obj.testreport_set.count() != 0:
            lastreports = TESTREPORT.objects.filter(testbatch=obj).latest('testtime')
            reporturl = lastreports.file.url
            logurl = lastreports.logfile.url
            reporthtml = format_html('<a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a> \
            <a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a> \
                                     <a href="{}"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a>',\
                                    reporturl, '查看报告', \
                                     logurl, '查看日志', \
                                    suitelisturl,'查看套件')
        else:
            reporthtml = ''
        return reporthtml
    edit.short_description = '操作'

    def runbatch(self,request,query_set):
        '''
        通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
        :param request:
        :param query_set:
        :return:
        '''
        try:
            post = request.POST
            baseurl = BASEURL.objects.get(id=post.get('baseurl'))
            runargs = [arg.split(' ')[0] for arg in post.get('runargs').split(',')]
            run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
            # scheduler添加任务异步在后台运行测试用例
            scheduler.add_job(run_batch, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[query_set,baseurl.url,post.get('sleeptime'),runargs,post.get('reruns'),post.get('reruns_delay'),post.get('ispostmail')])
        except Exception as e:
            return JsonResponse(data={
                'status': 'error',
                'msg': f'异常！{e}'
            })
        return JsonResponse(data={
            'status': 'success',
            'msg': '处理成功！'
        })
    runbatch.short_description = '运行选中批次'
    runbatch.layer = {
        # 这里指定对话框的标题
        'title': '运行批次',
        # 提示信息
        'tips': '待编辑',
        # 确认按钮显示文本
        'confirm_button': '确定',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",

        'params': [
            {
                'type': 'select',
                'key': 'baseurl',
                'label': '测试环境',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'require': True,
                'options': [{'key': obj['id'], 'label': obj['name']} for obj in BASEURL.objects.all().values()]
            },
            {
                'type': 'input',
                'key': 'sleeptime',
                'label': '运行延时',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'},
            {
                'type': 'checkbox',
                'key': 'runargs',
                # 必须指定默认值
                'value': [],
                'label': '运行参数',
                'options': [{'key': obj['id'], 'label': obj['name'] + ' ' + obj['description']} for obj in
                            Argument.objects.all().values()]
            },
            {
                'type': 'input',
                'key': 'reruns',
                'label': '失败重跑次数',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'},
            {
                'type': 'input',
                'key': 'reruns_delay',
                'label': '重跑间隔时间',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'},
            {
                'type': 'switch',
                'key': 'ispostmail',
                'label': '发送邮件'
            }
        ]
    }

    def jenkinsrun(self,request,query_set):
        '''
        调用jenkins的构建接口
        :param request:
        :param query_set:
        :return:
        '''

        for batch in query_set:

            try:
                post = request.POST
                testbatch = []
                baseurl = BASEURL.objects.get(id=post.get('baseurl'))
                for obj in batch.testsuite.all():
                    testsuite = get_suitedata(obj, baseurl.url, post.get('sleeptime') )
                    testbatch.extend(testsuite)
                write_case(f'{filedir}/runner/data/test.yaml', [testbatch])
                # 创建新jenkins构建
                server = jenkins.Jenkins(url='http://127.0.0.1:8888/', username='admin', password='z111111')
                last_build_number = server.get_job_info('apitest')['lastCompletedBuild']['number']
                this_build_number = last_build_number + 1
                configdata = server.get_job_config('apitest')
                args = ','.join([arg.split(' ')[0] for arg in post.get('runargs').split(',')])
                build_args = {'args':args,'extra_args':f"--reruns={post.get('reruns')} --reruns-delay={post.get('reruns_delay')} --log-file={filedir}/data/jenkinslogs/{this_build_number}.log"}
                server.build_job('apitest', parameters = build_args, token='111111')
                Jenkinsreport.objects.create(number=this_build_number,batch=batch)
            except Exception as e:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': f'异常！{e}'
                })
            return JsonResponse(data={
                'status': 'success',
                'msg': '运行成功！'
            })
    jenkinsrun.short_description = 'jenkins运行批次'
    jenkinsrun.layer = {
        # 这里指定对话框的标题
        'title': 'jenkins运行批次',
        # 提示信息
        'tips': '待编辑',
        # 确认按钮显示文本
        'confirm_button': '确定',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",

        'params': [
            {
                'type': 'select',
                'key': 'baseurl',
                'label': '测试环境',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'require': True,
                'options': [{'key': obj['id'], 'label': obj['name']} for obj in BASEURL.objects.all().values()]
            },
            {
                'type': 'input',
                'key': 'sleeptime',
                'label': '运行延时',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'},
            {
                'type': 'checkbox',
                'key': 'runargs',
                # 必须指定默认值
                'value': [],
                'label': '运行参数',
                'options': [{'key': obj['id'], 'label': obj['name'] + ' ' + obj['description']} for obj in
                            Argument.objects.all().values()]
            },
            {
                'type': 'input',
                'key': 'reruns',
                'label': '失败重跑次数',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'},
            {
                'type': 'input',
                'key': 'reruns_delay',
                'label': '重跑间隔时间',
                'width': '200px',
                # size对应elementui的size，取值为：medium / small / mini
                'size': 'small',
                'value': '0'}
        ]
    }

@admin.register(Jenkinsreport)
class JenkinsreportAdmin(admin.ModelAdmin):
    list_display = ['number','url','batch','runtime','result','receivetime','edit']
    readonly_fields = ['number','url','batch','duration','runtime','result','receivetime']
    actions = ['refresh']

    def edit(self,obj):
        # 获取所有测试套件列表拼接字符串
        return format_html('<a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a> \
                           <a href="{}"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a>', \
                           obj.jenkinslogfile.url, '查看运行日志', \
                                    f'/getjenkinslog/{obj.id}','查看日志')
    edit.short_description = '操作'

    def refresh(self,request,query_set):
        try:
            for obj in query_set:
                # jenkins API获取构建信息保存入库
                server = jenkins.Jenkins(url='http://127.0.0.1:8888/', username='admin', password='z111111')
                result = server.get_build_info('apitest',obj.number)
                duration = datetime.timedelta(microseconds=result['duration'])
                runtime = datetime.datetime.fromtimestamp(float(result['timestamp']/1000))
                if result['result'] == 'SUCCESS':
                    with open(f'{filedir}/data/jenkinslogs/{obj.number}.log', 'r', encoding='utf-8') as f:
                        jlogfile = File(f)
                        jlogfile.name = jlogfile.name.split('jenkinslogs/')[1]
                        obj.jenkinslogfile = jlogfile
                        obj.save()
                Jenkinsreport.objects.filter(id=obj.id).update(url=result['url'],duration=duration,runtime=runtime,result=result['result'])
        except Exception as e:
            self.message_user(request,f'异常！{e}')
        self.message_user(request,'更新成功！')
    refresh.short_description = '更新'

@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ['name']

    def has_module_permission(self,request):
        return False

TESTREPORTparams = [p.attname for p in TESTREPORT._meta.fields][1:]
for k,v in TESTREPORT._meta.fields_map.items():
    TESTREPORTparams.append(re.findall("TESTREPORT_(.*?)\+",v.name)[0])

@admin.register(TESTREPORT)
class TESTREPORTAdmin(admin.ModelAdmin):
    list_display = ['reportname', 'testtime', 'testnum', 'result', 'suc', 'fail','edit']
    list_filter = ['testsuite']
    view_on_site = True
    params = TESTREPORTparams
    fields = params
    readonly_fields = params
    fields_options = {
        'edit': {
            'fixed': 'left'
        }
    }

    def edit(self,obj):
        # 获得失败用例列表
        failcaselist = obj.failcase.all()
        cids = ''
        for case in failcaselist:
            cids = cids + str(case.id) + ','

        if cids == '':
            casefailhtml = format_html('</div>')
        else:
            casefailhtml = format_html('<button type="button" class="el-button el-button--default el-button--mini"><a href="{}">{}</a></button> \
            <button type="button" class="el-button el-button--default el-button--mini"><a href="{}">{}</a></button>',\
                               reverse('admin:apitest_testcase_changelist') + '?id__in=' +  cids[:-1],'查看失败用例',\
                               rvs('testreport-detail',args=[obj.id]) + 'runfail','失败重跑',)
        return format_html(
            '<button type="button" class="el-button el-button--default el-button--mini"><a href="{}" target="_blank">{}</a></button> \
            <a href="{}" target="_blank"><button type="button" class="el-button el-button--default el-button--mini">{}</button></a>', \
            obj.file.url, '查看报告', obj.logfile.url, '下载日志') + casefailhtml
    edit.short_description = '操作'

    def delete_model(self,request,obj):
        '''删除对象同时删除本地文件'''
        reportfile = obj.file.url.rsplit('/',1)[0]
        if os.path.exists(filedir+reportfile):
            shutil.rmtree(filedir+reportfile)
