import csv
import datetime
import random

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db import transaction
from django.forms import formset_factory, forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, path
from django.utils.html import format_html
from openpyxl import Workbook

from .forms import CsvImportForm
from .models import *
from .datahandle import *
# Register your models here.
from .runner import testrunner

AdminSite.site_header = "证通自动化测试后台"
AdminSite.index_title = "api测试"
filedir = os.path.dirname(__file__)
@admin.register(Api)
class ApiAdmin(admin.ModelAdmin):
    list_display = ['code','name','project','method','group','description','isValid','url','edit']
    search_fields = ['name']
    list_display_links = ['edit']
    list_filter = ['group','project']
    actions = ['get_excel']
    change_list_template = 'admin/apitest/api/option_changelist.html'

    def edit(self,obj):
        return format_html('<a href="{}">{}</a>',reverse('admin:apitest_api_change', args=(obj.id,)),'编辑')
    edit.short_description = '操作'

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
                project = Project.objects.get(name=data['project'])
                group = ApiGroup.objects.get(name=data['group'])
                Api.objects.create(code=data['code'],name=data['name'],project=project,group=group,method = data['method'],description=data['description'],isValid=True,url=data['url'])
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
    extra = 3

@admin.register(Headerkey)
class HeaderkeyAdmin(admin.ModelAdmin):
    search_fields = ['value']

@admin.register(Headerval)
class HeadervalAdmin(admin.ModelAdmin):
    search_fields = ['value']

class AssertParaminline(admin.TabularInline):
    model = AssertParam
    extra = 3
    autocomplete_fields = ['paramkey','paramval']

class RequestParaminline(admin.TabularInline):
    model = RequestParam
    extra = 3
    autocomplete_fields = ['paramkey', 'paramval']

class Runparaminline(admin.TabularInline):
    model = Runparam
    extra = 3
    readonly_fields = ['value']

@admin.register(Reqquestkey)
class ReqquestkeyAdmin(admin.ModelAdmin):
    search_fields = ['value']

@admin.register(Reqquestval)
class ReqquestvalAdmin(admin.ModelAdmin):
    search_fields = ['value']

@admin.register(Assertkey)
class AssertkeyAdmin(admin.ModelAdmin):
    search_fields = ['value']

    # def get_changeform_initial_data(self, request):
    #     return {'value': '$..'}

@admin.register(Assertval)
class AssertvalAdmin(admin.ModelAdmin):
    search_fields = ['value']

@admin.register(Testcase)
class TestcaseAdmin(admin.ModelAdmin):
    list_display = ['caseno','casename', 'group', 'isrun', 'api', 'createtime', 'runtime', 'edit']
    list_display_links = ['edit']
    search_fields = ['casename']
    radio_fields = {"isrun": admin.HORIZONTAL, "datamode": admin.HORIZONTAL}
    autocomplete_fields = ['api']
    inlines = [HeaderParaminline,RequestParaminline, AssertParaminline,Runparaminline]
    save_on_top = True
    actions = ['copy','get_caseyml','runcase']
    fields = ('casename', 'group', 'api', 'isrun','baseurl', 'datamode', 'requestdata')
    # change_list_template = 'admin/apitestwork/testcase/option_changelist.html'
    # list_per_page = 50

    def edit(self,obj):
        reporturl = '-'
        lastreports = TESTREPORT.objects.filter(testcases=obj).order_by('-testtime')
        if len(lastreports) != 0:
            reporturl = lastreports[0].file.url
        return format_html('<a href="{}" style="white-space:nowrap;">{}</a>',reverse('admin:apitest_testcase_change', args=(obj.id,)),'编辑')
    edit.short_description = '操作'

    def save_model(self, request, obj, form, change):
        obj.caseno = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1,1000))
        obj.project = obj.api.project
        obj.creater = request.user
        super().save_model(request, obj, form, change)

    def copy(self,request,query_set):
        for obj in query_set:
            oid = obj.id
            obj.id = None
            obj.save()
            oldobj = Testcase.objects.get(id = oid)
            for par in list(oldobj.headerparam_set.all()):
                HeaderParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.requestparam_set.all()):
                RequestParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval)
            for par in list(oldobj.assertparam_set.all()):
                AssertParam.objects.create(testcase=obj,paramkey=par.paramkey,paramval=par.paramval,mode=par.mode)
    copy.short_description = '复制'

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
        caseids = query_set.values_list('id', flat=True)
        Testcase.objects.select_for_update().filter(id__in = caseids)
        with transaction.atomic():
            testcases = self.gen_yml(request,query_set)
            try:
                write_case(f'{filedir}/runner/data/test.yaml', testcases)
                report = testrunner.pyrun()
            #     testresult = json.loads(os.environ.get('TESTRESULT'),encoding='utf-8')
            #     result = testresult['result']
            #     failed = testresult['failed']
            #     passed = testresult['passed']
            #     caseid = jsonpath.jsonpath(testcases,'$[*]..caseid.')
            #     thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
            #     with open(report + '/index.html','r',encoding='utf-8') as f:
            #         thisfile = File(f)
            #         thisfile.name = thisfile.name.split('report/')[1]
            #         testreport = TESTREPORT.objects.create(reportname=thisname, testnum=len(caseid),runner=request.user, file=thisfile, result=result, suc=passed, fail=failed)
            #         for passedcase in testresult['passedcase']:
            #             testreport.succase.add(Testcase.objects.get(caseid=passedcase))
            #         for failedcase in testresult['failedcase']:
            #             testreport.succase.add(Testcase.objects.get(caseid=failedcase))
            except Exception as e:
                self.message_user(request,'发生异常' + str(e))
            #     testreport = TESTREPORT.objects.create(reportname=thisname, testnum=len(caseid), result='N',runner=request.user, file=thisfile, suc=passed, fail=failed)
            # for obj in query_set:
            #     testreport.testcases.add(obj)
            #     testreport.save()
            #     obj.runtime = timezone.now()
            # Testcase.objects.bulk_update(query_set,['runtime'])
            # filelink = format_html('<a href="{}" style="white-space:nowrap;" target="_blank">{}</a>',testreport.file.url,'查看报告')
            self.message_user(request, '测试运行完成，请查看测试报告')
    runcase.short_description = '运行所有用例'

@admin.register(TESTSUITE)
class TESTSUITEAdmin(admin.ModelAdmin):
    list_display = ['name','baseurl','ctime','creater','edit']
    filter_horizontal = ['case']
    actions = ['gen_yaml','runsuite']
    exclude = ['creater','runtime']
    list_display_links = ['edit']

    def save_model(self, request, obj, form, change):
        obj.creater = request.user
        super().save_model(request, obj, form, change)

    def edit(self,obj):
        # if obj.suite_report.count() != 0:
        #     lastreports = TESTREPORT.objects.filter(testsuite=obj).latest('testtime')
        #     reporturl = lastreports.file.url
        #     return format_html('<a href="{}" style="white-space:nowrap;" >{}</a> <a href="{}" style="white-space:nowrap;" target="_blank">{}</a>',reverse('admin:apitestwork_testsuite_change', args=(obj.id,)),'编辑',reporturl,'查看报告')
        # else:
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
        testsuites = []
        for obj in query_set:
            testsuite = get_suitedata(obj)
            testsuites.append(testsuite)
        try:
            write_case(f'{filedir}/runner/test.yaml',testsuites)
            report = testrunner.pyrun()
            # caseid = jsonpath.jsonpath(testcases,'$[*]..caseid.')
            # thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
            # with open(report + '/index.html','r',encoding='utf-8') as f:
            #     thisfile = File(f)
            #     thisfile.name = thisfile.name.split('report/')[1]
            #     testreport  = TESTREPORT.objects.create(reportname=thisname, testnum = len(caseid),result='成功',runner= request.user,file=thisfile)
        except Exception as e:
            self.message_user(request,'发生异常' + str(e))
        #     testreport  = TESTREPORT.objects.create(reportname=thisname, testnum=len(caseid), result='失败', runner=request.user,file=thisfile)
        # for obj in query_set:
        #     testreport.testsuite.add(obj)
        #     testreport.save()
        # filelink = format_html('<a href="{}" style="white-space:nowrap;" target="_blank">{}</a>',testreport.file.url,'查看报告')
        self.message_user(request, '测试运行完成，请查看测试报告')
    runsuite.short_description = '运行套件'