from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'url', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title is required.")
        return value
    
    def validate_description(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Description is required.")
        return value