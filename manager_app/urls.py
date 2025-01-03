# urls.py
from django.urls import path
from .views import DoctorsUnderVSO, ManagerAnalysisAPIView, ManagerProfileAPIView,VSOAndDoctorFilterView


urlpatterns = [
    path('create-manager-profile/', ManagerProfileAPIView.as_view(), name='manager-list-create'),  # List all or create new
    path('manager/<str:manager_id>/update/', ManagerProfileAPIView.as_view(), name='update_manager_profile'),
    
    path('managers/<str:manager_id>/', ManagerProfileAPIView.as_view(), name='manager-detail'),  # Retrieve, update, or delete by manager_id
    path('vso/<str:vso_id>/doctors/', DoctorsUnderVSO.as_view(), name='doctors-under-vso'),

    path('api/vso-doctor-filter/', VSOAndDoctorFilterView.as_view(), name='vso-doctor-filter'),
    path('api/manager-analysis/', ManagerAnalysisAPIView.as_view(), name='manager-analysis'),

 

    
]
