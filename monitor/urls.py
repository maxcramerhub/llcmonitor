from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('', views.index, name='index'),
    path('class-select/', views.class_select, name='class_select'),
    path('class-check/', views.class_check, name='class_check'),
    path('success/', views.success, name='success'),
    path('admin/', views.admin_login, name = 'admin_login')
]