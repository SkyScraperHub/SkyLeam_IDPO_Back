from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from .models import User

class StudentLoginView(APIView):
    def post(self, request, *args, **kwargs):
        login1 = request.data.get('login')
        password1 = request.data.get('password')

        user = User.objects.get(login=str(login1)[1:-1], password = str(password1)[1:-1])

        if user and user.position == 'student':
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({'token': token})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    def get(self, request, *args, **kwargs):
        try:
            login1 = self.request.query_params['login']
            password1 = self.request.query_params['password']
            user = User.objects.get(login=str(login1)[1:-1], password = str(password1)[1:-1])

            if user and user.position == 'student':
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)

                return Response({'token': token})
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except KeyError:
            raise AuthenticationFailed('Invalid data. Provide both "login" and "password" parameters.')
