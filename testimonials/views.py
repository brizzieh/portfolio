from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Testimonial

def list(request):
    search_query = request.GET.get('q', '')
    filter_featured = request.GET.get('featured', '')
    
    testimonials = Testimonial.objects.all()
    
    if search_query:
        testimonials = testimonials.filter(
            Q(client_name__icontains=search_query) |
            Q(client_company__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    if filter_featured:
        testimonials = testimonials.filter(is_featured=True)
    
    testimonials = testimonials.order_by('-created_at')
    
    paginator = Paginator(testimonials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_featured': filter_featured,
    }
    return render(request, 'dashboard/testimonials/list.html', context)

def create(request):
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_position = request.POST.get('client_position', '')
        client_company = request.POST.get('client_company', '')
        content = request.POST.get('content')
        rating = request.POST.get('rating', 5)
        is_featured = request.POST.get('is_featured') == 'on'
        project_url = request.POST.get('project_url', '')
        client_image = request.FILES.get('client_image')
        
        if client_name and content:
            testimonial = Testimonial.objects.create(
                client_name=client_name,
                client_position=client_position,
                client_company=client_company,
                content=content,
                rating=rating,
                is_featured=is_featured,
                project_url=project_url,
                client_image=client_image
            )
            messages.success(request, 'Testimonial created successfully!')
            return redirect('testimonials:list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'form_title': 'Create New Testimonial',
        'action_description': 'add',
        'submit_button_text': 'Create Testimonial'
    }
    return render(request, 'dashboard/testimonials/form.html', context)

def update(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    
    if request.method == 'POST':
        testimonial.client_name = request.POST.get('client_name')
        testimonial.client_position = request.POST.get('client_position', '')
        testimonial.client_company = request.POST.get('client_company', '')
        testimonial.content = request.POST.get('content')
        testimonial.rating = request.POST.get('rating', 5)
        testimonial.is_featured = request.POST.get('is_featured') == 'on'
        testimonial.project_url = request.POST.get('project_url', '')
        
        if 'client_image' in request.FILES:
            testimonial.client_image = request.FILES.get('client_image')
        
        testimonial.save()
        messages.success(request, 'Testimonial updated successfully!')
        return redirect('testimonials:list')
    
    context = {
        'testimonial': testimonial,
        'form_title': 'Edit Testimonial',
        'action_description': 'update',
        'submit_button_text': 'Update Testimonial'
    }
    return render(request, 'dashboard/testimonials/form.html', context)

def delete(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully!')
        return redirect('testimonials:list')
    
    context = {
        'testimonial': testimonial
    }
    return render(request, 'dashboard/testimonials/delete.html', context)