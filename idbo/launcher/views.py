from rest_framework import generics, exceptions, request, status
from rest_framework.permissions import IsAuthenticated
from .models import Session
import io
from django.http import FileResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializer
from django.template import loader
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from services.s3 import MinioClient
from rest_framework import parsers
from utils import get_random_string
from PyPDFForm import PyPDFForm

class SessionPagination(PageNumberPagination):
    page_size = 20


class SessionList(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = serializer.SessionSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = SessionPagination
    authentication_classes = (JWTAuthentication,)
    
    def list(self, request):
       
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(FK_user=request.auth["id"])
        date_filter = request.query_params.get('date')
        scenario_filter = request.query_params.get('scenario')
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        if scenario_filter:
            queryset = queryset.filter(scenario=scenario_filter)
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
    # permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    @swagger_auto_schema(
    operation_description='Add session',
    consumes=[ "multipart/form-data"],
    manual_parameters=[
        openapi.Parameter('date', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, default="2023-03-30", description='Дата сессии'),
        openapi.Parameter('time', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, default="11:59:01", description='Время'),
        openapi.Parameter('scenario', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description='Сценарий'),
        openapi.Parameter('result', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description='Результат'),  
        openapi.Parameter('video', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description='Видео'),
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
            MinioClient.upload_data("public/"+str(request.auth["id"]) + "/" + file_name, file, length=file.size)
            serializer_class.save()
            return Response()
        else: 
            return Response(serializer_class.error)
 
@api_view(["GET"])
@permission_classes([IsAuthenticated,])
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
    file_path = f"./resources/template.pdf"
    try:
        session = Session.objects.get(id = pk)
    except:
        return HttpResponseBadRequest("File not found.")
    pdf_form = PyPDFForm(file_path)
    
    pdf_form.elements["id"].font = "Montserrat-SemiBold"
    pdf_form.elements["id"].font_size = 5
    
    pdf_form.elements["full_name"].font = "Montserrat-SemiBold"
    pdf_form.elements["full_name"].font_size = 10
    
    pdf_form.elements["scenario"].font = "Montserrat-Regular"
    pdf_form.elements["scenario"].font_size = 5
    
    pdf_form.elements["hour"].font = "Montserrat-SemiBold"
    pdf_form.elements["hour"].font_size = 5
    
    pdf_form.elements["minute"].font = "Montserrat-SemiBold"
    pdf_form.elements["minute"].font_size = 5
    
    pdf_form.elements["score"].font = "Montserrat-SemiBold"
    pdf_form.elements["score"].font_size = 5
    
    pdf_form.elements["rez_word"].font = "Montserrat-SemiBold"
    pdf_form.elements["rez_word"].font_size = 5
    
    pdf_form.elements["date"].font = "Montserrat-SemiBold"
    pdf_form.elements["date"].font_size = 5
    id = "0"*(6 - len(str(session.FK_user_id))) + str(session.FK_user_id)
    date = session.date.strftime('%d.%m.%Y')
    pdf_form.fill({
        "id": id,
        "full_name": f"{session.FK_user.last_name} {session.FK_user.first_name} {session.FK_user.middle_name}",
        "scenario": session.scenario,
        "hour": session.time.strftime('%H'),
        "minute": session.time.strftime('%M'),
        "score": str(session.result),
        "rez_word": "" if session.result > 65 else "не",
        "date":date,
        
    })

    return FileResponse(io.BytesIO(pdf_form.stream), filename=f"sertificat_{session.FK_user.id}_{date}.pdf")


class SessionVideoView(APIView):
    permission_classes = (IsAuthenticated,)
    


    def get(self, request, pk):
        try:
            session = Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            return HttpResponseBadRequest("Session not found.")

        if session.video:
            video_url = MinioClient.get_presigned_url(f"public/{session.FK_user_id}/{session.video}")
            template = loader.get_template('video.html')
            context = {"video_url": video_url}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseBadRequest("Video not found.")
        
class UniqueScenariosSessionList(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication,)

    @swagger_auto_schema(
        operation_description='Get unique scenarios for student sessions',
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Student user ID'),
        ],
        responses={
            200: 'OK',
            401: 'Unauthorized',
            500: 'Internal Server Error'
        }
    )
    def get(self, request):
        
        try:
            unique_scenarios = Session.objects.filter(FK_user__pk=request.auth["id"]).values_list('scenario', flat=True).distinct()
        except: 
            pass
        return Response(data=unique_scenarios)
