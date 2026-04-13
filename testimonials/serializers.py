from rest_framework import serializers
from .models import Testimonial

class TestimonialSerializer(serializers.ModelSerializer):
    rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_position', 'client_company',
            'content', 'rating', 'rating_display', 'is_featured',
            'project_url', 'client_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_rating_display(self, obj):
        """Return a star rating display"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return stars
    
    def validate_client_name(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Client name is required.")
        if len(value) > 100:
            raise serializers.ValidationError("Client name cannot exceed 100 characters.")
        return value.strip()
    
    def validate_content(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Content is required.")
        if len(value) > 1000:
            raise serializers.ValidationError("Content cannot exceed 1000 characters.")
        return value.strip()
    
    def validate_rating(self, value):
        if value is None:
            value = 5
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Rating must be a number.")
        
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate_client_position(self, value):
        if value and len(value) > 100:
            raise serializers.ValidationError("Position cannot exceed 100 characters.")
        return value
    
    def validate_client_company(self, value):
        if value and len(value) > 100:
            raise serializers.ValidationError("Company name cannot exceed 100 characters.")
        return value
    
    def validate_project_url(self, value):
        if value and len(value) > 200:
            raise serializers.ValidationError("Project URL cannot exceed 200 characters.")
        return value