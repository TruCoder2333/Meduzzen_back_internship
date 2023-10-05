from rest_framework import serializers
from accounts.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'created_at', 'updated_at', 'email', 'first_name', 'last_name')