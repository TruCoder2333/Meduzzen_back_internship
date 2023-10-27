from rest_framework import serializers

from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'avatar', 'password', 'created_at', 'updated_at', 'email',  'additional_info')

class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()