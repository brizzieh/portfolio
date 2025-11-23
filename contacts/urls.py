from django.urls import path
from .views import contact_list, delete

app_name='contacts'

urlpatterns = [
    path('', contact_list, name='contact_list'),
    path('<int:id>/delete/', delete, name='delete'),
]