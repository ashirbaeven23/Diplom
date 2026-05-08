from django.contrib import admin
from django.utils.html import format_html
from django.db import models

from .models import (
    Specialization, AdmissionCampaign, Applicant, 
    Application, ExamResult, Attachment, EnrollmentOrder
)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'faculty', 'budget_places', 'is_active']
    list_filter = ['faculty', 'is_active']
    search_fields = ['code', 'name']


@admin.register(AdmissionCampaign)
class AdmissionCampaignAdmin(admin.ModelAdmin):
    list_display = ['year', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']


class ExamResultInline(admin.TabularInline):
    model = ExamResult
    extra = 0


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    fields = ['specialization', 'priority', 'status', 'is_agreement_signed']
    readonly_fields = ['specialization', 'priority']


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'status', 'created_at']
    list_filter = ['status', 'sex']
    search_fields = ['user__last_name', 'user__first_name', 'phone', 'snils']
    inlines = [ApplicationInline, AttachmentInline]
    actions = ['make_accepted', 'make_rejected']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'ФИО'

    @admin.action(description='Зачислить выбранных абитуриентов')
    def make_accepted(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f'Зачислено абитуриентов: {updated}')

    @admin.action(description='Отказать выбранным абитуриентам')
    def make_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'Отказано абитуриентам: {updated}')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'specialization', 'priority', 'status', 'total_score', 'submission_date']
    list_filter = ['status', 'campaign', 'specialization', 'priority']
    search_fields = ['applicant__user__last_name', 'specialization__name']
    inlines = [ExamResultInline]
    actions = ['make_agreement_signed']

    def total_score(self, obj):
        return obj.exam_results.aggregate(s=models.Sum('score'))['s'] or 0
    total_score.short_description = 'Сумма баллов'

    @admin.action(description='Подписать согласие на зачисление')
    def make_agreement_signed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_agreement_signed=True,
            status='agreement_signed',
            agreement_date=timezone.now()
        )
        self.message_user(request, f'Подписано согласий: {updated}')


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['application', 'subject', 'score', 'is_ege']
    list_filter = ['subject', 'is_ege']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'doc_type', 'is_verified', 'uploaded_at']
    list_filter = ['doc_type', 'is_verified']


@admin.register(EnrollmentOrder)
class EnrollmentOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'order_date', 'campaign', 'created_by']
    filter_horizontal = ['applications']