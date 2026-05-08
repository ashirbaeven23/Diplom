from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import serializers

from .models import (
    Specialization, Application, Applicant, AdmissionCampaign
)
from .serializers import (
    SpecializationSerializer, ApplicationSerializer,
    ApplicationCreateSerializer, RatingSerializer,
    ApplicantSerializer
)


class IsOwnerOrStaff(permissions.BasePermission):
    """Разрешение: только владелец или сотрудник"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.applicant.user == request.user


class SpecializationListAPI(generics.ListAPIView):
    """API: список всех специальностей"""
    queryset = Specialization.objects.filter(is_active=True)
    serializer_class = SpecializationSerializer
    permission_classes = [permissions.AllowAny]


class ApplicationListAPI(generics.ListAPIView):
    """API: список заявлений текущего пользователя (абитуриента) или всех (для сотрудников)"""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Application.objects.all()
        try:
            applicant = self.request.user.applicant_profile
            return Application.objects.filter(applicant=applicant)
        except Applicant.DoesNotExist:
            return Application.objects.none()


class ApplicationCreateAPI(generics.CreateAPIView):
    """API: подача заявления"""
    serializer_class = ApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        applicant = self.request.user.applicant_profile
        active_campaign = AdmissionCampaign.objects.filter(is_active=True).first()
        if not active_campaign:
            raise serializers.ValidationError({"error": "Нет активной приемной кампании"})
        serializer.save(applicant=applicant, campaign=active_campaign, status='submitted')


class ApplicationDetailAPI(generics.RetrieveAPIView):
    """API: детали заявления"""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Application.objects.all()
        try:
            return Application.objects.filter(applicant=self.request.user.applicant_profile)
        except Applicant.DoesNotExist:
            return Application.objects.none()


class RatingAPI(generics.ListAPIView):
    """API: рейтинг по специальности"""
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        spec_id = self.kwargs.get('specialization_id')
        return Application.objects.filter(
            specialization_id=spec_id,
            is_agreement_signed=True
        ).annotate(
            total_score=Sum('exam_results__score')
        ).order_by('-total_score', 'submission_date')