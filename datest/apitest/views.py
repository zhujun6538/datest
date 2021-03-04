from django.shortcuts import render
from rest_framework import viewsets, renderers
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import *
from .serializers import *
from .viewsfunc import *
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
        rtext = apipost(httpMethod=case.api.method,endpoint=case.baseurl.url,requestUri=case.api.url, data=case.requestdata)
        return Response(json.loads(rtext.text))