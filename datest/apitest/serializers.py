from rest_framework import serializers
from .models import *


class TestcaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Testcase
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)

class TestsuiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = TESTSUITE
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)

class TestbatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Testbatch
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)

class DebugTalkSerializer(serializers.ModelSerializer):

    class Meta:
        model = DebugTalk
        fields = []
        for field in model._meta.fields:
            fields.append(field.name)