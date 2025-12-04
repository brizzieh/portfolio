from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    path('', views.skill_list, name='list'),
    path('create/', views.skill_create, name='create'),
    path('edit/<int:pk>/', views.skill_edit, name='edit'),
    path('delete/<int:pk>/', views.skill_delete, name='delete'),
]