import jmespath
from django.shortcuts import render
from jmespath.exceptions import JMESPathError
from rest_framework import viewsets, renderers
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import *
from .serializers import *
from .viewsfunc import *
from httprunner.builtin import comparators
# Create your views here.

class PostdataViewset(viewsets.ModelViewSet):
    queryset = Postdata.objects.all()
    serializer_class = PostdataSerializer

    def create(self, request, *args, **kwargs):
        rtext = apipost(request.data['apiurl'],request.data['reqdata'])
        return Response(json.loads(rtext.text))

class TestcaseViewset(viewsets.ModelViewSet):
    queryset = Testcase.objects.all()
    serializer_class = TestcaseSerializer

    @action(methods=['get'],detail='testcase-detail',url_path='postcase',url_name='testcase-postcase')
    def runcase(self,request, *args, **kwargs):
        case = Testcase.objects.get(pk=kwargs['pk'])
        res = apipost(httpMethod=case.api.method,endpoint=case.baseurl.url,requestUri=case.api.url, data=case.requestdata)
        resp_obj_meta = {
            "status_code": res.status_code,
            "headers": res.headers,
            "cookies": res.cookies,
            "body": json.loads(res.text,encoding='utf-8'),
        }
        try:
            for assdata in case.assertparam_set.all():
                check_value = jmespath.search(assdata.paramkey.value, resp_obj_meta)
                expect_value = assdata.paramval.value
                result = comparators.equal(check_value,expect_value)
        except JMESPathError as ex:
            return Response({'JMESPathError':str(ex)})
        except AssertionError as e:
            return Response({'assert':'失败','check_value':check_value,'expect_value':expect_value,'data':json.loads(case.requestdata,encoding='utf-8'),'response':json.loads(res.text,encoding='utf-8')})
        result = {'assert':'成功','check_value':check_value,'expect_value':expect_value,'data':json.loads(case.requestdata,encoding='utf-8'),'response':json.loads(res.text,encoding='utf-8')}
        return Response(result)