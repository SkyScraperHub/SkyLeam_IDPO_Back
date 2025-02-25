from django.urls import path
from rest_framework import routers
from . import views

urlpatterns = [
    path("sessions", views.SessionList.as_view(), name="get-sessions"),
    path("sessions/add", views.SessionAdd.as_view(), name="add-session"),
    path("sessions/report", views.DocGenerate, name="doc-generate"),
    path(
        "sessions/video/<int:pk>/",
        views.SessionVideoView.as_view(),
        name="session-video",
    ),
    path(
        "sessions/scenario",
        views.UniqueScenariosSessionList.as_view(),
        name="unique_scenarios",
    ),
    path("sessions/game", views.GamesList.as_view(), name="games"),
]
