import csv
import datetime
import random
import re
import shutil
import time

import jenkins
import jsonpath
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import MultipleObjectsReturned
from django.core.files import File
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from openpyxl import Workbook
from rest_framework.reverse import reverse as rvs
from .forms import CsvImportForm
from .models import *
from .datahandle import *
# Register your models here.
from .runner import testrunner


# admin.site.unregister(User)
# admin.site.unregister(Group)
from .runner.scheduler import scheduler

AdminSite.site_header = "datest接口自动化测试平台"
AdminSite.index_title = "api测试"
filedir = os.path.dirname(__file__)
@admin.register(Api)
class ApiAdmin(admin.ModelAdmin):
    list_display = ['id','name','creater','project','method','group','isValid','url','get_casenum','edit']
    search_fields = ['name']
    filter_horizontal = ['header']
    list_display_links = ['edit']
    list_filter = ['group','project','isValid']
    actions = ['get_excel','unvalid']
    save_on_top = True
    exclude = ('creater',)
    list_editable = ('isValid','url')

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
        return format_html('<a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}">',reverse('admin:apitest_api_change', args=(obj.id,)),'编辑',reverse('admin:apitest_api_delete', args=(obj.id,)),'删除')
    edit.short_description = '操作'

    def get_casenum(self,obj):
        casenum = obj.testcase_set.count()
        return format_html('<a href="{}" style="text-decoration:underline">{}',f'/admin/apitest/testcase/?api__id__exact={obj.id}' , str(casenum))
    get_casenum.short_description = '用例数'

    def unvalid(self, request, query_set):
        query_set.update(isValid=False)
    unvalid.short_description = '失效'

    def get_excel(self, request, query_set):
        '''
        导出xls文件
        :param request:
        :param query_set:
        :return:
        '''
        fieldsname = [field.name for field in self.model._meta.fields]
        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment ; filename = "api.xlsx"'
        wb = Workbook()
        ws = wb.active
        ws.append(fieldsname)
        for obj in query_set:
            rowvalue = []
            for field in fieldsname:
                rowvalue.append(f'{getattr(obj,field)}')
            row = ws.append(rowvalue)
        wb.save(response)
        return response
    get_excel.short_description = '导出'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','creater','sonpj','banben']
    exclude = ('creater',)

    def save_model(self, request, obj, form, change):
        projectpath = filedir + '/runner/projectdata/'
        if not os.path.exists(projectpath):
            os.mkdir(projectpath)
        if not change:
            obj.creater = request.user
            super().save_model(request, obj, form, change)
            if not os.path.exists(projectpath + obj.name):
                os.mkdir(projectpath + obj.name)
            shutil.copyfile(filedir + '/runner/debugtalk.py', projectpath + obj.name + '/debugtalk.py')
            with open(projectpath + obj.name + '/debugtalk.py', 'r+', encoding='utf-8') as f:
                content = f.read()
            DebugTalk.objects.create(project=obj,file='/runner/projectdata/' + obj.name + '/debugtalk.py',content=content)
        super().save_model(request, obj, form, change)


@admin.register(DebugTalk)
class DebugTalkAdmin(admin.ModelAdmin):
    list_display = ['project','file','edit']

    def edit(self,obj):
        return format_html('<a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}">',rvs('debugtalk-detail',args=[obj.id]) + 'edit','编辑',reverse('admin:apitest_debugtalk_delete', args=(obj.id,)),'删除')
    edit.short_description = '操作'

    def delete_model(self,request,obj):
        '''删除对象同时删除本地文件'''
        super().delete_model(request,obj)
        debugtalkfile = obj.file.rsplit('/',1)[0]
        if os.path.exists(filedir+debugtalkfile):
            shutil.rmtree(filedir+debugtalkfile)

@admin.register(ApiGroup)
class ApiGroupAdmin(admin.ModelAdmin):
    list_display = ['name']

    def has_module_permission(self,request):
        return False

@admin.register(TestcaseGroup)
class TestcaseGroupAdmin(admin.ModelAdmin):
    exclude = ['creater',]

    def has_module_permission(self,request):
        return False

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
    model = HeaderParam
    extra = 0

@admin.register(Headerkey)
class HeaderkeyAdmin(admin.ModelAdmin):
    search_fields = ['value']

    def has_module_permission(self,request):
        return False

@admin.register(Headerval)
class HeadervalAdmin(admin.ModelAdmin):
    search_fields = ['value']

    def has_module_permission(self,request):
        return False

class FormdataParaminline(admin.TabularInline):
    model = FormdataParam
    extra = 0
    autocomplete_fields = ['paramkey','paramval']

class AssertParaminline(admin.TabularInline):
    model = AssertParam
    extra = 0
    autocomplete_fields = ['paramkey','paramval']

class RequestParaminline(admin.TabularInline):
    model = RequestParam
    extra = 0
    autocomplete_fields = ['paramkey', 'paramval']

class Runparaminline(admin.TabularInline):
    model = Runparam
    extra = 0

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

@admin.register(Assertkey)
class AssertkeyAdmin(admin.ModelAdmin):
    search_fields = ['value']

    def has_module_permission(self,request):
        return False

    def get_changeform_initial_data(self, request):
        return {'value': 'body.'}


@admin.register(Assertval)
class AssertvalAdmin(admin.ModelAdmin):
    search_fields = ['value']

    def has_module_permission(self,request):
        return False

@admin.register(FUNC)
class FUNCAdmin(admin.ModelAdmin):
    list_display = ['name','description']

    def has_module_permission(self,request):
        return False

@admin.register(CALLFUNC)
class CALLFUNCAdmin(admin.ModelAdmin):
    list_display = ['name','description']

    def has_module_permission(self,request):
        return False

def run_back_case(query_set):
    casenum = query_set.all().count()
    passedall = 0
    failedall = 0
    try:
        for obj in query_set:
            thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
            testcase = get_casedata('运行测试用例', obj)
            if not os.path.exists(f'{filedir}/runner/data'):
                os.mkdir(f'{filedir}/runner/data')
            write_case(f'{filedir}/runner/data/test.yaml', [[testcase]])
            report = testrunner.pyrun(args='')
            testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
            os.environ.pop('TESTRESULT')
            result = testresult['result']
            failed = testresult['failed']
            passed = testresult['passed']
            with open(report + '/index.html', 'r', encoding='utf-8') as f:
                thisfile = File(f)
                thisfile.name = thisfile.name.split('report/')[1]
                testreport = TESTREPORT.objects.create(reportname=thisname, file=thisfile,testnum=casenum, result=result, suc=passed, fail=failed)
            for passedcase in testresult['passedcase']:
                testreport.succase.add(Testcase.objects.get(caseno=passedcase))
            for failedcase in testresult['failedcase']:
                testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
            testreport.testcases.add(obj)
            testreport.save()
            obj.runtime = timezone.now()
            passedall += passed
            failedall += failed
    except Exception as e:
        testreport = TESTREPORT.objects.create(reportname=thisname, testnum=casenum, result='N',errors=str(e))
        raise e

@admin.register(Testcase)
class TestcaseAdmin(admin.ModelAdmin):
    list_display = ['caseno','casename','creater','isValid', 'group', 'api', 'edit']
    list_display_links = ['edit']
    search_fields = ['caseno','casename']
    radio_fields = {"datamode": admin.HORIZONTAL}
    autocomplete_fields = ['api']
    inlines = [HeaderParaminline,RequestParaminline,FormdataParaminline, AssertParaminline,]
    save_on_top = True
    list_filter = ['group', 'project','callfunc','isValid']
    actions = ['get_excel','copy','get_caseyml','runcase','unvalid']
    fields = ('casename','group','baseurl','api','datamode','requestdata','setupfunc','teardownfunc','callfunc','isValid',)
    change_list_template = 'admin/apitest/testcase/option_changelist.html'
    list_per_page = 50
    readonly_fields = ('responsedata',)
    list_editable = ['isValid','api']

    def get_search_results(self, request, queryset, search_term):
        if request.path == '/admin/apitest/testcase/autocomplete/':
            queryset = queryset.filter(isValid=True)
        return super().get_search_results(request, queryset, search_term)

    def edit(self,obj):
        reportlink = ''
        reporturl = ''
        lastreports = TESTREPORT.objects.filter(testcases=obj).order_by('-testtime')
        if len(lastreports) != 0:
            return format_html(
                '<a href="{}" style="white-space:nowrap;" target="_blank"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"></a> <a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}"> <span style="float:left;margin-top:10px"><a href="{}" style="white-space:nowrap;" target="_blank"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"></input>',
                rvs('testcase-detail', args=[obj.id]) + 'postcase', '发送',
                reverse('admin:apitest_testcase_change', args=(obj.id,)), '编辑',
                reverse('admin:apitest_testcase_delete', args=(obj.id,)), '删除', lastreports[0].file.url, '查看报告')
        else:
            return format_html(
                '<a href="{}" style="white-space:nowrap;" target="_blank"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"></a> <a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}">',
                rvs('testcase-detail', args=[obj.id]) + 'postcase', '发送',
                reverse('admin:apitest_testcase_change', args=(obj.id,)), '编辑',
                reverse('admin:apitest_testcase_delete', args=(obj.id,)), '删除')
    edit.short_description = '操作'

    def unvalid(self, request, query_set):
        query_set.update(isValid=False)
    unvalid.short_description = '失效'

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.caseno = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1,1000))
            obj.project = obj.api.project
            obj.creater = request.user
        super().save_model(request, obj, form, change)

    def copy(self,request,query_set):
        for obj in query_set:
            oid = obj.id
            obj.id = None
            obj.caseno = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1, 1000))
            obj.save()
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
            for field in fieldsname:
                if getattr(obj,field) is not None:
                    rowvalue.append(f'{getattr(obj,field)}')
                else:
                    rowvalue.append('')
            for assdata in obj.assertparam_set.all():
                rowvalue.append(assdata.paramkey.value + '|' + assdata.paramval.value)
            row = ws.append(rowvalue)
        wb.save(response)
        return response
    get_excel.short_description = '导出'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/',self.import_excel),
        ]
        return my_urls + urls

    def import_excel(self, request):
        '''导出xls'''
        if request.method == 'POST':
            xfile = request.FILES['x_file'].file
            with open(filedir + '/data/uploadfile/temp.xls', 'wb') as f:
                f.write(xfile.read())
            testcases = get_exceldata(filedir + '/data/uploadfile/temp.xls')
            num = 0
            for data in testcases:
                caseno = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1,10000))
                project = Project.objects.get_or_create(name=data['project'],defaults = {'banben':'1'})
                group = TestcaseGroup.objects.get_or_create(name=data['group'],defaults = {'project':project[0]})
                baseurl = BASEURL.objects.get_or_create(url=data['baseurl'],defaults = {'name':'新建环境','project':project[0]})
                api = Api.objects.get(id=data['api'])
                def get_func(data,name,model):
                    if data[name] != '':
                        return model.objects.get(name = data[name])
                    else:
                        return None
                setupfunc = get_func(data,'setupfunc',FUNC)
                teardownfunc = get_func(data,'teardownfunc',FUNC)
                callfunc = get_func(data,'callfunc',CALLFUNC)
                testcaseobj = Testcase.objects.create(caseno = caseno,casename=data['casename'],project= project[0],group=group[0],api = api,isValid=True,baseurl=baseurl[0],datamode = data['datamode'],requestdata=data['requestdata'],creater=request.user,setupfunc=setupfunc,teardownfunc=teardownfunc,callfunc=callfunc)
                num += 1
                def addorget(mod, value):
                    try:
                        obj = mod.objects.get_or_create(value=value)
                        return obj[0]
                    except MultipleObjectsReturned as e:
                        obj = mod.objects.filter(value=value)
                        return obj[0]
                if data['headers'] != '':
                    for key,value in json.loads(data['headers']).items():
                        hkeyobj = addorget(Headerkey, key)
                        hvalobj = addorget(Headerval, value)
                        HeaderParam.objects.create(testcase=testcaseobj, paramkey=hkeyobj, paramval=hvalobj)
                for k,v in data.items():
                    if k.startswith('assert') and v is not '':
                        assertkey = v.split('|')[0]
                        assertvalue = v.split('|',1)[1]
                        hkeyobj = addorget(Assertkey, assertkey)
                        hvobj = addorget(Assertval, assertvalue)
                        AssertParam.objects.create(testcase=testcaseobj, paramkey=hkeyobj, paramval=hvobj)
            self.message_user(request, str(num) + "个用例批量导入成功")
            return redirect("..")
        form = CsvImportForm()
        return render(request, 'admin/csv_form.html', {'form': form})

    def gen_yml(self,request,query_set):
        '''
        获取选中用例的数据拼接为数组
        :param request:
        :param query_set:
        :return:
        '''
        testdata = []
        for obj in query_set:
            testcase = get_casedata('批量运行用例',obj)
            testdata.append(testcase)
        testcases = [testdata]
        return testcases

    def get_caseyml(self,request,query_set):
        '''
        根据gen_yml输出的数组在apitest/runner/data下生成yaml格式的测试用例文件
        :param request:
        :param query_set:
        :return:
        '''
        testcases = self.gen_yml(request,query_set)
        try:
            write_case(f'{filedir}/runner/data/test.yaml', testcases)
        except Exception as e:
            self.message_user(request, '发生异常' + str(e))
        self.message_user(request, '测试文件已生成')
    get_caseyml.short_description = '生成文件'

    def runcase(self,request,query_set):
        '''
        通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
        :param request:
        :param query_set:
        :return:
        '''
        try:
            run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
            scheduler.add_job(run_back_case, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[query_set])
        except Exception as e:
            self.message_user(request, '发生异常：' + str(e))
        self.message_user(request,str(list(query_set.values_list('caseno','casename'))) + f'测试用例运行，请稍后查看测试报告')
    runcase.short_description = '运行选中用例'

class Testcaselistinline(admin.TabularInline):
    model = Testcaselist
    extra = 0
    autocomplete_fields = ['testcase']

@admin.register(TESTSUITE)
class TESTSUITEAdmin(admin.ModelAdmin):
    list_display = ['name','createtime','creater','baseurl','get_testcase','isorder','edit']
    actions = ['gen_yaml','runsuite']
    filter_horizontal = ['case']
    exclude = ['creater','runtime']
    list_display_links = ['edit']
    inlines = [Testcaselistinline,]
    list_editable = ('baseurl','isorder')

    

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        '''
        formfield_for_manytomany可以重写该方法。
        :param db_field:
        :param request:
        :param kwargs:
        :return:
        '''
        if db_field.name == "case":
            kwargs["queryset"] = Testcase.objects.filter(isValid=True)
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
        if obj.isorder == False:
            caselist = obj.case.all()
        else:
            caselist = obj.testcaselist_set.all()
        cids = ''
        for case in caselist:
            cids = cids + str(case.id) + ','
        caselisturl = reverse('admin:apitest_testcase_changelist') + '?id__in=' + cids[:-1]
        if obj.suite_report.count() != 0:
            lastreports = TESTREPORT.objects.filter(testsuite=obj).latest('testtime')
            reporturl = lastreports.file.url
            return format_html(
                '<a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" target="_blank"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}"> ',
                rvs('testsuite-detail', args=[obj.id]) + 'runback', '后台运行', reporturl, '查看报告',
                caselisturl, '查看用例',
                reverse('admin:apitest_testsuite_change', args=(obj.id,)), '编辑',
                reverse('admin:apitest_testsuite_delete', args=(obj.id,)), '删除')
        else:
            return format_html(
                '<a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}">',
                rvs('testsuite-detail', args=[obj.id]) + 'runback', '后台运行',
                caselisturl, '查看用例',
                reverse('admin:apitest_testsuite_change', args=(obj.id,)), '编辑',
                reverse('admin:apitest_testsuite_delete', args=(obj.id,)), '删除')
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
        通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
        :param request:
        :param query_set:
        :return:
        '''
        thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
        passedall = 0
        failedall = 0
        for obj in query_set:
            testsuite = get_suitedata(obj)
            casenum = obj.case.count()
            args = obj.args.all().values_list('name')
            try:
                write_case(f'{filedir}/runner/data/test.yaml',[testsuite])
                runtime = timezone.now()
                report = testrunner.pyrun(args,obj.reruns,obj.reruns_delay)
                testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
                os.environ.pop('TESTRESULT')
                result = testresult['result']
                failed = testresult['failed']
                passed = testresult['passed']
                with open(report + '/index.html','r',encoding='utf-8') as f:
                    thisfile = File(f)
                    thisfile.name = thisfile.name.split('report/')[1]
                    testreport = TESTREPORT.objects.create(reportname=thisname, file=thisfile,testnum=casenum, result=result,suc=passed, fail=failed)
                for passedcase in testresult['passedcase']:
                    testreport.succase.add(Testcase.objects.get(caseno=passedcase))
                for failedcase in testresult['failedcase']:
                    testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
                testreport.testsuite.add(obj)
                for case in obj.case.all():
                    testreport.testcases.add(case)
                    case.runtime = timezone.now()
                    case.save()
                obj.runtime = timezone.now()
                obj.save()
                testreport.save()
                passedall += passed
                failedall += failed
            except Exception as e:
                self.message_user(request,'发生异常' + str(e))
                testreport  = TESTREPORT.objects.create(reportname=thisname, testnum=casenum, result='N', errors = str(e))
                raise e
        self.message_user(request, str(list(query_set.values_list('name'))) + f'测试运行完成，本次测试结果：{result}，测试用例成功数量{passedall}，测试用例失败数量{failedall}，请查看测试报告')
    runsuite.short_description = '运行套件'


@admin.register(Testbatch)
class TestbatchAdmin(admin.ModelAdmin):
    list_display = ['name','creater','createtime','runtime','edit']
    filter_horizontal = ['testsuite']
    actions = ['gen_yaml','runbatch','jenkinsrun']
    exclude = ('runtime','creater',)

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
        suitelist = obj.testsuite.all()
        sids = ''
        for suite in suitelist:
            sids = sids + str(suite.id) + ','
        suitelisturl = reverse('admin:apitest_testsuite_changelist') + '?id__in=' + sids[:-1]
        if obj.testreport_set.count() != 0:
            lastreports = TESTREPORT.objects.filter(testbatch=obj).latest('testtime')
            reporturl = lastreports.file.url
            return format_html(
                '<a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" target="_blank"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}">',
                rvs('testbatch-detail', args=[obj.id]) + 'runback', '后台运行',
                suitelisturl, '查看套件',
                reverse('admin:apitest_testbatch_change', args=(obj.id,)), '编辑', reporturl, '查看报告',
                reverse('admin:apitest_testbatch_delete', args=(obj.id,)), '删除')
        else:
            return format_html(
                '<a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}" style="white-space:nowrap;" ><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert;background:#ba2121" value="{}">',
                rvs('testbatch-detail', args=[obj.id]) + 'runback', '后台运行',
                suitelisturl, '查看套件',
                reverse('admin:apitest_testbatch_change', args=(obj.id,)), '编辑',
                reverse('admin:apitest_testbatch_delete', args=(obj.id,)), '删除')
    edit.short_description = '操作'

    def runbatch(self,request,query_set):
        '''
        通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
        :param request:
        :param query_set:
        :return:
        '''
        for batch in query_set:
            batch_reportname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + batch.name + '套件批次报告'
            passedall = 0
            failedall = 0
            testbatch = []
            for obj in batch.testsuite.all():
                testsuite = get_suitedata(obj)
                testbatch.extend(testsuite)
            casenum = len(testbatch)
            args = batch.args.all().values_list('name')
            try:
                write_case(f'{filedir}/runner/data/test.yaml',[testbatch])
                runtime = timezone.now()
                report = testrunner.pyrun(args,batch.reruns,batch.reruns_delay)
                testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
                os.environ.pop('TESTRESULT')
                result = testresult['result']
                failed = testresult['failed']
                passed = testresult['passed']
                with open(report + '/index.html','r',encoding='utf-8') as f:
                    thisfile = File(f)
                    thisfile.name = thisfile.name.split('report/')[1]
                    testreport = TESTREPORT.objects.create(reportname=batch_reportname,testbatch=batch, file=thisfile,testnum=casenum, result=result,suc=passed, fail=failed)
                for passedcase in testresult['passedcase']:
                    testreport.succase.add(Testcase.objects.get(caseno=passedcase))
                for failedcase in testresult['failedcase']:
                    testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
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
                obj.runtime = timezone.now()
                obj.save()
                testreport.save()
                passedall += passed
                failedall += failed
            except Exception as e:
                self.message_user(request,'发生异常' + str(e))
                testreport  = TESTREPORT.objects.create(reportname=batch_reportname, testnum=casenum,testbatch=batch, result='N', errors = str(e))
                raise e
        self.message_user(request, '批次测试运行完成，请查看测试报告')
    runbatch.short_description = '运行批次'

    def jenkinsrun(self,request,query_set):
        '''
        调用jenkins的构建接口
        :param request:
        :param query_set:
        :return:
        '''
        for batch in query_set:
            testbatch = []
            for obj in batch.testsuite.all():
                testsuite = get_suitedata(obj)
                testbatch.extend(testsuite)
            try:
                write_case(f'{filedir}/runner/data/test.yaml', [testbatch])
                server = jenkins.Jenkins(url='http://127.0.0.1:8888/', username='admin', password='z111111')
                last_build_number = server.get_job_info('apitest')['lastCompletedBuild']['number']
                this_build_number = last_build_number + 1
                server.build_job('apitest', token='111111')
                Jenkinsreport.objects.create(number=this_build_number,batch=batch)
                self.message_user(request, 'Jenkins已进行构建')
            except Exception as e:
                self.message_user(request,'发生异常' + str(e))
    jenkinsrun.short_description = 'jenkins运行套件'

@admin.register(Jenkinsreport)
class JenkinsreportAdmin(admin.ModelAdmin):
    list_display = ['number','url','batch','runtime','result','getresult','receivetime']

    def getresult(self,obj):
        server = jenkins.Jenkins(url='http://127.0.0.1:8888/', username='admin', password='z111111')
        result = server.get_build_info('apitest',obj.number)
        log = server.get_build_console_output('apitest',obj.number)
        duration = datetime.timedelta(microseconds=result['duration'])
        runtime = datetime.datetime.fromtimestamp(float(result['timestamp']/1000))
        Jenkinsreport.objects.filter(id=obj.id).update(url=result['url'],duration=duration,runtime=runtime,result=result['result'],output=log)
        return '已更新'

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
    list_display = ['reportname', 'testtime', 'testnum', 'result', 'suc', 'fail','filelink']
    list_filter = ['testsuite']
    view_on_site = True
    params = TESTREPORTparams
    fields = params
    readonly_fields = params
    list_display_links = ['filelink']

    def filelink(self,obj):
        failcaselist = obj.failcase.all()
        cids = ''
        for case in failcaselist:
            cids = cids + str(case.id) + ','
        if cids == '':
            caselisturl = ''
            caseliststr = '-'
        else:
            caselisturl = reverse('admin:apitest_testcase_changelist') + '?id__in=' +  cids[:-1]
            caseliststr = '查看失败用例'
        return format_html('<a href="{}" target="_blank"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}"> <a href="{}"><input type="button" class="default" style="padding:2px 2px;border-radius:revert" value="{}">',obj.file.url,'查看报告',reverse('admin:apitest_testreport_change', args=(obj.id,)),'详情',caselisturl,caseliststr)
    filelink.short_description = '操作'

    def delete_model(self,request,obj):
        '''删除对象同时删除本地文件'''
        reportfile = obj.file.url.rsplit('/',1)[0]
        if os.path.exists(filedir+reportfile):
            shutil.rmtree(filedir+reportfile)
