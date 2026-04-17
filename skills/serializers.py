from rest_framework import serializers
from .models import Skill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'proficiency', 'category', 'icon', 
                 'description', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Skill name is required.")
        if len(value) > 100:
            raise serializers.ValidationError("Skill name cannot exceed 100 characters.")
        return value.strip()
    
    def validate_proficiency(self, value):
        if value is None:
            raise serializers.ValidationError("Proficiency is required.")
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Proficiency must be a number.")
        if value < 0 or value > 100:
            raise serializers.ValidationError("Proficiency must be between 0 and 100.")
        return value
    
    def validate_category(self, value):
        if value and len(value) > 50:
            raise serializers.ValidationError("Category cannot exceed 50 characters.")
        return value
    
    def validate_order(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Order must be a positive number.")
        return value or 0