from django.db import models

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title