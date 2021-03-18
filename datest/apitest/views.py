import io

import jmespath
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import viewsets, renderers, permissions, authentication
from rest_framework.response import Response,SimpleTemplateResponse
from rest_framework.decorators import api_view, action
from rest_framework.routers import APIRootView

from .models import *
from .serializers import *
from .viewsfunc import *
from .datahandle import get_casedata
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