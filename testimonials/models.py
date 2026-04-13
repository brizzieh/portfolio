from django.db import models

class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    client_position = models.CharField(max_length=100, blank=True)
    client_company = models.CharField(max_length=100, blank=True)
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    is_featured = models.BooleanField(default=False)
    project_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"{self.client_name} - {self.client_company}"