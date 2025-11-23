from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('', views.resume_view, name='view'),
    path('list/', views.resume_list, name='list'),
    path('create/', views.resume_create, name='create'),
    path('edit/<int:pk>/', views.resume_edit, name='edit'),
    path('delete/<int:pk>/', views.resume_delete, name='delete'),
]