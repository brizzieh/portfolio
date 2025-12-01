from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg
from .models import Skill

def skill_list(request):
    skills = Skill.objects.filter(is_active=True)
    
    # Calculate stats
    total_skills = skills.count()
    
    # Count expert skills (proficiency >= 80)
    expert_skills = skills.filter(proficiency__gte=80).count()
    
    # Get unique categories count
    categories_count = skills.values('category').distinct().count()
    
    # Calculate average proficiency
    avg_proficiency = skills.aggregate(avg=Avg('proficiency'))['avg'] or 0
    
    # Group skills by category
    categories = {}
    for skill in skills:
        if skill.category not in categories:
            categories[skill.category] = []
        categories[skill.category].append(skill)
    
    return render(request, 'dashboard/skills/list.html', {
        'categories': categories,
        'total_skills': total_skills,
        'expert_skills': expert_skills,
        'categories_count': categories_count,
        'avg_proficiency': round(avg_proficiency),
        'skills': skills
    })

def skill_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        proficiency = request.POST.get('proficiency')
        category = request.POST.get('category')
        icon = request.POST.get('icon')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not name or not proficiency:
            messages.error(request, 'Name and proficiency are required.')
            return render(request, 'dashboard/skills/form.html', {
                'form_title': 'Add New Skill',
                'submit_button_text': 'Create Skill',
                'skill': None
            })
        
        try:
            Skill.objects.create(
                name=name,
                proficiency=int(proficiency),
                category=category,
                icon=icon,
                description=description,
                order=int(order),
                is_active=is_active
            )
            messages.success(request, 'Skill created successfully!')
            return redirect('skills:list')
        except Exception as e:
            messages.error(request, f'Error creating skill: {str(e)}')
            return render(request, 'dashboard/skills/form.html', {
                'form_title': 'Add New Skill',
                'submit_button_text': 'Create Skill',
                'skill': None
            })
    
    return render(request, 'dashboard/skills/form.html', {
        'form_title': 'Add New Skill',
        'submit_button_text': 'Create Skill',
        'skill': None
    })

def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        proficiency = request.POST.get('proficiency')
        category = request.POST.get('category')
        icon = request.POST.get('icon')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not name or not proficiency:
            messages.error(request, 'Name and proficiency are required.')
            return render(request, 'dashboard/skills/form.html', {
                'form_title': 'Edit Skill',
                'submit_button_text': 'Update Skill',
                'skill': skill
            })
        
        try:
            skill.name = name
            skill.proficiency = int(proficiency)
            skill.category = category
            skill.icon = icon
            skill.description = description
            skill.order = int(order)
            skill.is_active = is_active
            skill.save()
            
            messages.success(request, 'Skill updated successfully!')
            return redirect('skills:list')
        except Exception as e:
            messages.error(request, f'Error updating skill: {str(e)}')
            return render(request, 'dashboard/skills/form.html', {
                'form_title': 'Edit Skill',
                'submit_button_text': 'Update Skill',
                'skill': skill
            })
    
    return render(request, 'dashboard/skills/form.html', {
        'form_title': 'Edit Skill',
        'submit_button_text': 'Update Skill',
        'skill': skill
    })

def skill_delete(request, pk):
    if request.method == 'POST':
        skill = get_object_or_404(Skill, pk=pk)
        skill_name = skill.name
        skill.delete()
        messages.success(request, f'Skill "{skill_name}" deleted successfully!')
        return redirect('skills:list')
    
    return redirect('skills:list')