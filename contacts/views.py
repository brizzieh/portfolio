from django.shortcuts import render, redirect
from .models import Contact

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts/list.html', {'contacts': contacts})
