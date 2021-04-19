import io
import random
from time import timezone
from urllib.parse import urlsplit

import jenkins
from django.core.files import File
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import viewsets, renderers, permissions, authentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.routers import APIRootView
from django.utils import timezone

from .postmail import postmail
from .runner import testrunner
from .runner.scheduler import scheduler
from .serializers import *
from .viewsfunc import *
from .datahandle import get_casedata, get_suitedata, write_case, get_faildata
from django.forms import modelform_factory
# Create your views here.


filedir = os.path.dirname(__file__)

def run_data(num=1,data=[],args=[],reruns = 0,reruns_delay=0):
    # 创建data目录，将Json离线化，转成yaml文件
    try:
        name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
        # 将数据库对象转成Json
        if not os.path.exists(f'{filedir}/runner/data'):
            os.mkdir(f'{filedir}/runner/data')
        write_case(f'{filedir}/runner/data/test.yaml', data)
        # 运行测试用例，记录测试结果
        report = testrunner.pyrun(args,reruns,reruns_delay)
        testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
        os.environ.pop('TESTRESULT')
        result = testresult['result']
        failed = testresult['failed']
        passed = testresult['passed']
        # 将测试结果和测试报告地址存表
        with open(report + '/index.html', 'r', encoding='utf-8') as f:
            thisfile = File(f)
            thisfile.name = thisfile.name.split('report/')[1]
            testreport = TESTREPORT.objects.create(reportname=name, file=thisfile, testnum=num, result=result,suc=passed, fail=failed)
        with open(f'{filedir}/data/logs/{report.split("/")[-1]}.log', 'r', encoding='utf-8') as f:
            logfile = File(f)
            logfile.name = logfile.name.split('logs/')[1]
            testreport.logfile = logfile
            testreport.save()
        for passedcase in testresult['passedcase']:
            testreport.succase.add(Testcase.objects.get(caseno=passedcase))
        for failedcase in testresult['failedcase']:
            testreport.failcase.add(Testcase.objects.get(caseno=failedcase))
        return testreport
    except Exception as e:
        TESTREPORT.objects.create(reportname=name, testnum=num, result='N',errors=str(e))
        raise e


class RootView(APIRootView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('admin:index'))


class IsOwnerOrReadOnly(object):
    pass


class ApiViewset(viewsets.ModelViewSet):
    queryset = Api.objects.all()
    serializer_class = ApiSerializer
    renderer_classes = (renderers.JSONRenderer,renderers.TemplateHTMLRenderer)
    authentication_classes = (authentication.BasicAuthentication,)

    @action(methods=['get','post'],detail='api-detail',url_path='runapi',url_name='api-runapi')
    def runapi(self,request, *args, **kwargs):
        testgroup = TestcaseGroup.objects.all()
        baseurl = BASEURL.objects.all()
        setupfunc = FUNC.objects.all()
        teardownfunc = FUNC.objects.all()
        callfunc = CALLFUNC.objects.all()
        if request.method == 'GET':
            apiobj = Api.objects.get(pk=kwargs['pk'])
            result = {'id': apiobj.id,
                      'jsondata': '',
                      'formdata': '',
                      'respdata': '',
                      'testgroup': testgroup,
                      'baseurl': baseurl,
                      'teardownfunc':teardownfunc,
                      'setupfunc': setupfunc,
                      'callfunc': callfunc,
                      'user':request.user
                      }
        return Response(result, template_name='postman/api.html')

    @action(methods=['post'], detail='api-detail', url_path='postapi', url_name='api-postapi')
    def postapi(self,request, *args, **kwargs):
        try:
            apiobj = Api.objects.get(pk=kwargs['pk'])
            reqdata = json.dumps(json.loads(request.POST.get('reqdata')), sort_keys=True, indent=4, ensure_ascii=False)
            res = apipost(requestUri=apiobj.url, data=json.loads(request.POST.get('reqdata'), encoding='utf-8'))
            if apiobj.requesttype == '1':
                url2 = apiobj.url.replace('Apply', 'Result')
                orderno = json.loads(res.text, encoding='utf-8')['orderNo']
                resultDesc = "订单处理中"
                while resultDesc == "订单处理中":
                    time.sleep(1)
                    res = apipost(requestUri=url2, data={'orderNo': orderno})
            result = json.dumps(json.loads(res.text,encoding='utf-8'), sort_keys=True, indent=4, ensure_ascii=False)
            return Response(result)
        except Exception as e:
            return Response(str(e))

    @action(methods=['post'], detail='api-detail', url_path='gennewcase', url_name='api-gennewcase')
    def gen_newcase(self,request, *args, **kwargs):
        apiobj = Api.objects.get(pk=kwargs['pk'])
        newcase = Testcase.objects.create(
            caseno= apiobj.code + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(
            random.randint(1, 1000)),
            casename = request.POST.get('casename'),
            project = apiobj.project,
            group = TestcaseGroup.objects.get(id=request.POST.get('group').split('-')[0]),
            api=apiobj,
            datamode='JSON',
            requestdata = request.POST.get('jsondata'),
            creater = request.user
        )
        newcase.save()
        return HttpResponseRedirect(f'/admin/apitest/testcase/?id={newcase.id}')

class DebugTalkViewset(viewsets.ModelViewSet):
    '''
    用于在线编辑debugtalk文件
    '''
    queryset = DebugTalk.objects.all()
    serializer_class = DebugTalkSerializer
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


    @action(methods=['get','post'], detail='debugtalk-detail', url_path='edit', url_name='debugtalk-edit')
    def edit(self, request, *args, **kwargs):
        # 在线编辑debugtalk文件
        obj = DebugTalk.objects.get(id=kwargs['pk'])
        debugtalk = DebugTalk.objects.values('id', 'content').get(id=kwargs['pk'])
        filepath = filedir + DebugTalk.objects.get(id=kwargs['pk']).file
        if request.method == 'GET':
            try:
                with open(filepath, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    debugtalk['content'] = content
            except Exception as e:
                with open(filepath, 'w', encoding='utf-8') as f:
                    pass
            return render(request , template_name='debugtalk/edit.html',context = debugtalk)
        else:
            changed = request.POST.get('content')
            code = changed.replace('new_line', '\r\n')
            obj.content = code
            obj.save()
            with io.open(filepath, 'w', encoding='utf-8') as stream:
                stream.write(code)
            return HttpResponseRedirect('/admin/apitest/debugtalk/')

class TestcaseViewset(viewsets.ModelViewSet):
    queryset = Testcase.objects.all()
    serializer_class = TestcaseSerializer
    renderer_classes = (renderers.JSONRenderer,renderers.TemplateHTMLRenderer)
    authentication_classes = (authentication.BasicAuthentication,)

    @action(methods=['get'],detail='testcase-detail',url_path='postcase',url_name='testcase-postcase')
    def runcase(self,request, *args, **kwargs):
        # 根据测试用例数据发送请求，查看响应信息
        if request.method == 'GET':
            caseobj = Testcase.objects.get(pk=kwargs['pk'])
            case = get_casedata('',caseobj)
            reqdata = case['data']
            res = apipost(httpMethod=case['method'], headers=case['headers'], endpoint=case['baseurl'],requestUri=case['url'], data=case['data'])
            if caseobj.api.requesttype == '1':
                url2 = caseobj.api.url.replace('Apply','Result')
                orderno = json.loads(res.text,encoding='utf-8')['orderNo']
                resultDesc = "订单处理中"
                while resultDesc == "订单处理中":
                    time.sleep(1)
                    res = apipost(requestUri=url2, data={'orderNo':orderno})
                    resultDesc = json.loads(res.text, encoding='utf-8')['resultDesc']
        resp_obj_meta = {
            "status_code": res.status_code,
            "headers": res.headers,
            "cookies": res.cookies,
            "body": json.loads(res.content, encoding='utf-8'),
        }
        datano = caseobj.api.code
        assertdata = []
        for key, value in resp_obj_meta['body'].items():
            akobj = Assertkey.objects.get_or_create(value='$..' + key)[0]
            # assertmode = 'assert_jsonmatch'
            # if type(value) is list:
            #     assertvalue = "\[(\{.*?\})*\]"
            # elif type(value) is dict:
            #     assertvalue = "\{.*?\}"
            # elif type(value) is str:
            #     assertvalue = ".*?"
            # elif value is False:
            #     assertvalue = 'False'
            # elif value is True:
            #     assertvalue = 'True'
            avobj = Assertval.objects.get_or_create(value=str(value))[0]
            assertdata.append({"path": akobj.value, "value": avobj.value})
        result = {'id': caseobj.id, 'headers': case['headers'],
                  'jsondata': reqdata,
                  'formdata': case['formdata'],
                  'respdata': json.dumps(resp_obj_meta.get('body'), sort_keys=True, indent=4, ensure_ascii=False),
                'assertdata': assertdata,
                  'user': request.user
                  }
        return Response(result, template_name='postman/postcase.html')

    @action(methods=['post'],detail='testcase-detail',url_path='getassertdata',url_name='testcase-getassertdata')
    def get_assert_data(self,request, *args, **kwargs):
        # 根据页面响应信息输入框自动生成此用例校验数据保存
        resjson = json.loads(request.POST.get('respdata'), encoding='utf-8')
        assertdata = []
        num = 0
        for key, value in resjson.items():
            # assertmode = 'assert_jsonmatch'
            # if type(value) is list:
            #     assertvalue = "\[(\{.*?\})*\]"
            # elif type(value) is dict:
            #     assertvalue = "\{.*?\}"
            # elif type(value) is str:
            #     assertvalue = ".*?"
            # elif value is False:
            #     assertvalue = 'False'
            # elif value is True:
            #     assertvalue = 'True'
            mode = 'assert_equal'
            assertdata.append({"no":num, "path": '$..' + key, "value": str(value), "mode": mode})
            num += 1
        return Response(assertdata)

    @action(methods=['post'],detail='testcase-detail',url_path='genassertdata',url_name='testcase-genassertdata')
    def gen_assert_data(self,request, *args, **kwargs):
        caseobj = Testcase.objects.get(pk=kwargs['pk'])
        case = get_casedata('', caseobj)
        assertjsondata = json.loads(request.POST.get('assertdata'), encoding='utf-8')
        for data in assertjsondata:
            akey = Assertkey.objects.get_or_create(value=data['path'])[0]
            aval = Assertval.objects.get_or_create(value=data['value'])[0]
            mode = data['mode']
            AssertParam.objects.get_or_create(testcase=caseobj,paramkey=akey,defaults = {'paramval':aval,'mode':mode})
        return HttpResponseRedirect(f'/admin/apitest/testcase/{caseobj.id}/change/')

def run_suite(id):
    '''
    通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
    :param query_set:
    :return:
    '''
        # 获取套件所有的测试用例，结果为[[{套件1用例},...],[{套件2用例},...]]
    obj = TESTSUITE.objects.get(id=id)
    testdata = get_suitedata(obj)
    casenum = obj.case.count()
    args = obj.args.all().values_list('name')
    reruns = obj.reruns
    reruns_delay = obj.reruns_delay
    testreport = run_data(num=casenum, data=[testdata],args=args,reruns=reruns,reruns_delay=reruns_delay)
    testreport.testsuite.add(obj)
    for case in obj.case.all():
        testreport.testcases.add(case)
        case.runtime = timezone.now()
        case.save()
    testreport.save()
    obj.runtime = timezone.now()
    obj.save

class TestsuiteViewset(viewsets.ModelViewSet):
    queryset = TESTSUITE.objects.all()
    serializer_class = TestsuiteSerializer
    renderer_classes = (renderers.TemplateHTMLRenderer,)

    @action(methods=['get'], detail='testsuite-detail', url_path='runback', url_name='testsuite-runback')
    def run_back(self,request, *args, **kwargs):
        '''
        后台运行单个测试套件任务
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        scheduler.add_job(run_suite, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[kwargs['pk']])
        return Response({},template_name='testsuite/runback.html')


def run_batch(host,id):
    batch = Testbatch.objects.get(id=id)
    testbatch = []
    for obj in batch.testsuite.all():
        testsuite = get_suitedata(obj)
        testbatch.extend(testsuite)
    casenum = len(testbatch)
    args = batch.args.all().values_list('name')
    testreport = run_data(num=casenum, data=[testbatch], args=args)
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
    postmail(host,'605662545@qq.com', '605662545@qq.com', testreport)


class TestbatchViewset(viewsets.ModelViewSet):
    queryset = Testbatch.objects.all()
    serializer_class = TestbatchSerializer
    renderer_classes = (renderers.TemplateHTMLRenderer,)

    @action(methods=['get'], detail='testbatch-detail', url_path='runback', url_name='testbatch-runback')
    def run_back(self,request, *args, **kwargs):
        # 后台运行测试批次任务
        run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        http = urlsplit(request.build_absolute_uri(None)).scheme
        host = http + '://' + request.META['HTTP_HOST']
        scheduler.add_job(run_batch, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[host,kwargs['pk']])
        return Response({},template_name='testbatch/runback.html')


def run_failcase(rid):
    '''
    通过apitest/runner下的testrunner脚本运行yaml测试用例文件，根据测试结果新建测试报告对象
    :param query_set:
    :return:
    '''
        # 获取套件所有的测试用例，结果为[[{套件1用例},...],[{套件2用例},...]]
    obj = TESTREPORT.objects.get(id=rid)
    testdata = get_faildata(obj)
    casenum = obj.failcase.count()
    testreport = run_data(num=casenum, data=[testdata])
    for case in obj.failcase.all():
        testreport.testcases.add(case)
        case.runtime = timezone.now()
        case.save()
    testreport.save()
    obj.runtime = timezone.now()
    obj.save

class TESTREPORTViewset(viewsets.ModelViewSet):
    queryset = TESTREPORT.objects.all()
    serializer_class = TESTREPORTSerializer
    renderer_classes = (renderers.TemplateHTMLRenderer,)

    @action(methods=['get'], detail='testreport-detail', url_path='runfail', url_name='testbatch-runfail')
    def run_fail(self,request, *args, **kwargs):
        # 后台运行测试批次任务
        run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        scheduler.add_job(run_failcase, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[kwargs['pk']])
        return Response({},template_name='testreport/runback.html')

@api_view(['GET'])
def get_log(request,*args,**kwargs):
    obj = Jenkinsreport.objects.get(pk=kwargs['id'])
    batchnumber = obj.number
    server = jenkins.Jenkins(url='http://127.0.0.1:8888/', username='admin', password='z111111')
    logdata =server.get_build_console_output('apitest',batchnumber)
    return render(request,template_name='testbatch/jenkinslog.html',context={'batchnumber':batchnumber,'logdata':logdata})