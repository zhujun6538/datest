import io
from time import timezone

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
from .runner import testrunner
from .runner.scheduler import scheduler
from .serializers import *
from .viewsfunc import *
from .datahandle import get_casedata, get_suitedata, write_case

# Create your views here.


filedir = os.path.dirname(__file__)

def run_data(num=1,data=[],args='',reruns = 0,reruns_delay=0):
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



class DebugTalkViewset(viewsets.ModelViewSet):
    '''
    用于在线编辑debugtalk文件
    '''
    queryset = DebugTalk.objects.all()
    serializer_class = DebugTalkSerializer
    authentication_classes = (authentication.BasicAuthentication,)


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
    renderer_classes = (renderers.TemplateHTMLRenderer,)
    authentication_classes = (authentication.BasicAuthentication,)

    @action(methods=['get'],detail='testcase-detail',url_path='postcase',url_name='testcase-postcase')
    def runcase(self,request, *args, **kwargs):
        # 根据测试用例数据发送请求，查看响应信息
        caseobj = Testcase.objects.get(pk=kwargs['pk'])
        case = get_casedata('',caseobj)
        res = apipost(httpMethod=case['method'],headers=case['headers'],endpoint=case['baseurl'],requestUri=case['url'], data=case['data'])
        resp_obj_meta = {
            "status_code": res.status_code,
            "headers": res.headers,
            "cookies": res.cookies,
            "body": json.loads(res.content,encoding='utf-8'),
        }
        result = {'id':caseobj.id,'headers':case['headers'],'jsondata':json.dumps(case['data'],sort_keys=True,indent=4,ensure_ascii=False),'formdata':case['formdata'],'respdata':json.dumps(resp_obj_meta.get('body'),sort_keys=True,indent=4,ensure_ascii=False)}
        return Response(result,template_name='postman/edit.html')

    @action(methods=['post'],detail='testcase-detail',url_path='genassertdata',url_name='testcase-genassertdata')
    def gen_assert_data(self,request, *args, **kwargs):
        # 根据页面响应信息输入框自动生成此用例校验数据保存
        caseobj = Testcase.objects.get(pk=kwargs['pk'])
        datano = caseobj.api.code
        body = json.loads(request.POST.get('content'),encoding='utf-8')
        assertparam = {}
        for key, value in body['resultData'][datano + 'Data'].items():
            akobj = Assertkey.objects.get_or_create(value='$..' + key)[0]
            assertmode = 'assert_jsonmatch'
            if type(value) is list:
                assertvalue = "\[(\{.*?\})*\]"
            elif type(value) is dict:
                assertvalue = "\{.*?\}"
            elif type(value) is str:
                assertvalue = ".*?"
            elif value is False:
                assertvalue = 'False'
            elif value is True:
                assertvalue = 'True'
            avobj = Assertval.objects.get_or_create(value=assertvalue)[0]
            AssertParam.objects.get_or_create(testcase=caseobj,paramkey=akobj,defaults = {'paramval':avobj,'mode':assertmode})
        return HttpResponseRedirect('/admin/apitest/testcase/')


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


def run_batch(id):
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


class TestbatchViewset(viewsets.ModelViewSet):
    queryset = Testbatch.objects.all()
    serializer_class = TestbatchSerializer
    renderer_classes = (renderers.TemplateHTMLRenderer,)

    @action(methods=['get'], detail='testbatch-detail', url_path='runback', url_name='testbatch-runback')
    def run_back(self,request, *args, **kwargs):
        # 后台运行测试批次任务
        run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        scheduler.add_job(run_batch, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[kwargs['pk']])
        return Response({},template_name='testbatch/runback.html')
