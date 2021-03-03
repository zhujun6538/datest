import csv
import datetime
import random
import re
import shutil

import jenkins
import jsonpath
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.core.exceptions import MultipleObjectsReturned
from django.core.files import File
from django.db import transaction
from django.forms import formset_factory, forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import format_html
from openpyxl import Workbook

from .forms import CsvImportForm
from .models import *
from .datahandle import *
# Register your models here.
from .runner import testrunner


# admin.site.unregister(User)
# admin.site.unregister(Group)
AdminSite.site_header = "证通自动化测试后台"
AdminSite.index_title = "api测试"
filedir = os.path.dirname(__file__)
@admin.register(Api)
class ApiAdmin(admin.ModelAdmin):
    list_display = ['code','name','project','method','group','isValid','url','get_casenum','edit']
    search_fields = ['name','code']
    list_display_links = ['edit']
    list_filter = ['group','project']
    actions = ['get_excel']
    change_list_template = 'admin/apitest/api/option_changelist.html'
    save_on_top = True

    def edit(self,obj):
        return format_html('<a href="{}">{}</a>',reverse('admin:apitest_api_change', args=(obj.id,)),'编辑')
    edit.short_description = '操作'

    def get_casenum(self,obj):
        return obj.testcase_set.count()
    get_casenum.short_description = '用例数'

    def get_excel(self, request, query_set):
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

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/',self.import_excel),
        ]
        return my_urls + urls

    def import_excel(self, request):
        if request.method == 'POST':
            xfile = request.FILES['x_file'].file
            with open(filedir + '\\data\\uploadfile\\temp.xls', 'wb') as f:
                f.write(xfile.read())
            apidatas = get_exceldata(filedir + '\\data\\uploadfile\\temp.xls')
            apinum = 0
            for data in apidatas:
                project = Project.objects.get_or_create(name=data['project'],defaults = {'banben':'1'})
                group = ApiGroup.objects.get_or_create(name=data['group'],defaults = {'project':project[0]})
                headers = json.loads(data['headers'])
                api = Api.objects.get_or_create(code=data['code'],name=data['name'],defaults = {'project':project[0],'group':group[0],'method' : data['method'],'description':data['description'],'isValid':True,'url':data['url']})
                for key,value in headers.items():
                    header = Header.objects.get_or_create(key=key,value=value)
                    api[0].header.add(header[0])
                api[0].save()
                apinum += 1
            self.message_user(request, str(apinum) + "个API批量导入成功")
            return redirect("..")
        form = CsvImportForm()
        return render(request, 'admin/csv_form.html', {'form': form})

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','sonpj','banben']

@admin.register(ApiGroup)
class ApiGroupAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(TestcaseGroup)
class TestcaseGroupAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ['key','value']

@admin.register(BASEURL)
class BASEURLAdmin(admin.ModelAdmin):
    list_display = ['name','url']

class HeaderParaminline(admin.TabularInline):
    model = HeaderParam
    extra = 1

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

class AssertParaminline(admin.TabularInline):
    model = AssertParam
    extra = 1
    autocomplete_fields = ['paramkey','paramval']

class RequestParaminline(admin.TabularInline):
    model = RequestParam
    extra = 1
    autocomplete_fields = ['paramkey', 'paramval']

class Runparaminline(admin.TabularInline):
    model = Runparam
    extra = 1

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

@admin.register(Testcase)
class TestcaseAdmin(admin.ModelAdmin):
    list_display = ['caseno','casename', 'group', 'isrun', 'api', 'createtime', 'runtime', 'edit']
    list_display_links = ['edit']
    search_fields = ['caseno','casename']
    radio_fields = {"isrun": admin.HORIZONTAL, "datamode": admin.HORIZONTAL}
    autocomplete_fields = ['api']
    inlines = [HeaderParaminline,RequestParaminline, AssertParaminline,Runparaminline]
    save_on_top = True
    list_filter = ['group', 'project','callfunc']
    actions = ['get_excel','copy','get_caseyml','runcase']
    fields = ('casename','group','isrun','baseurl','api','datamode','requestdata','setupfunc','callfunc','responsedata')
    change_list_template = 'admin/apitest/testcase/option_changelist.html'
    list_per_page = 50
    readonly_fields = ('responsedata',)

    def edit(self,obj):
        reportlink = '-'
        reporturl = '#'
        lastreports = TESTREPORT.objects.filter(testcases=obj).order_by('-testtime')
        if len(lastreports) != 0:
            reportlink = '查看报告'
            reporturl = lastreports[0].file.url
        return format_html('<a href="{}" style="white-space:nowrap;">{}</a> <a href="{}" style="white-space:nowrap;" target="_blank">{}</a>',reverse('admin:apitest_testcase_change', args=(obj.id,)),'编辑',reporturl,reportlink)
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
            oldobj = Testcase.objects.get(id = oid)
            for par in list(oldobj.headerparam_set.all()):
                HeaderParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.requestparam_set.all()):
                RequestParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.assertparam_set.all()):
                AssertParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval,mode=par.mode)
    copy.short_description = '复制'

    def get_excel(self, request, query_set):
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
        if request.method == 'POST':
            xfile = request.FILES['x_file'].file
            with open(filedir + '\\data\\uploadfile\\temp.xls', 'wb') as f:
                f.write(xfile.read())
            testcases = get_exceldata(filedir + '\\data\\uploadfile\\temp.xls')
            num = 0
            for data in testcases:
                caseno = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1,10000))
                project = Project.objects.get_or_create(name=data['project'],defaults = {'banben':'1'})
                group = TestcaseGroup.objects.get_or_create(name=data['group'],defaults = {'project':project[0]})
                baseurl = BASEURL.objects.get_or_create(url=data['baseurl'],defaults = {'name':'新建环境','project':project[0]})
                api = Api.objects.get(code=data['api'])
                if data['setupfunc'] != '':
                    setupfunc = FUNC.objects.get(name = data['setupfunc'])
                else:
                    setupfunc = None
                if data['callfunc'] != '':
                    callfunc = CALLFUNC.objects.get(name=data['callfunc'])
                else:
                    callfunc = None
                testcaseobj = Testcase.objects.create(caseno = caseno,casename=data['casename'],project= project[0],group=group[0],api = api,isrun='Y',baseurl=baseurl[0],datamode = data['datamode'],requestdata=data['requestdata'],creater=request.user,setupfunc=setupfunc,callfunc=callfunc)
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
        testdata = []
        for obj in query_set:
            testcase = get_casedata('批量运行用例',obj)
            testdata.append(testcase)
        testcases = [testdata]
        return testcases

    def get_caseyml(self,request,query_set):
        testcases = self.gen_yml(request,query_set)
        try:
            write_case(f'{filedir}/runner/data/test.yaml', testcases)
        except Exception as e:
            self.message_user(request, '发生异常' + str(e))
        self.message_user(request, '测试文件已生成')
    get_caseyml.short_description = '生成文件'

    def runcase(self,request,query_set):
        casenum = query_set.all().count()
        caseids = query_set.values_list('id', flat=True)
        Testcase.objects.select_for_update().filter(id__in = caseids)
        with transaction.atomic():
            testcases = self.gen_yml(request,query_set)
            try:
                for obj in query_set:
                    testcase = get_casedata('运行测试用例', obj)
                    write_case(f'{filedir}/runner/data/test.yaml', [[testcase]])
                    report = testrunner.pyrun(args='')
                    testresult = json.loads(os.environ.get('TESTRESULT'),encoding='utf-8')
                    result = testresult['result']
                    failed = testresult['failed']
                    passed = testresult['passed']
                    thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
                    with open(report + '/index.html','r',encoding='utf-8') as f:
                        thisfile = File(f)
                        thisfile.name = thisfile.name.split('report/')[1]
                        testreport = TESTREPORT.objects.create(reportname=thisname,runner=request.user, file=thisfile,testnum=casenum,result=result,suc=passed, fail=failed)
                        for passedcase in testresult['passedcase']:
                            testreport.succase.add(Testcase.objects.get(caseno=passedcase))
                        for failedcase in testresult['failedcase']:
                            testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
                    testreport.testcases.add(obj)
                    testreport.save()
                    obj.runtime = timezone.now()
            except Exception as e:
                self.message_user(request,'发生异常' + str(e))
                testreport = TESTREPORT.objects.create(reportname=thisname, testnum=casenum, result='N',runner=request.user, errors=str(e))
            self.message_user(request, '测试运行完成，请查看测试报告')
    runcase.short_description = '运行所有用例'

class Testcaselistinline(admin.TabularInline):
    model = Testcaselist
    extra = 1
    autocomplete_fields = ['testcase']

@admin.register(TESTSUITE)
class TESTSUITEAdmin(admin.ModelAdmin):
    list_display = ['name','baseurl','ctime','creater','get_testcase','edit']
    actions = ['gen_yaml','runsuite','jrunsuite']
    filter_horizontal = ['case']
    exclude = ['creater','runtime']
    list_display_links = ['edit']
    inlines = [Testcaselistinline,]

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
        if obj.suite_report.count() != 0:
            lastreports = TESTREPORT.objects.filter(testsuite=obj).latest('testtime')
            reporturl = lastreports.file.url
            return format_html('<a href="{}" style="white-space:nowrap;" >{}</a> <a href="{}" style="white-space:nowrap;" target="_blank">{}</a>',reverse('admin:apitest_testsuite_change', args=(obj.id,)),'编辑',reporturl,'查看报告')
        else:
            return format_html('<a href="{}" style="white-space:nowrap;" >{}</a>',reverse('admin:apitest_testsuite_change', args=(obj.id,)), '编辑')
    edit.short_description = '操作'

    def gen_yaml(self,request,query_set):
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
        thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
        for obj in query_set:
            testsuite = get_suitedata(obj)
            casenum = obj.case.count()
            args = obj.args.all().values_list('name')
            try:
                write_case(f'{filedir}/runner/data/test.yaml',[testsuite])
                report = testrunner.pyrun(args,obj.reruns,obj.reruns_delay)
                testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
                os.environ.pop('TESTRESULT')
                result = testresult['result']
                failed = testresult['failed']
                passed = testresult['passed']
                with open(report + '/index.html','r',encoding='utf-8') as f:
                    thisfile = File(f)
                    thisfile.name = thisfile.name.split('report/')[1]
                    testreport = TESTREPORT.objects.create(reportname=thisname, runner=request.user, file=thisfile,testnum=casenum, result=result,suc=passed, fail=failed)
                    for passedcase in testresult['passedcase']:
                        testreport.succase.add(Testcase.objects.get(caseno=passedcase))
                    for failedcase in testresult['failedcase']:
                        testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
                testreport.testsuite.add(obj)
                for case in obj.case.all():
                    testreport.testcases.add(case)
                    case.runtime = timezone.now()
                    case.save()
                testreport.save()
            except Exception as e:
                self.message_user(request,'发生异常' + str(e))
                testreport  = TESTREPORT.objects.create(reportname=thisname, testnum=casenum, result='N', runner=request.user,errors = str(e))
        self.message_user(request, '测试运行完成，请查看测试报告')
    runsuite.short_description = '运行套件'

    def jrunsuite(self,request,query_set):
        testsuites = []
        for obj in query_set:
            rundatas = get_suitedata(obj)
            testsuites.append(rundatas)
        try:
            write_case(f'{filedir}/runner/data/test.yaml', testsuites)
        except Exception as e:
            self.message_user(request,'发生异常' + str(e))
        server = jenkins.Jenkins(url='http://127.0.0.1:8888/', username='admin', password='z111111')
        last_build_number = server.get_job_info('apitest')['lastCompletedBuild']['number']
        this_build_number = last_build_number + 1
        server.build_job('apitest', token='111111')
        url = 'http://127.0.0.1:8888/job/apitest/'+ str(this_build_number)
        Jenkinsreport.objects.create(testno=this_build_number,url=url)
        self.message_user(request, 'Jenkins已进行构建')
    jrunsuite.short_description = 'jenkins运行套件'

@admin.register(Testbatch)
class TestbatchAdmin(admin.ModelAdmin):
    list_display = ['batchno','ctime','runtime']
    filter_horizontal = ['testsuite']
    actions = ['runbatch',]
    exclude = ('runtime',)

    def runbatch(self,request,query_set):
        thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
        for batch in query_set:
            for obj in batch.testsuite.all():
                testsuite = get_suitedata(obj)
                casenum = obj.case.count()
                args = obj.args.all().values_list('name')
                try:
                    write_case(f'{filedir}/runner/data/test.yaml',[testsuite])
                    report = testrunner.pyrun(args,obj.reruns,obj.reruns_delay)
                    testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
                    os.environ.pop('TESTRESULT')
                    result = testresult['result']
                    failed = testresult['failed']
                    passed = testresult['passed']
                    with open(report + '/index.html','r',encoding='utf-8') as f:
                        thisfile = File(f)
                        thisfile.name = thisfile.name.split('report/')[1]
                        testreport = TESTREPORT.objects.create(reportname=thisname, runner=request.user, file=thisfile,testnum=casenum, result=result,suc=passed, fail=failed)
                        for passedcase in testresult['passedcase']:
                            testreport.succase.add(Testcase.objects.get(caseno=passedcase))
                        for failedcase in testresult['failedcase']:
                            testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
                    testreport.testsuite.add(obj)
                    for case in obj.case.all():
                        testreport.testcases.add(case)
                        case.runtime = timezone.now()
                        case.save()
                    testreport.save()
                except Exception as e:
                    self.message_user(request,'发生异常' + str(e))
                    testreport  = TESTREPORT.objects.create(reportname=thisname, testnum=casenum, result='N', runner=request.user,errors = str(e))
        self.message_user(request, '测试运行完成，请查看测试报告')
    runbatch.short_description = '运行批次'

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
    list_display = ['reportname', 'testtime', 'testnum', 'result', 'suc', 'fail', 'runner','filelink']
    list_filter = ['testsuite']
    view_on_site = True
    params = TESTREPORTparams
    fields = params
    readonly_fields = params
    list_display_links = ['filelink']

    def filelink(self,obj):
        return format_html('<a href="{}" target="_blank">{}</a> <a href="{}">{}</a>',obj.file.url,'查看报告',reverse('admin:apitest_testreport_change', args=(obj.id,)),'详情')
    filelink.short_description = '操作'

    def delete_model(self,request,obj):
        reportfile = obj.file.url.rsplit('/',1)[0]
        if os.path.exists(filedir+reportfile):
            shutil.rmtree(filedir+reportfile)