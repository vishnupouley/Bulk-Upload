from import_export.resources import ModelResource
from bulkupload.models import UsersModel
from import_export.fields import Field


class UsersResource(ModelResource):
    user_id = Field(column_name='user_id', attribute='user_id')
    user_name = Field(column_name='user_name', attribute='user_name')
    email = Field(column_name='email', attribute='email')
    business_unit = Field(column_name='business_unit', attribute='business_unit')
    department = Field(column_name='department', attribute='department')
    date_of_joining = Field(column_name='date_of_joining', attribute='date_of_joining')
    mobile_number = Field(column_name='mobile_number', attribute='mobile_number')

    class Meta:
        model = UsersModel