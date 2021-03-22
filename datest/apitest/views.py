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

class RootView(APIRootView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('admin:index'))

class PostdataViewset(viewsets.ModelViewSet):
    queryset = Postdata.objects.all()
    serializer_class = PostdataSerializer

    def create(self, request, *args, **kwargs):
        rtext = apipost(request.data['apiurl'],request.data['reqdata'])
        return Response(json.loads(rtext.text))


class IsOwnerOrReadOnly(object):
    pass


class DebugTalkViewset(viewsets.ModelViewSet):
    queryset = DebugTalk.objects.all()
    serializer_class = DebugTalkSerializer
    authentication_classes = (authentication.BasicAuthentication,)


    @action(methods=['get','post'], detail='debugtalk-detail', url_path='edit', url_name='debugtalk-edit')
    def edit(self, request, *args, **kwargs):
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
        caseobj = Testcase.objects.get(pk=kwargs['pk'])
        case = get_casedata('',caseobj)
        res = apipost(httpMethod=case['method'],headers=case['headers'],endpoint=case['baseurl'],requestUri=case['url'], json=case['data'],files=case['formdata'])
        resp_obj_meta = {
            "status_code": res.status_code,
            "headers": res.headers,
            "cookies": res.cookies,
            "body": json.loads(res.content,encoding='utf-8'),
        }
        result = {'id':caseobj.id,'headers':case['headers'],'reqdata':{'jsondata':json.dumps(case['data'],sort_keys=True,indent=4,ensure_ascii=False),'formdata':case['formdata']},'respdata':json.dumps(resp_obj_meta.get('body'),sort_keys=True,indent=4,ensure_ascii=False)}
        return Response(result,template_name='postman/edit.html')

    @action(methods=['post'],detail='testcase-detail',url_path='genassertdata',url_name='testcase-genassertdata')
    def gen_assert_data(self,request, *args, **kwargs):
        caseobj = Testcase.objects.get(pk=kwargs['pk'])
        body = json.loads(request.POST.get('content'),encoding='utf-8')
        for key, value in body.items():
            akobj = Assertkey.objects.get_or_create(value='$..' + key)[0]
            avobj = Assertval.objects.get_or_create(value=str(value))[0]
            AssertParam.objects.get_or_create(testcase=caseobj,paramkey=akobj,defaults = {'paramval':avobj,'mode':'assert_equal'})
        return HttpResponseRedirect('/admin/apitest/testcase/')

def run_back_suite(id):
    thisname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '测试报告'
    obj = TESTSUITE.objects.get(id=id)
    testsuite = get_suitedata(obj)
    casenum = obj.case.count()
    args = obj.args.all().values_list('name')
    try:
        write_case(f'{filedir}/runner/data/test.yaml', [testsuite])
        runtime = timezone.now()
        report = testrunner.pyrun(args, obj.reruns, obj.reruns_delay)
        testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
        os.environ.pop('TESTRESULT')
        result = testresult['result']
        failed = testresult['failed']
        passed = testresult['passed']
        with open(report + '/index.html', 'r', encoding='utf-8') as f:
            thisfile = File(f)
            thisfile.name = thisfile.name.split('report/')[1]
            testreport = TESTREPORT.objects.create(reportname=thisname, file=thisfile, testnum=casenum,
                                                   result=result, suc=passed, fail=failed)
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
    except Exception as e:
        TESTREPORT.objects.create(reportname=thisname, testnum=casenum, result='N', errors=str(e))
        raise e

class TestsuiteViewset(viewsets.ModelViewSet):
    queryset = TESTSUITE.objects.all()
    serializer_class = TestsuiteSerializer
    renderer_classes = (renderers.TemplateHTMLRenderer,)

    @action(methods=['get'], detail='testsuite-detail', url_path='runback', url_name='testsuite-runback')
    def run_back(self,request, *args, **kwargs):
        run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        scheduler.add_job(run_back_suite, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[kwargs['pk']])
        return Response({},template_name='testsuite/runback.html')

def run_back_batch(id):
    batch = Testbatch.objects.get(id=id)
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
        write_case(f'{filedir}/runner/data/test.yaml', [testbatch])
        runtime = timezone.now()
        report = testrunner.pyrun(args, batch.reruns, batch.reruns_delay)
        testresult = json.loads(os.environ.get('TESTRESULT'), encoding='utf-8')
        os.environ.pop('TESTRESULT')
        result = testresult['result']
        failed = testresult['failed']
        passed = testresult['passed']
        with open(report + '/index.html', 'r', encoding='utf-8') as f:
            thisfile = File(f)
            thisfile.name = thisfile.name.split('report/')[1]
            testreport = TESTREPORT.objects.create(reportname=batch_reportname, testbatch=batch,
                                                   file=thisfile, testnum=casenum, result=result, suc=passed,
                                                   fail=failed)
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
        testreport = TESTREPORT.objects.create(reportname=batch_reportname, testnum=casenum, testbatch=batch,result='N',  errors=str(e))
        raise e

class TestbatchViewset(viewsets.ModelViewSet):
    queryset = Testbatch.objects.all()
    serializer_class = TestbatchSerializer
    renderer_classes = (renderers.TemplateHTMLRenderer,)

    @action(methods=['get'], detail='testbatch-detail', url_path='runback', url_name='testbatch-runback')
    def run_back(self,request, *args, **kwargs):
        run_date = (datetime.datetime.now() + datetime.timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        scheduler.add_job(run_back_batch, 'date', id=str(datetime.datetime.now().timestamp().as_integer_ratio()[0]),run_date=run_date, args=[kwargs['pk']])
        return Response({},template_name='testbatch/runback.html')
