from rest_framework import serializers
from .models import Session
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from django.conf import settings


class SessionAddSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(write_only=True)
    # uuid = serializers.UUIDField(read_only = True)
    date = serializers.DateTimeField(format="%Y.%m.%d %H:%M:%S")
    duration = serializers.DurationField()
    class Meta:
        model = Session
        fields = ("date", "time", "scenario", "result","FK_user")
    
class SessionSerializer(serializers.ModelSerializer):
    
    # user_id = serializers.UUIDField(write_only=True)
    # uuid = serializers.UUIDField(read_only = True)

    class Meta:
        model = Session
       
        fields = ("id","date", "time", "scenario")