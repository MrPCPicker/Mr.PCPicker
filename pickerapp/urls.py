from django.urls import path
from . import views

urlpatterns = [
    path('pickerapp/', views.post_list),
    path('pickerapp/<int:post_pk>/', views.post_detail),
]
