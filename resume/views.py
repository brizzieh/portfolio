from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Resume

def resume_list(request):
    """List all resumes"""
    resumes = Resume.objects.all().order_by('-uploaded_at')
    return render(request, 'dashboard/resumes/list.html', {
        'resumes': resumes,
        'page_title': 'Resumes'
    })

def resume_create(request):
    """Create a new resume"""
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not title or not file:
            messages.error(request, 'Title and file are required.')
            return render(request, 'dashboard/resumes/form.html', {
                'form_title': 'Upload Resume',
                'action_description': 'upload',
                'submit_button_text': 'Upload Resume'
            })
        
        # Validate file type
        allowed_types = ['.pdf', '.doc', '.docx']
        file_extension = file.name.lower().split('.')[-1]
        if file_extension not in ['pdf', 'doc', 'docx']:
            messages.error(request, 'Please upload a PDF, DOC, or DOCX file.')
            return render(request, 'dashboard/resumes/form.html', {
                'form_title': 'Upload Resume',
                'action_description': 'upload',
                'submit_button_text': 'Upload Resume'
            })
        
        # Create resume
        resume = Resume.objects.create(
            title=title,
            file=file,
            is_active=is_active
        )
        
        messages.success(request, 'Resume uploaded successfully!')
        return redirect('resumes:list')
    
    return render(request, 'dashboard/resumes/form.html', {
        'form_title': 'Upload Resume',
        'action_description': 'upload',
        'submit_button_text': 'Upload Resume'
    })

def resume_edit(request, pk):
    """Edit an existing resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'dashboard/resumes/form.html', {
                'resume': resume,
                'form_title': 'Edit Resume',
                'action_description': 'update',
                'submit_button_text': 'Update Resume'
            })
        
        # Update fields
        resume.title = title
        resume.is_active = is_active
        
        # Update file if provided
        if file:
            # Validate file type
            allowed_types = ['.pdf', '.doc', '.docx']
            file_extension = file.name.lower().split('.')[-1]
            if file_extension not in ['pdf', 'doc', 'docx']:
                messages.error(request, 'Please upload a PDF, DOC, or DOCX file.')
                return render(request, 'dashboard/resumes/form.html', {
                    'resume': resume,
                    'form_title': 'Edit Resume',
                    'action_description': 'update',
                    'submit_button_text': 'Update Resume'
                })
            resume.file = file
        
        resume.save()
        messages.success(request, 'Resume updated successfully!')
        return redirect('resumes:list')
    
    return render(request, 'dashboard/resumes/form.html', {
        'resume': resume,
        'form_title': 'Edit Resume',
        'action_description': 'update',
        'submit_button_text': 'Update Resume'
    })

def resume_delete(request, pk):
    """Delete a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume deleted successfully!')
        return redirect('resumes:list')
    
    return render(request, 'dashboard/resumes/delete_confirm.html', {
        'resume': resume
    })

def resume_view(request):
    """View active resume (original functionality)"""
    resume = Resume.objects.filter(is_active=True).first()
    return render(request, 'dashboard/resumes/view.html', {'resume': resume})