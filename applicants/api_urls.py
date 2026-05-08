from django.urls import path
from . import api_views

urlpatterns = [
    # Специальности
    path('specializations/', api_views.SpecializationListAPI.as_view(), name='api_specializations'),
    # Заявления
    path('applications/', api_views.ApplicationListAPI.as_view(), name='api_applications'),
    path('applications/create/', api_views.ApplicationCreateAPI.as_view(), name='api_application_create'),
    path('applications/<int:pk>/', api_views.ApplicationDetailAPI.as_view(), name='api_application_detail'),
    # Рейтинг
    path('rating/<int:specialization_id>/', api_views.RatingAPI.as_view(), name='api_rating'),
]