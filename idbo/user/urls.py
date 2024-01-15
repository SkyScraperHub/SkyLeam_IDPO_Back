from django.urls import path, include
from django.conf import settings
from .views import CustomTokenObtainPairView, CheckUser

urlpatterns = [
    # ...
    # path('login/', StudentLoginView.as_view(), name='student-login'),
    path("auth", CustomTokenObtainPairView.as_view()),
    path("check-user", CheckUser.as_view()),
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
