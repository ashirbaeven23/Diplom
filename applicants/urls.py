from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('application/create/', views.create_application, name='create_application'),

    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/sign-agreement/', views.sign_agreement, name='sign_agreement'),
    path('rating/<int:specialization_id>/', views.rating_view, name='rating'),
    path('rating/<int:specialization_id>/export/', views.export_rating_excel, name='export_rating_excel'),
    path('profile/', views.profile_view, name='profile'),

    path('upload-document/old/', views.upload_document, name='upload_document'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('enrollment-orders/', views.enrollment_orders_list, name='enrollment_orders'),
    path('enrollment-orders/create/', views.create_order, name='create_order'),
    path('enrollment-orders/<int:order_id>/download/', views.download_order_pdf, name='download_order'),
    path('upload-document/', views.upload_document_page, name='upload_document_page'),
]