from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size_kb = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'file', 'file_url', 'file_name', 'file_size_kb',
            'is_active', 'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Get the URL of the file"""
        if obj.file:
            return obj.file.url
        return None
    
    def get_file_name(self, obj):
        """Get the original file name"""
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None
    
    def get_file_size_kb(self, obj):
        """Get file size in KB"""
        if obj.file and obj.file.size:
            return round(obj.file.size / 1024, 2)
        return 0
    
    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title is required.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value.strip()
    
    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("File is required.")
        
        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        # Validate file extension
        allowed_extensions = ['pdf', 'doc', 'docx']
        file_extension = value.name.lower().split('.')[-1]
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def validate_is_active(self, value):
        """Ensure only one resume can be active"""
        if value:
            # Check if there's already an active resume
            if Resume.objects.filter(is_active=True).exists():
                # This will be handled in the view by deactivating others
                pass
        return value