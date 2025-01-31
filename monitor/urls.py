from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('', views.index, name='index'),
    path('class-select/', views.class_select, name='class_select'),
    path('success/', views.success, name='success'),
]