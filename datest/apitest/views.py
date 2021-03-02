from django.shortcuts import render
from rest_framework import viewsets, renderers
from rest_framework.response import Response

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
