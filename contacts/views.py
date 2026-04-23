from django.shortcuts import render, redirect
from .models import Contact
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response

def contact_list(request):
    search_query = request.GET.get('q', '')
    
    if search_query:
        Contactss = Contact.objects.filter(
            title__icontains=search_query
        ).order_by('-created_at')
    else:
        Contactss = Contact.objects.all().order_by('-created_at')
    
    paginator = Paginator(Contactss, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/contacts/list.html', context)


def delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'contact deleted successfully!')
        return redirect('contacts:contact_list')
    
    context = {
        'contact': contact
    }
    return render(request, 'dashboard/contacts/delete.html', context)

@api_view(['POST'])
def send_message(request):
    name = request.data.get('name')
    email = request.data.get('email')
    subject = request.data.get('subject')
    message = request.data.get('message')

    if not name or not email or not subject or not message:
        return Response({'error': 'All fields are required.'}, status=400)

    Contact.objects.create(name=name, email=email, subject=subject, message=message)
    return Response({'success': 'Message sent successfully!'}, status=201)