from django import forms

class CsvImportForm(forms.Form):
    x_file = forms.FileField()
