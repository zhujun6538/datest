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
from .datahandle import get_casedata
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
        caseobj = Testcase.objects.get(pk=kwargs['pk'])
        case = get_casedata('',caseobj)
        res = apipost(httpMethod=case['method'],headers=case['headers'],endpoint=case['baseurl'],requestUri=case['url'], json=case['data'],files=case['formdata'])
        resp_obj_meta = {
            "status_code": res.status_code,
            "headers": res.headers,
            "cookies": res.cookies,
            "body": json.loads(res.text,encoding='utf-8'),
        }
        try:
            checkresult = []
            for assdata in caseobj.assertparam_set.all():
                check_value = jmespath.search(assdata.paramkey.value, resp_obj_meta)
                expect_value = assdata.paramval.value
                result = comparators.equal(check_value,expect_value)
                checkresult.append({'断言':'成功','check_path':assdata.paramkey.value,'check_value':check_value,'expect_value':expect_value})
        except JMESPathError as ex:
            return Response({'JMESPathError':str(ex)})
        except AssertionError as e:
            checkresult.append({'断言': '失败', 'check_path': assdata.paramkey.value, 'check_value': check_value,'expect_value': expect_value})
        result = {'校验结果':checkresult,'headers':case['headers'],'jsondata':case['data'],'formdata':case['formdata'],'响应':resp_obj_meta.get('body')}
        return Response(result)