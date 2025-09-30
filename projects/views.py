from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from django.core.paginator import Paginator
from django.contrib import messages

def list(request):
    search_query = request.GET.get('q', '')
    
    if search_query:
        projects = Project.objects.filter(
            title__icontains=search_query
        ).order_by('-created_at')
    else:
        projects = Project.objects.all().order_by('-created_at')
    
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'dashboard/projects/list.html', context)

def create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        url = request.POST.get('url')
        image = request.FILES.get('image')
        
        if title and description and image:
            project = Project.objects.create(
                title=title,
                description=description,
                url=url,
                image=image
            )
            messages.success(request, 'Project created successfully!')
            return redirect('projects:list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'form_title': 'Create New Project',
        'action_description': 'add',
        'submit_button_text': 'Create Project'
    }
    return render(request, 'dashboard/projects/form.html', context)

def update(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.url = request.POST.get('url')
        
        if 'image' in request.FILES:
            project.image = request.FILES.get('image')
        
        project.save()
        messages.success(request, 'Project updated successfully!')
        return redirect('projects:list')
    
    context = {
        'project': project,
        'form_title': 'Edit Project',
        'action_description': 'update',
        'submit_button_text': 'Update Project'
    }
    return render(request, 'dashboard/projects/form.html', context)

def show(request, id):
    project = get_object_or_404(Project, id=id)
    context = {
        'project': project
    }
    return render(request, 'dashboard/projects/show.html', context)

def delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('projects:list')
    
    context = {
        'project': project
    }
    return render(request, 'dashboard/projects/delete.html', context)