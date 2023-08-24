from django.urls import path
from . import views
from rest_framework import routers

urlpatterns = [
    path('sessions', views.SessionList.as_view()),
    path("sessions/add", views.SessionAdd.as_view()),
    path("sessions/report",views.DocGenerate),
    path('sessions/video/<int:pk>/', views.SessionVideoView.as_view(), name='session-video'),
    ]
