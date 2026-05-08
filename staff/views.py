from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from applicants.models import (
    Applicant, Application, Specialization, 
    AdmissionCampaign, ExamResult, Attachment, EnrollmentOrder
)


def is_staff_user(user):
    """Проверка: является ли пользователь сотрудником приемной комиссии"""
    return user.is_staff or user.groups.filter(name__in=['Secretary', 'Chairman']).exists()


@login_required
@user_passes_test(is_staff_user)
def staff_dashboard(request):
    """Главная панель сотрудника"""
    active_campaign = AdmissionCampaign.objects.filter(is_active=True).first()
    
    if not active_campaign:
        messages.warning(request, 'Нет активной приемной кампании')
        return render(request, 'staff/dashboard.html', {'campaign': None})
    
    # Статистика
    total_applicants = Applicant.objects.filter(
        applications__campaign=active_campaign
    ).distinct().count()
    
    total_applications = Application.objects.filter(campaign=active_campaign).count()
    
    with_agreement = Application.objects.filter(
        campaign=active_campaign, 
        is_agreement_signed=True
    ).count()
    
    accepted = Application.objects.filter(
        campaign=active_campaign,
        status='accepted'
    ).count()
    
    # Последние заявления
    recent_applications = Application.objects.filter(
        campaign=active_campaign
    ).select_related('applicant', 'specialization').order_by('-submission_date')[:10]
    
    # Специальности с конкурсом
    specializations_stats = []
    for spec in Specialization.objects.filter(is_active=True):
        apps_count = Application.objects.filter(
            campaign=active_campaign,
            specialization=spec
        ).count()
        
        agreement_count = Application.objects.filter(
            campaign=active_campaign,
            specialization=spec,
            is_agreement_signed=True
        ).count()
        
        competition = round(apps_count / spec.budget_places, 1) if spec.budget_places > 0 else 0
        
        specializations_stats.append({
            'name': spec.name,
            'code': spec.code,
            'total': apps_count,
            'with_agreement': agreement_count,
            'budget': spec.budget_places,
            'competition': competition,
        })
    
    context = {
        'campaign': active_campaign,
        'total_applicants': total_applicants,
        'total_applications': total_applications,
        'with_agreement': with_agreement,
        'accepted': accepted,
        'recent_applications': recent_applications,
        'specializations_stats': specializations_stats,
    }
    
    return render(request, 'staff/dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def applicants_list(request):
    """Список всех абитуриентов"""
    active_campaign = AdmissionCampaign.objects.filter(is_active=True).first()
    
    # Фильтры
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    applicants = Applicant.objects.filter(
        applications__campaign=active_campaign
    ).distinct().prefetch_related('applications')
    
    if status_filter:
        applicants = applicants.filter(status=status_filter)
    
    if search:
        applicants = applicants.filter(
            Q(user__last_name__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(snils__icontains=search)
        )
    
    context = {
        'applicants': applicants.order_by('user__last_name'),
        'current_status': status_filter,
        'search': search,
    }
    
    return render(request, 'staff/applicants_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def applicant_detail(request, pk):
    """Просмотр карточки абитуриента"""
    applicant = get_object_or_404(Applicant, pk=pk)
    applications = Application.objects.filter(applicant=applicant).annotate(
        total_score=Sum('exam_results__score')
    )
    attachments = Attachment.objects.filter(applicant=applicant)
    
    context = {
        'applicant': applicant,
        'applications': applications,
        'attachments': attachments,
    }
    
    return render(request, 'staff/applicant_detail.html', context)


@login_required
@user_passes_test(is_staff_user)
def applications_list(request):
    """Управление заявлениями"""
    active_campaign = AdmissionCampaign.objects.filter(is_active=True).first()
    
    spec_filter = request.GET.get('specialization', '')
    status_filter = request.GET.get('status', '')
    
    applications = Application.objects.filter(campaign=active_campaign).annotate(
        total_score=Sum('exam_results__score')
    ).select_related('applicant', 'specialization')
    
    if spec_filter:
        applications = applications.filter(specialization_id=spec_filter)
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    specializations = Specialization.objects.filter(is_active=True)
    
    context = {
        'applications': applications.order_by('-submission_date'),
        'specializations': specializations,
        'current_spec': spec_filter,
        'current_status': status_filter,
    }
    
    return render(request, 'staff/applications_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_application_status(request, pk):
    """Изменение статуса заявления"""
    if request.method != 'POST':
        return redirect('staff_applications')
    
    application = get_object_or_404(Application, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Application.APP_STATUS):
        application.status = new_status
        application.save()
        messages.success(request, f'Статус заявления изменён на "{application.get_status_display()}"')
    
    return redirect('staff_applications')


@login_required
@user_passes_test(is_staff_user)
def add_exam_result(request, application_id):
    """Добавление результата экзамена"""
    application = get_object_or_404(Application, pk=application_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        score = request.POST.get('score')
        is_ege = request.POST.get('is_ege') == 'on'
        
        if subject and score:
            ExamResult.objects.update_or_create(
                application=application,
                subject=subject,
                defaults={
                    'score': int(score),
                    'is_ege': is_ege,
                }
            )
            messages.success(request, f'Результат по предмету "{subject}" сохранён')
        
        return redirect('staff_applicant_detail', pk=application.applicant.pk)
    
    return redirect('staff_applicant_detail', pk=application.applicant.pk)


@login_required
@user_passes_test(is_staff_user)
def staff_statistics(request):
    """Расширенная статистика для сотрудников"""
    active_campaign = AdmissionCampaign.objects.filter(is_active=True).first()
    
    if not active_campaign:
        messages.warning(request, 'Нет активной приемной кампании')
        return redirect('staff_dashboard')
    
    # Статистика по полу
    male_count = Applicant.objects.filter(
        applications__campaign=active_campaign,
        sex='M'
    ).distinct().count()
    
    female_count = Applicant.objects.filter(
        applications__campaign=active_campaign,
        sex='F'
    ).distinct().count()
    
    # Средний балл по специальностям
    specs_avg = []
    for spec in Specialization.objects.filter(is_active=True):
        avg = Application.objects.filter(
            campaign=active_campaign,
            specialization=spec,
            is_agreement_signed=True
        ).annotate(
            total=Sum('exam_results__score')
        ).aggregate(avg_score=Avg('total'))['avg_score']
        
        specs_avg.append({
            'name': spec.name,
            'code': spec.code,
            'avg_score': round(avg, 1) if avg else 0,
        })
    
    # Распределение по статусам
    status_distribution = []
    for status_code, status_name in Application.APP_STATUS:
        count = Application.objects.filter(
            campaign=active_campaign,
            status=status_code
        ).count()
        status_distribution.append({
            'name': status_name,
            'count': count,
        })
    
    context = {
        'male_count': male_count,
        'female_count': female_count,
        'specs_avg': specs_avg,
        'status_distribution': status_distribution,
    }
    
    return render(request, 'staff/statistics.html', context)