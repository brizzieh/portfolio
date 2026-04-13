from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Testimonial
from .serializers import TestimonialSerializer

@api_view(['GET'])
def api_testimonial_list(request):
    """List all testimonials with search and filtering"""
    # Get query parameters
    search_query = request.GET.get('q', '')
    filter_featured = request.GET.get('featured', '')
    min_rating = request.GET.get('min_rating')
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    
    # Base queryset
    testimonials = Testimonial.objects.all()
    
    # Apply search filter
    if search_query:
        testimonials = testimonials.filter(
            Q(client_name__icontains=search_query) |
            Q(client_company__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Apply featured filter
    if filter_featured and filter_featured.lower() == 'true':
        testimonials = testimonials.filter(is_featured=True)
    
    # Apply rating filter
    if min_rating:
        try:
            min_rating = int(min_rating)
            testimonials = testimonials.filter(rating__gte=min_rating)
        except ValueError:
            pass
    
    # Order by created_at descending
    testimonials = testimonials.order_by('-created_at', '-id')
    
    # Calculate statistics
    stats = {
        'total_count': Testimonial.objects.count(),
        'featured_count': Testimonial.objects.filter(is_featured=True).count(),
        'average_rating': Testimonial.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
        'rating_distribution': {
            '5_star': Testimonial.objects.filter(rating=5).count(),
            '4_star': Testimonial.objects.filter(rating=4).count(),
            '3_star': Testimonial.objects.filter(rating=3).count(),
            '2_star': Testimonial.objects.filter(rating=2).count(),
            '1_star': Testimonial.objects.filter(rating=1).count(),
        }
    }
    
    # Pagination
    paginator = Paginator(testimonials, page_size)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
    
    # Serialize the data
    serializer = TestimonialSerializer(page_obj.object_list, many=True)
    
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
            'featured_only': filter_featured == 'true',
            'min_rating': min_rating if min_rating else None,
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_testimonial_detail(request, testimonial_id):
    """Get a single testimonial by ID"""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    serializer = TestimonialSerializer(testimonial)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_testimonial_create(request):
    """Create a new testimonial"""
    serializer = TestimonialSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Testimonial created successfully!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Validation failed. Client name and content are required.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def api_testimonial_update(request, testimonial_id):
    """Update a testimonial completely (PUT) or partially (PATCH)"""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    
    # For partial updates, use partial=True
    serializer = TestimonialSerializer(testimonial, data=request.data, partial=request.method == 'PATCH')
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Testimonial updated successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Update failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_testimonial_delete(request, testimonial_id):
    """Delete a testimonial"""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    client_name = testimonial.client_name
    testimonial.delete()
    
    return Response({
        'message': f'Testimonial from "{client_name}" deleted successfully!'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_testimonial_featured(request):
    """Get all featured testimonials"""
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('-created_at')
    serializer = TestimonialSerializer(testimonials, many=True)
    
    return Response({
        'count': testimonials.count(),
        'featured_testimonials': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_testimonial_statistics(request):
    """Get statistics about testimonials"""
    total = Testimonial.objects.count()
    featured = Testimonial.objects.filter(is_featured=True).count()
    avg_rating = Testimonial.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Rating breakdown
    rating_breakdown = {
        5: Testimonial.objects.filter(rating=5).count(),
        4: Testimonial.objects.filter(rating=4).count(),
        3: Testimonial.objects.filter(rating=3).count(),
        2: Testimonial.objects.filter(rating=2).count(),
        1: Testimonial.objects.filter(rating=1).count(),
    }
    
    # Recent testimonials (last 30 days)
    from django.utils import timezone
    from datetime import timedelta
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent = Testimonial.objects.filter(created_at__gte=thirty_days_ago).count()
    
    stats = {
        'total_testimonials': total,
        'featured_testimonials': featured,
        'average_rating': round(avg_rating, 1),
        'recent_testimonials_30d': recent,
        'rating_breakdown': rating_breakdown,
        'has_testimonials': total > 0,
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_testimonial_bulk_create(request):
    """Create multiple testimonials at once"""
    testimonials_data = request.data.get('testimonials', [])
    
    if not testimonials_data:
        return Response({
            'message': 'No testimonials data provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_testimonials = []
    errors = []
    
    for index, testimonial_data in enumerate(testimonials_data):
        serializer = TestimonialSerializer(data=testimonial_data)
        if serializer.is_valid():
            testimonial = serializer.save()
            created_testimonials.append(serializer.data)
        else:
            errors.append({
                'index': index,
                'data': testimonial_data,
                'errors': serializer.errors
            })
    
    return Response({
        'message': f'Successfully created {len(created_testimonials)} testimonials.',
        'created_count': len(created_testimonials),
        'error_count': len(errors),
        'created_testimonials': created_testimonials,
        'errors': errors
    }, status=status.HTTP_201_CREATED if created_testimonials else status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def api_testimonial_bulk_update(request):
    """Update multiple testimonials at once"""
    testimonials_data = request.data.get('testimonials', [])
    
    if not testimonials_data:
        return Response({
            'message': 'No testimonials data provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    updated_testimonials = []
    errors = []
    
    for testimonial_data in testimonials_data:
        testimonial_id = testimonial_data.get('id')
        if not testimonial_id:
            errors.append({
                'data': testimonial_data,
                'error': 'ID is required for update'
            })
            continue
        
        try:
            testimonial = Testimonial.objects.get(id=testimonial_id)
            serializer = TestimonialSerializer(testimonial, data=testimonial_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_testimonials.append(serializer.data)
            else:
                errors.append({
                    'id': testimonial_id,
                    'data': testimonial_data,
                    'errors': serializer.errors
                })
        except Testimonial.DoesNotExist:
            errors.append({
                'id': testimonial_id,
                'error': 'Testimonial not found'
            })
    
    return Response({
        'message': f'Successfully updated {len(updated_testimonials)} testimonials.',
        'updated_count': len(updated_testimonials),
        'error_count': len(errors),
        'updated_testimonials': updated_testimonials,
        'errors': errors
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def api_testimonial_bulk_delete(request):
    """Delete multiple testimonials at once"""
    testimonial_ids = request.data.get('ids', [])
    
    if not testimonial_ids:
        return Response({
            'message': 'No testimonial IDs provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    testimonials = Testimonial.objects.filter(id__in=testimonial_ids)
    deleted_count = testimonials.count()
    deleted_names = list(testimonials.values_list('client_name', flat=True))
    testimonials.delete()
    
    return Response({
        'message': f'Successfully deleted {deleted_count} testimonial(s).',
        'deleted_count': deleted_count,
        'deleted_testimonials': deleted_names
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_testimonial_toggle_featured(request, testimonial_id):
    """Toggle featured status of a testimonial"""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    testimonial.is_featured = not testimonial.is_featured
    testimonial.save()
    
    return Response({
        'message': f'Testimonial {"featured" if testimonial.is_featured else "unfeatured"} successfully!',
        'is_featured': testimonial.is_featured,
        'testimonial_id': testimonial.id,
        'client_name': testimonial.client_name
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_testimonial_high_rated(request):
    """Get testimonials with high ratings (4 or 5 stars)"""
    min_rating = request.GET.get('min_rating', 4)
    limit = request.GET.get('limit', 10)
    
    try:
        min_rating = int(min_rating)
        limit = int(limit)
    except ValueError:
        min_rating = 4
        limit = 10
    
    testimonials = Testimonial.objects.filter(rating__gte=min_rating).order_by('-rating', '-created_at')[:limit]
    serializer = TestimonialSerializer(testimonials, many=True)
    
    return Response({
        'count': len(serializer.data),
        'min_rating': min_rating,
        'testimonials': serializer.data
    }, status=status.HTTP_200_OK)

# Combined view for detail operations
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_testimonial_combined(request, testimonial_id):
    """Combined view for single testimonial operations"""
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    
    if request.method == 'GET':
        serializer = TestimonialSerializer(testimonial)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = TestimonialSerializer(testimonial, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Testimonial updated successfully!',
                'data': serializer.data
            })
        return Response({
            'message': 'Update failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        client_name = testimonial.client_name
        testimonial.delete()
        return Response({
            'message': f'Testimonial from "{client_name}" deleted successfully!'
        }, status=status.HTTP_204_NO_CONTENT)