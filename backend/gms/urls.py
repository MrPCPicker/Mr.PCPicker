from django.urls import path
from .views import gms_test

urlpatterns = [
    path("gms-test/", gms_test),
]
