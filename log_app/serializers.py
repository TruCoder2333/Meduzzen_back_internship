from rest_framework import serializers
from .models import Logger

class LoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logger
        fields = '__all__'