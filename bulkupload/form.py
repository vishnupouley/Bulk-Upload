from django import forms
from bulkupload.models import UsersModel


class UsersForm(forms.Form):
    class Meta:
        model = UsersModel
        fields = '__all__'