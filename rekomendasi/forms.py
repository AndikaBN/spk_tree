
from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name","nilai_mtk","nilai_bindo","nilai_bing","nilai_ipa","minat"]

class UploadDatasetForm(forms.Form):
    excel_file = forms.FileField(help_text="Upload file Excel dengan dua sheet: data AKUNTANSI dan PERKANTORAN")
