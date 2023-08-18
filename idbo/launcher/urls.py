from django.urls import path
from . import views

urlpatterns = [
    path('sessions', views.Session.as_view()),
    path("sessions/add", views.SessionAdd.as_view()),
    # path("session/add-file", views.testDownload.as_view())
    # path("session/report/{:id}",)
]