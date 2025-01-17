from django.urls import path
from bulkupload import views

app_name = 'bulkupload'
urlpatterns = [
    path('', views.import_data_pandas, name='import_data'),
]