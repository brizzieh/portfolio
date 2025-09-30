from django.urls import path
from .views import *

app_name = 'projects'

urlpatterns = [
    path('', list, name="list"),
    path('create/', create, name="create"),
    path('<int:project_id>/edit/', update, name="edit"),
    path('<int:project_id>/delete/', delete, name="delete"),
]
