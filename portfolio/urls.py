from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard URLs
    path('dashboard/', include('app.urls')),
    path('dashboard/projects/', include('projects.urls')),
    path('dashboard/skills/', include('skills.urls')),
    path('dashboard/testimonials/', include('testimonials.urls')),
    path('dashboard/resume/', include('resume.urls')),
    path('dashboard/contacts/', include('contacts.urls')),
    path('dashboard/profile/', include('UserProfile.urls')),
    path('dashboard/settings/', include('settings.urls')),
    
    
    # Website URLs
    

    # Authentication URLs
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
