from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('', views.index, name='index'),
    path('class-select/', views.class_select, name='class_select'),
    path('class-check/', views.class_check, name='class_check'),
    path('visualize/', views.visualize, name='visualize'),
    path('success/', views.success, name='success'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('tutor-management/', views.tutor_management, name='tutor_management'),
    path('tutor/add/', views.add_tutor, name='add_tutor'),
    path('tutor/edit/<int:tutor_id>/', views.edit_tutor, name='edit_tutor'),
    path('tutor/delete/<int:tutor_id>/', views.delete_tutor, name='delete_tutor'),
    path('admin-management/', views.admin_management, name='admin_management'),
    path('admin/add/', views.add_admin, name='add_admin'),
    path('admin/edit/<int:admin_id>/', views.edit_admin, name='edit_admin'),
    path('admin/delete/<int:admin_id>/', views.delete_admin, name='delete_admin'),
    path('admin-reviews/', views.admin_reviews, name='admin_reviews'),
    path('fetch-checkins/', views.fetch_checkins, name='fetch_checkins'),
    path('export-checkins/', views.export_checkins, name='export_checkins'),
    path('submit_review', views.submit_review, name='submit_review'),
    path('success', views.success, name='review_success'),
    path('leave_review/', views.leave_review, name='leave_review'),
    path('thank_you/', views.thank_you, name='thank_you'),
]