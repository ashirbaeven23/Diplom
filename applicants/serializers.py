from rest_framework import serializers
from .models import (
    Specialization, AdmissionCampaign, Applicant, 
    Application, ExamResult, Attachment
)
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'last_name', 'first_name']


class ApplicantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Applicant
        fields = [
            'id', 'full_name', 'birth_date', 'sex', 
            'phone', 'snils', 'status', 'user'
        ]


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = ['subject', 'score', 'is_ege', 'exam_date']


class ApplicationSerializer(serializers.ModelSerializer):
    exam_results = ExamResultSerializer(many=True, read_only=True)
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    total_score = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'applicant_name', 'specialization_name', 
            'status', 'status_display', 'submission_date',
            'exam_results', 'total_score'
        ]

    def get_total_score(self, obj):
        return obj.exam_results.aggregate(
            total=serializers.models.Sum('score')
        )['total'] or 0


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['specialization', 'priority']


class RatingSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'applicant_name', 'total_score', 'submission_date']

    def get_total_score(self, obj):
        return obj.exam_results.aggregate(
            total=serializers.models.Sum('score')
        )['total'] or 0