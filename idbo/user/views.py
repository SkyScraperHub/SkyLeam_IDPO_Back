from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

# Кастомный класс для получения токена доступа
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            user = serializer.user
            # Проверка, что пользователь - студент
            if user.position != 'student':
                return Response(
                    {"details": "Only students can log in"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            tokens = serializer.validated_data
            user_name = f'{user.last_name} {user.first_name} {user.middle_name}'
            return Response(
                {   "firstName": user.first_name,
                    "middleName": "" if user.middle_name is None else user.middle_name,
                    "lastName": user.last_name,
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                },
                status=status.HTTP_200_OK,
            )


# Проверка наличия аутентификации и разрешения у пользователя
class CheckUser(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        try:
            user = request.user
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            if type(e).__name__ == "InvalidToken":
                return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
