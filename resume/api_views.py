from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Resume
from .serializers import ResumeSerializer

@api_view(['GET'])
def api_resume_list(request):
    """List all resumes with search and pagination"""
    # Get query parameters
    search_query = request.GET.get('q', '')
    is_active = request.GET.get('is_active')
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    
    # Base queryset
    resumes = Resume.objects.all()
    
    # Apply search filter
    if search_query:
        resumes = resumes.filter(
            Q(title__icontains=search_query)
        )
    
    # Apply active filter
    if is_active is not None:
        resumes = resumes.filter(is_active=is_active.lower() == 'true')
    
    # Order by uploaded_at descending
    resumes = resumes.order_by('-uploaded_at', '-id')
    
    # Get active resume info
    active_resume = Resume.objects.filter(is_active=True).first()
    
    # Statistics
    stats = {
        'total_count': Resume.objects.count(),
        'active_count': Resume.objects.filter(is_active=True).count(),
        'inactive_count': Resume.objects.filter(is_active=False).count(),
        'has_active_resume': active_resume is not None,
        'active_resume_id': active_resume.id if active_resume else None,
        'active_resume_title': active_resume.title if active_resume else None,
    }
    
    # Pagination
    paginator = Paginator(resumes, page_size)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
    
    # Serialize the data
    serializer = ResumeSerializer(page_obj.object_list, many=True)
    
    response_data = {
        'statistics': stats,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        },
        'results': serializer.data,
        'filters_applied': {
            'search_query': search_query,
            'is_active': is_active,
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_resume_detail(request, pk):
    """Get a single resume by ID"""
    resume = get_object_or_404(Resume, pk=pk)
    serializer = ResumeSerializer(resume)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_resume_create(request):
    """Create a new resume"""
    # Validate file
    file_obj = request.FILES.get('file')
    
    if not file_obj:
        return Response({
            'message': 'File is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    file_extension = file_obj.name.lower().split('.')[-1]
    allowed_extensions = ['pdf', 'doc', 'docx']
    
    if file_extension not in allowed_extensions:
        return Response({
            'message': 'Invalid file type. Please upload a PDF, DOC, or DOCX file.',
            'allowed_types': allowed_extensions
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create resume with file
    data = request.data.copy()
    data['file'] = file_obj
    
    serializer = ResumeSerializer(data=data)
    
    if serializer.is_valid():
        # If this resume is active, deactivate all other active resumes
        if serializer.validated_data.get('is_active', False):
            Resume.objects.filter(is_active=True).update(is_active=False)
        
        serializer.save()
        return Response({
            'message': 'Resume uploaded successfully!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Validation failed. Title and file are required.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def api_resume_update(request, pk):
    """Update a resume completely (PUT) or partially (PATCH)"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Handle file upload if present
    data = request.data.copy()
    file_obj = request.FILES.get('file')
    
    if file_obj:
        # Validate file type
        file_extension = file_obj.name.lower().split('.')[-1]
        allowed_extensions = ['pdf', 'doc', 'docx']
        
        if file_extension not in allowed_extensions:
            return Response({
                'message': 'Invalid file type. Please upload a PDF, DOC, or DOCX file.',
                'allowed_types': allowed_extensions
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data['file'] = file_obj
    
    # For partial updates, use partial=True
    serializer = ResumeSerializer(resume, data=data, partial=request.method == 'PATCH')
    
    if serializer.is_valid():
        # If setting as active, deactivate all other active resumes
        if serializer.validated_data.get('is_active', False):
            Resume.objects.filter(is_active=True).exclude(pk=pk).update(is_active=False)
        
        serializer.save()
        return Response({
            'message': 'Resume updated successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Update failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_resume_delete(request, pk):
    """Delete a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    resume_title = resume.title
    resume.delete()
    
    return Response({
        'message': f'Resume "{resume_title}" deleted successfully!'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_resume_active(request):
    """Get the currently active resume"""
    resume = Resume.objects.filter(is_active=True).first()
    
    if resume:
        serializer = ResumeSerializer(resume)
        return Response({
            'has_active_resume': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'has_active_resume': False,
        'message': 'No active resume found.'
    }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def api_resume_set_active(request, pk):
    """Set a specific resume as active"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Deactivate all other resumes
    Resume.objects.filter(is_active=True).update(is_active=False)
    
    # Activate the selected resume
    resume.is_active = True
    resume.save()
    
    serializer = ResumeSerializer(resume)
    
    return Response({
        'message': f'Resume "{resume.title}" is now active.',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_resume_download(request, pk):
    """Get download URL for a resume file"""
    resume = get_object_or_404(Resume, pk=pk)
    
    return Response({
        'resume_id': resume.id,
        'resume_title': resume.title,
        'file_url': resume.file.url if resume.file else None,
        'file_name': resume.file.name.split('/')[-1] if resume.file else None,
        'file_size': resume.file.size if resume.file else 0,
        'uploaded_at': resume.uploaded_at,
        'download_url': request.build_absolute_uri(resume.file.url) if resume.file else None
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_resume_statistics(request):
    """Get statistics about resumes"""
    from django.utils import timezone
    from datetime import timedelta
    
    total = Resume.objects.count()
    active_count = Resume.objects.filter(is_active=True).count()
    inactive_count = Resume.objects.filter(is_active=False).count()
    
    # Recent uploads (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_uploads = Resume.objects.filter(uploaded_at__gte=thirty_days_ago).count()
    
    # File type distribution
    file_types = {
        'pdf': Resume.objects.filter(file__name__endswith='.pdf').count(),
        'doc': Resume.objects.filter(file__name__endswith='.doc').count(),
        'docx': Resume.objects.filter(file__name__endswith='.docx').count(),
    }
    
    stats = {
        'total_resumes': total,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'recent_uploads_30d': recent_uploads,
        'has_active_resume': active_count > 0,
        'file_type_distribution': file_types,
        'storage_summary': {
            'total_files': total,
            'active_file': active_count
        }
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_resume_bulk_delete(request):
    """Delete multiple resumes at once"""
    resume_ids = request.data.get('ids', [])
    
    if not resume_ids:
        return Response({
            'message': 'No resume IDs provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    resumes = Resume.objects.filter(pk__in=resume_ids)
    
    # Check if trying to delete active resume
    active_in_batch = resumes.filter(is_active=True).exists()
    
    deleted_count = resumes.count()
    deleted_titles = list(resumes.values_list('title', flat=True))
    resumes.delete()
    
    response_message = f'Successfully deleted {deleted_count} resume(s).'
    if active_in_batch:
        response_message += ' Note: An active resume was deleted.'
    
    return Response({
        'message': response_message,
        'deleted_count': deleted_count,
        'deleted_resumes': deleted_titles,
        'active_deleted': active_in_batch
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_resume_search(request):
    """Advanced search for resumes"""
    title = request.GET.get('title', '')
    is_active = request.GET.get('is_active')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    resumes = Resume.objects.all()
    
    if title:
        resumes = resumes.filter(title__icontains=title)
    
    if is_active is not None:
        resumes = resumes.filter(is_active=is_active.lower() == 'true')
    
    if from_date:
        resumes = resumes.filter(uploaded_at__date__gte=from_date)
    
    if to_date:
        resumes = resumes.filter(uploaded_at__date__lte=to_date)
    
    resumes = resumes.order_by('-uploaded_at')
    
    serializer = ResumeSerializer(resumes, many=True)
    
    return Response({
        'count': resumes.count(),
        'results': serializer.data,
        'search_criteria': {
            'title': title,
            'is_active': is_active,
            'from_date': from_date,
            'to_date': to_date
        }
    }, status=status.HTTP_200_OK)

# Combined view for detail operations
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_resume_combined(request, pk):
    """Combined view for single resume operations"""
    resume = get_object_or_404(Resume, pk=pk)
    
    if request.method == 'GET':
        serializer = ResumeSerializer(resume)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Handle file upload if present
        data = request.data.copy()
        file_obj = request.FILES.get('file')
        
        if file_obj:
            # Validate file type
            file_extension = file_obj.name.lower().split('.')[-1]
            allowed_extensions = ['pdf', 'doc', 'docx']
            
            if file_extension not in allowed_extensions:
                return Response({
                    'message': 'Invalid file type. Please upload a PDF, DOC, or DOCX file.',
                    'allowed_types': allowed_extensions
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data['file'] = file_obj
        
        serializer = ResumeSerializer(resume, data=data, partial=request.method == 'PATCH')
        
        if serializer.is_valid():
            # If setting as active, deactivate all other active resumes
            if serializer.validated_data.get('is_active', False):
                Resume.objects.filter(is_active=True).exclude(pk=pk).update(is_active=False)
            
            serializer.save()
            return Response({
                'message': 'Resume updated successfully!',
                'data': serializer.data
            })
        return Response({
            'message': 'Update failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        resume_title = resume.title
        resume.delete()
        return Response({
            'message': f'Resume "{resume_title}" deleted successfully!'
        }, status=status.HTTP_204_NO_CONTENT)