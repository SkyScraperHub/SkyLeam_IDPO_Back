from rest_framework import generics, exceptions, request, status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import  Session
from django.http import FileResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.views import APIView
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
from rest_framework import parsers
from utils import get_random_string
from django.template import loader
from django.http import HttpResponse

from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
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
        queryset = queryset.filter(FK_user=request.auth["id"])
        page = self.paginate_queryset(queryset)
        if page is not None:
            
            serializer = self.get_serializer(page, many=True)
            data = {"page":int(self.request.query_params.get('page'))}
            pagination_info = self.get_paginated_response(serializer.data).data
            data.update(pagination_info)
            for item in data["results"]:
                item["doc"] = f"sessions/report?pk="+str(item["id"])
            return Response(data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class SessionAdd(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    @swagger_auto_schema(
    operation_description='Add session',
    consumes=[ "multipart/form-data"],
    manual_parameters=[
        openapi.Parameter('date', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, default="30-03-2023", description='Дата сессии'),
        openapi.Parameter('time', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description=' 11:59:01'),
        openapi.Parameter('scenario', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description='Сценарий'),
        openapi.Parameter('result', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description='Результат'),  
        openapi.Parameter('video', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description='The uploaded video'),
    ],
    responses={
        200: openapi.Response(description='OK'),
        400: openapi.Response(description='Bad Request'),
        401: openapi.Response(description='Unauthorized'),
        500: openapi.Response(description='Internal Server Error')
    }
)
    def post(self,request):
        if request.user.position != 'student':
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            
        file = request.FILES["file"]
        file_name = get_random_string(24) + "." + file.name.split(".")[-1]
        data = request.data
        data["video"] = file_name
        del data["file"]
        data["FK_user"] = request.auth["id"]
        serializer_class = serializer.SessionAddSerializer(data=data, many=False)
        if serializer_class.is_valid(raise_exception=True):
            MinioClient.upload_data("/" + str(request.auth["id"]) + "/" + file_name, file, length=file.size)
            serializer_class.save()
            return Response()
        else: 
            return Response(serializer_class.error)
 
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@swagger_auto_schema(
    operation_description='Generate Document',
    manual_parameters=[
        openapi.Parameter('pk', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Document ID')
    ],
    responses={
        200: 'OK',
        400: 'Bad Request',
    }
)
def DocGenerate(request):
    
    # Get the query parameter 'pk' from the request
    pk = request.query_params.get('pk', None)
    if pk is None:
        return HttpResponseBadRequest("The 'pk' parameter is required.")
    file_path = f"./resources/test.pdf"
    try:
        file = open(file_path, "rb")
        return FileResponse(file, filename=f"{pk}.pdf")
    except FileNotFoundError:
        return HttpResponseBadRequest("File not found.")


class SessionVideoView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, pk):
        try:
            session = Session.objects.get(pk=pk, FK_user=request.auth["id"])
        except Session.DoesNotExist:
            return HttpResponseBadRequest("Session not found.")

        video_name = session.video

        if video_name:
            video_url = MinioClient.get_presigned_url(video_name)
            template = loader.get_template('video.html')
            context = {"video_url": video_url}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseBadRequest("Video not found.")
