from django.urls import path
from .views import *

urlpatterns = [
    path('', list, name="projects"),
    path('create/', create, name="create_project"),
]
