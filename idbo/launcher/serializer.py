from rest_framework import serializers
from .models import Session, Game, GameImage



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

class GameImageSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = GameImage
        fields = ("img",  )
        
class GameSerializer(serializers.ModelSerializer):
    
    # user_id = serializers.UUIDField(write_only=True)
    # uuid = serializers.UUIDField(read_only = True)
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
       
        fields = ("id","name", "exe_name", "images", "version", "file", "description","use_tcp")
    
    def get_images(self, obj):
        return [image.img.url for image in obj.images.all()]
