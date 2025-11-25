from django.urls import path
from . import views

app_name = 'pickerapp'
urlpatterns = [
    path('', views.index, name='index'),
]
