from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Skill
from .serializers import SkillSerializer

@api_view(['GET'])
def api_skill_list(request):
    """List all active skills with statistics"""
    # Get query parameters
    is_active = request.GET.get('is_active')
    category = request.GET.get('category')
    min_proficiency = request.GET.get('min_proficiency')
    search = request.GET.get('search')
    
    # Base queryset
    if is_active is not None:
        skills = Skill.objects.filter(is_active=is_active.lower() == 'true')
    else:
        skills = Skill.objects.all()
    
    # Apply filters
    if category:
        skills = skills.filter(category=category)
    
    if min_proficiency:
        skills = skills.filter(proficiency__gte=int(min_proficiency))
    
    if search:
        skills = skills.filter(name__icontains=search)
    
    # Order by order field, then name
    skills = skills.order_by('order', 'name')
    
    # Calculate statistics
    total_skills = skills.count()
    expert_skills = skills.filter(proficiency__gte=80).count()
    categories_count = skills.values('category').distinct().count()
    avg_proficiency = skills.aggregate(avg=Avg('proficiency'))['avg'] or 0
    
    # Group skills by category
    categories_dict = {}
    for skill in skills:
        if skill.category not in categories_dict:
            categories_dict[skill.category] = []
        categories_dict[skill.category].append(skill)
    
    # Serialize the data - FIXED: Serialize each skill individually
    skills_by_category_serialized = {}
    for cat, cat_skills in categories_dict.items():
        serializer = SkillSerializer(cat_skills, many=True)
        skills_by_category_serialized[cat] = serializer.data
    
    # Serialize all skills
    all_skills_serializer = SkillSerializer(skills, many=True)
    
    # Get unique categories list
    unique_categories = skills.values_list('category', flat=True).distinct()
    
    response_data = {
        'statistics': {
            'total_skills': total_skills,
            'expert_skills': expert_skills,
            'categories_count': categories_count,
            'average_proficiency': round(avg_proficiency),
        },
        'categories': list(unique_categories),
        'skills_by_category': skills_by_category_serialized,
        'all_skills': all_skills_serializer.data,
        'filters_applied': {
            'is_active': is_active,
            'category': category,
            'min_proficiency': min_proficiency,
            'search': search
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_skill_detail(request, pk):
    """Get a single skill by ID"""
    skill = get_object_or_404(Skill, pk=pk)
    serializer = SkillSerializer(skill)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_skill_create(request):
    """Create a new skill"""
    serializer = SkillSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Skill created successfully!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Validation failed. Name and proficiency are required.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def api_skill_update(request, pk):
    """Update a skill completely (PUT) or partially (PATCH)"""
    skill = get_object_or_404(Skill, pk=pk)
    
    # For partial updates, use partial=True
    serializer = SkillSerializer(skill, data=request.data, partial=request.method == 'PATCH')
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Skill updated successfully!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Update failed. Name and proficiency are required.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_skill_delete(request, pk):
    """Delete a skill"""
    skill = get_object_or_404(Skill, pk=pk)
    skill_name = skill.name
    skill.delete()
    
    return Response({
        'message': f'Skill "{skill_name}" deleted successfully!'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_skill_statistics(request):
    """Get only statistics about skills"""
    skills = Skill.objects.filter(is_active=True)
    
    # Calculate statistics
    total_skills = skills.count()
    expert_skills = skills.filter(proficiency__gte=80).count()
    advanced_skills = skills.filter(proficiency__gte=70, proficiency__lt=80).count()
    intermediate_skills = skills.filter(proficiency__gte=50, proficiency__lt=70).count()
    beginner_skills = skills.filter(proficiency__lt=50).count()
    
    # Category statistics
    category_stats = {}
    for skill in skills:
        if skill.category not in category_stats:
            category_stats[skill.category] = {
                'count': 0,
                'avg_proficiency': 0,
                'total_proficiency': 0
            }
        category_stats[skill.category]['count'] += 1
        category_stats[skill.category]['total_proficiency'] += skill.proficiency
    
    # Calculate averages for each category
    for cat in category_stats:
        category_stats[cat]['avg_proficiency'] = round(
            category_stats[cat]['total_proficiency'] / category_stats[cat]['count']
        )
        del category_stats[cat]['total_proficiency']
    
    stats = {
        'total_skills': total_skills,
        'expert_skills': expert_skills,
        'advanced_skills': advanced_skills,
        'intermediate_skills': intermediate_skills,
        'beginner_skills': beginner_skills,
        'average_proficiency': round(skills.aggregate(avg=Avg('proficiency'))['avg'] or 0),
        'category_statistics': category_stats
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_skill_bulk_create(request):
    """Create multiple skills at once"""
    skills_data = request.data.get('skills', [])
    
    if not skills_data:
        return Response({
            'message': 'No skills data provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_skills = []
    errors = []
    
    for index, skill_data in enumerate(skills_data):
        serializer = SkillSerializer(data=skill_data)
        if serializer.is_valid():
            skill = serializer.save()
            created_skills.append(serializer.data)
        else:
            errors.append({
                'index': index,
                'data': skill_data,
                'errors': serializer.errors
            })
    
    return Response({
        'message': f'Successfully created {len(created_skills)} skills.',
        'created_count': len(created_skills),
        'error_count': len(errors),
        'created_skills': created_skills,
        'errors': errors
    }, status=status.HTTP_201_CREATED if created_skills else status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def api_skill_bulk_update(request):
    """Update multiple skills at once"""
    skills_data = request.data.get('skills', [])
    
    if not skills_data:
        return Response({
            'message': 'No skills data provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    updated_skills = []
    errors = []
    
    for skill_data in skills_data:
        skill_id = skill_data.get('id')
        if not skill_id:
            errors.append({
                'data': skill_data,
                'error': 'ID is required for update'
            })
            continue
        
        try:
            skill = Skill.objects.get(pk=skill_id)
            serializer = SkillSerializer(skill, data=skill_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_skills.append(serializer.data)
            else:
                errors.append({
                    'id': skill_id,
                    'data': skill_data,
                    'errors': serializer.errors
                })
        except Skill.DoesNotExist:
            errors.append({
                'id': skill_id,
                'error': 'Skill not found'
            })
    
    return Response({
        'message': f'Successfully updated {len(updated_skills)} skills.',
        'updated_count': len(updated_skills),
        'error_count': len(errors),
        'updated_skills': updated_skills,
        'errors': errors
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def api_skill_bulk_delete(request):
    """Delete multiple skills at once"""
    skill_ids = request.data.get('ids', [])
    
    if not skill_ids:
        return Response({
            'message': 'No skill IDs provided.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    skills = Skill.objects.filter(pk__in=skill_ids)
    deleted_count = skills.count()
    deleted_names = list(skills.values_list('name', flat=True))
    skills.delete()
    
    return Response({
        'message': f'Successfully deleted {deleted_count} skill(s).',
        'deleted_count': deleted_count,
        'deleted_skills': deleted_names
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_skill_categories(request):
    """Get all unique skill categories"""
    categories = Skill.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Get category details
    category_details = []
    for category in categories:
        if category:  # Skip None/null categories
            skills_in_category = Skill.objects.filter(category=category)
            category_details.append({
                'name': category,
                'skill_count': skills_in_category.count(),
                'average_proficiency': round(skills_in_category.aggregate(avg=Avg('proficiency'))['avg'] or 0)
            })
    
    return Response({
        'categories': [cat for cat in categories if cat],  # Filter out None values
        'category_details': category_details
    }, status=status.HTTP_200_OK)

# Combined view for detail operations
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_skill_combined(request, pk):
    """Combined view for single skill operations"""
    skill = get_object_or_404(Skill, pk=pk)
    
    if request.method == 'GET':
        serializer = SkillSerializer(skill)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = SkillSerializer(skill, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Skill updated successfully!',
                'data': serializer.data
            })
        return Response({
            'message': 'Update failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        skill_name = skill.name
        skill.delete()
        return Response({
            'message': f'Skill "{skill_name}" deleted successfully!'
        }, status=status.HTTP_204_NO_CONTENT)