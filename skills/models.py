from django.db import models

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('framework', 'Framework'),
        ('library', 'Library'),
        ('tool', 'Tool'),
        ('language', 'Language'),
        ('soft', 'Soft Skill'),
        ('design', 'Design'),
    ]
    
    name = models.CharField(max_length=50)
    proficiency = models.PositiveIntegerField(default=50)  # percentage
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., 'fab fa-python')")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'category', 'name']

    def __str__(self):
        return self.name

    def get_category_color(self):
        colors = {
            'programming': 'bg-blue-100 text-blue-800',
            'framework': 'bg-green-100 text-green-800',
            'tool': 'bg-purple-100 text-purple-800',
            'language': 'bg-red-100 text-red-800',
            'soft': 'bg-pink-100 text-pink-800',
            'design': 'bg-orange-100 text-orange-800',
        }
        return colors.get(self.category, 'bg-gray-100 text-gray-800')