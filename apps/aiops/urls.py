from django.urls import path
from .views.dashboard import aiops_dashboard, metrics_api, alerts_api, incidents_api

urlpatterns = [
    path('', aiops_dashboard, name='aiops_dashboard'),
    path('api/metrics/', metrics_api, name='metrics_api'),
    path('api/alerts/', alerts_api, name='alerts_api'),
    path('api/incidents/', incidents_api, name='incidents_api'),
]