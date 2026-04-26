from django.urls import path, include
from contacts.views import send_message
from projects import api_views
from skills import api_views as skills_api_views
from testimonials import api_views as testimonials_api_views
from resume import api_views as resume_api_views


urlpatterns = [
    # Projects API endpoints
    path('projects/', api_views.api_list, name='api_list'),
    path('projects/create/', api_views.api_create, name='api_create'),
    path('projects/<int:id>/', api_views.api_show, name='api_show'),
    path('projects/<int:project_id>/update/', api_views.api_update, name='api_update'),
    path('projects/<int:project_id>/delete/', api_views.api_delete, name='api_delete'),
    path('projects/detail/<int:project_id>/', api_views.api_project_detail, name='api_detail'),
    path('projects/bulk-delete/', api_views.api_bulk_delete, name='api_bulk_delete'),

    # Message sending endpoint
    path('contact/send_message/', send_message, name='send_message'),

    # Skills API endpoints
    path('skills/', skills_api_views.api_skill_list, name='api_list'),
    path('skills/statistics/', skills_api_views.api_skill_statistics, name='api_statistics'),
    path('skills/categories/', skills_api_views.api_skill_categories, name='api_categories'),
    path('skills/create/', skills_api_views.api_skill_create, name='api_create'),
    path('skills/bulk-create/', skills_api_views.api_skill_bulk_create, name='api_bulk_create'),
    path('skills/bulk-update/', skills_api_views.api_skill_bulk_update, name='api_bulk_update'),
    path('skills/bulk-delete/', skills_api_views.api_skill_bulk_delete, name='api_bulk_delete'),
    path('skills/<int:pk>/', skills_api_views.api_skill_detail, name='api_detail'),
    path('skills/<int:pk>/update/', skills_api_views.api_skill_update, name='api_update'),
    path('skills/<int:pk>/delete/', skills_api_views.api_skill_delete, name='api_delete'),
    path('skills/combined/<int:pk>/', skills_api_views.api_skill_combined, name='api_combined'),

    # Testimonials API endpoints
    path('testimonials/', testimonials_api_views.api_testimonial_list, name='api_list'),
    path('testimonials/statistics/', testimonials_api_views.api_testimonial_statistics, name='api_statistics'),
    path('testimonials/featured/', testimonials_api_views.api_testimonial_featured, name='api_featured'),
    path('testimonials/high-rated/', testimonials_api_views.api_testimonial_high_rated, name='api_high_rated'),
    path('testimonials/create/', testimonials_api_views.api_testimonial_create, name='api_create'),
    path('testimonials/bulk-create/', testimonials_api_views.api_testimonial_bulk_create, name='api_bulk_create'),
    path('testimonials/bulk-update/', testimonials_api_views.api_testimonial_bulk_update, name='api_bulk_update'),
    path('testimonials/bulk-delete/', testimonials_api_views.api_testimonial_bulk_delete, name='api_bulk_delete'),
    path('testimonials/<int:testimonial_id>/', testimonials_api_views.api_testimonial_detail, name='api_detail'),
    path('testimonials/<int:testimonial_id>/update/', testimonials_api_views.api_testimonial_update, name='api_update'),
    path('testimonials/<int:testimonial_id>/delete/', testimonials_api_views.api_testimonial_delete, name='api_delete'),
    path('testimonials/<int:testimonial_id>/toggle-featured/', testimonials_api_views.api_testimonial_toggle_featured, name='api_toggle_featured'),
    path('testimonials/combined/<int:testimonial_id>/', testimonials_api_views.api_testimonial_combined, name='api_combined'),

    # Resume API endpoints
    path('resume/', resume_api_views.api_resume_list, name='api_list'),
    path('resume/statistics/', resume_api_views.api_resume_statistics, name='api_statistics'),
    path('resume/active/', resume_api_views.api_resume_active, name='api_active'),
    path('resume/search/', resume_api_views.api_resume_search, name='api_search'),
    path('resume/create/', resume_api_views.api_resume_create, name='api_create'),
    path('resume/bulk-delete/', resume_api_views.api_resume_bulk_delete, name='api_bulk_delete'),
    path('resume/<int:pk>/', resume_api_views.api_resume_detail, name='api_detail'),
    path('resume/<int:pk>/update/', resume_api_views.api_resume_update, name='api_update'),
    path('resume/<int:pk>/delete/', resume_api_views.api_resume_delete, name='api_delete'),
    path('resume/<int:pk>/set-active/', resume_api_views.api_resume_set_active, name='api_set_active'),
    path('resume/<int:pk>/download/', resume_api_views.api_resume_download, name='api_download'),
    path('resume/combined/<int:pk>/', resume_api_views.api_resume_combined, name='api_combined'),
]