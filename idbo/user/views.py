from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import JSONWebTokenSerializer
from rest_framework_simplejwt.views import ObtainJSONWebToken

class ManagerLoginView(ObtainJSONWebToken):
    serializer_class = JSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = self.user
            if user.is_administrator and user.position == 'manager':
                return response
            return Response({'detail': 'Only manager users are allowed to log in.'}, status=status.HTTP_403_FORBIDDEN)
        return response
