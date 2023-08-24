from rest_framework import serializers
from .models import Session



class SessionAddSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y.%m.%d")
    time = serializers.TimeField(format="%H:%M:%S")
    class Meta:
        model = Session
        fields = ("date", "time", "scenario", "result","FK_user", "video")

class SessionSerializer(serializers.ModelSerializer):
    
    # user_id = serializers.UUIDField(write_only=True)
    # uuid = serializers.UUIDField(read_only = True)

    class Meta:
        model = Session
       
        fields = ("id","date", "time", "scenario", "result")