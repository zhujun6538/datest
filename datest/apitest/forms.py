from django import forms
from .models import *

class CsvImportForm(forms.Form):
    x_file = forms.FileField()

