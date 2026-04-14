from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Project
from .serializers import ProjectSerializer

@api_view(['GET'])
def api_list(request):
    """List all projects with search and pagination"""
    search_query = request.GET.get('q', '')
    
    if search_query:
        projects = Project.objects.filter(
            title__icontains=search_query
        ).order_by('-created_at')
    else:
        projects = Project.objects.all().order_by('-created_at')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(projects, 10)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
    
    # Serialize the data
    serializer = ProjectSerializer(page_obj.object_list, many=True)
    
    response_data = {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'results': serializer.data,
        'search_query': search_query,
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_create(request):
    """Create a new project"""
    serializer = ProjectSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Project created successfully!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Please fill in all required fields.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_show(request, id):
    """Get a single project by ID"""
    project = get_object_or_404(Project, id=id)
    serializer = ProjectSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
def api_update(request, project_id):
    """Update a project completely (PUT) or partially (PATCH)"""
    project = get_object_or_404(Project, id=project_id)
    
    # For partial updates, use partial=True
    serializer = ProjectSerializer(project, data=request.data, partial=request.method == 'PATCH')
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Project updated successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Update failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete(request, project_id):
    """Delete a project"""
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    
    return Response({
        'message': 'Project deleted successfully!'
    }, status=status.HTTP_204_NO_CONTENT)

# Optional: Combined view for detail operations (GET, PUT, DELETE)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_project_detail(request, project_id):
    """Combined view for single project operations"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectSerializer(project, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Project updated successfully!',
                'data': serializer.data
            })
        return Response({
            'message': 'Update failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        project.delete()
        return Response({
            'message': 'Project deleted successfully!'
        }, status=status.HTTP_204_NO_CONTENT)

# Optional: Bulk delete endpoint
@api_view(['DELETE'])
def api_bulk_delete(request):
    """Delete multiple projects at once"""
    project_ids = request.data.get('ids', [])
    
    if not project_ids:
        return Response({
            'message': 'No project IDs provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    projects = Project.objects.filter(id__in=project_ids)
    deleted_count = projects.count()
    projects.delete()
    
    return Response({
        'message': f'Successfully deleted {deleted_count} project(s).',
        'deleted_count': deleted_count
    }, status=status.HTTP_200_OK)