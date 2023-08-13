from django.urls import path, include
from django.conf import settings
from .views import StudentLoginView

urlpatterns = [
    # ...
    path('login/', StudentLoginView.as_view(), name='student-login'),
    # ...
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
