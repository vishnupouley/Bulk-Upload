from django.urls import path
from . import views

app_name = 'list_picker'

urlpatterns = [
    path('', views.index, name='index'),
    path('add-teams/', views.add_teams, name='add_teams'),
    path('remove-teams/', views.remove_teams, name='remove_teams'),
    path('add-employees/', views.add_employees, name='add_employees'),
    path('remove-employees/', views.remove_employees, name='remove_employees'),
    path('save/', views.save, name='save'),
]