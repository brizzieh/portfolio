from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_company', 'rating', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'rating', 'created_at']
    search_fields = ['client_name', 'client_company', 'content']