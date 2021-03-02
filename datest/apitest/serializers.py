from rest_framework import serializers
from .models import *

class PostdataSerializer(serializers.HyperlinkedModelSerializer):
    repdata = serializers.JSONField(read_only=True)


    class Meta:
        model = Postdata
        fields = ('id','apiurl','reqdata','repdata')