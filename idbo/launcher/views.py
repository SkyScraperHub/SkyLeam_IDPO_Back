from rest_framework import generics, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import  Session
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from . import serializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication
from launcher.models import Session
from datetime import timedelta, datetime
from services.s3 import MinioClient
class SessionPagination(PageNumberPagination):
    page_size = 20


class Session(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = serializer.SessionSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = SessionPagination
    authentication_classes = (JWTAuthentication,)
    
    def list(self, request):
       
        queryset = self.filter_queryset(self.get_queryset())
        now = datetime.now()
        one_month_ago = now - timedelta(days=30)
        queryset = queryset.filter(date__gte=one_month_ago,user_id=request.auth["id"])
        page = self.paginate_queryset(queryset)
        if page is not None:
            
            serializer = self.get_serializer(page, many=True)
            data = {"page":int(self.request.query_params.get('page'))}
            pagination_info = self.get_paginated_response(serializer.data).data
            data.update(pagination_info)
            return Response(data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class SessionAdd(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication,)
#     @swagger_auto_schema(
#     request_body=openapi.Schema(
#         type=openapi.IN_FORM,
#         properties={
#             'duration': openapi.Schema(type=openapi.TYPE_STRING,defauilt="0:00:00", description='длительность'),
#             'date': openapi.Schema(type=openapi.TYPE_STRING,default="30-03-2023", description='Дата сессии'),
#             'time': openapi.Schema(type=openapi.TYPE_INTEGER, description=' 11:59:01'),
#             'scenario': openapi.Schema(type=openapi.TYPE_STRING, description='Сценарий'),
#             'result': openapi.Schema(type=openapi.TYPE_STRING, description='Результат'),
#             'file': openapi.Schema(type=openapi.TYPE_FILE, description='The uploaded file'),
#         }
#     ),
#     responses={
#         200: openapi.Response(description='OK'),
#         400: openapi.Response(description='Bad Request'),
#         403: openapi.Response(description='Unauthorized'),
#         500: openapi.Response(description='Internal Server Error')
#     }
# ) 
    def post(self,request):
        data = request.data["sessions"]
        if isinstance(data, list):
            for item in range(len(data)):
                data[item]["user_id"] = request.auth["id"]
            serializer_class = serializer.SessionAddSerializer(data=data, many=True)
        elif isinstance(data, dict):
            data["user_id"] = request.auth["id"]
            serializer_class = serializer.SessionAddSerializer(data=data, many=False)
        
        if serializer_class.is_valid(raise_exception=True):
            serializer_class.save()
            return Response()
        else: 
            return Response(serializer_class.error)

# class testDownload(APIView):
#     def post(self, request):
#         data = request.FILES["test"]
#         MinioClient.upload_data("test.png", data, length=data.size)
#         return Response(status=200)
        