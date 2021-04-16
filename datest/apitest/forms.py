from django import forms
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.widgets import ForeignKeyWidget

from .models import *

class CsvImportForm(forms.Form):
    x_file = forms.FileField()

class ApiImportForm(ImportForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True)
    group = forms.ModelChoiceField(
        queryset=ApiGroup.objects.all(),
        required=True)


class ApiConfirmImportForm(ConfirmImportForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True)
    group = forms.ModelChoiceField(
        queryset=ApiGroup.objects.all(),
        required=True)

class TestcaseImportForm(ImportForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True)
    group = forms.ModelChoiceField(
        queryset=TestcaseGroup.objects.all(),
        required=True)

class TestcaseConfirmImportForm(ConfirmImportForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True)
    group = forms.ModelChoiceField(
        queryset=TestcaseGroup.objects.all(),
        required=True)