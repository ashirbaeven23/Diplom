from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_dashboard, name='staff_dashboard'),
    path('applicants/', views.applicants_list, name='staff_applicants'),
    path('applicants/<int:pk>/', views.applicant_detail, name='staff_applicant_detail'),
    path('applications/', views.applications_list, name='staff_applications'),
    path('applications/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('add-exam-result/<int:application_id>/', views.add_exam_result, name='add_exam_result'),
    path('statistics/', views.staff_statistics, name='staff_statistics'),
]