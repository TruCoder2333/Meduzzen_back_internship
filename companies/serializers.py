from rest_framework import serializers

from companies.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'owner', 'name', 'description', 'members', 'administrators']
        read_only_fields = ['owner']

    def send_invitations(self, user_id):
        self.instance.members.add(user_id)

class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name'] 

class AdministratorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()

class AppointAdministratorSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class RemoveAdministratorSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

