from rest_framework import serializers
from .models import *

class PostdataSerializer(serializers.HyperlinkedModelSerializer):
    repdata = serializers.JSONField(read_only=True)


    class Meta:
        model = Postdata
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)

class TestcaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Testcase
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)