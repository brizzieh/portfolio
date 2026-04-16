from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    path('', views.list, name='list'),
    path('create/', views.create, name='create'),
    path('<int:testimonial_id>/edit/', views.update, name='edit'),
    path('<int:testimonial_id>/delete/', views.delete, name='delete'),
]