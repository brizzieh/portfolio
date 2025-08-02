from django.shortcuts import render
from .models import Project

# Create your views here.
def list(request):
    context = {}
    return render(request, 'dashboard/projects/list.html', context)

def create(request):
    context = {}
    return render(request, 'dashboard/projects/create.html', context)

def update(request):
    context = {}
    return render(request, 'dashboard/projects/update.html', context)

def show(request):
    context = {}
    return render(request, 'dashboard/projects/show.html', context)

def delete(request):
    context = {}
    return render(request, 'dashboard/projects/delete.html', context)