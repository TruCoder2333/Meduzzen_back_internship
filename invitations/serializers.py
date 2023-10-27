from rest_framework import serializers

from .models import InvitationStatus


class SendInvitationSerializer(serializers.Serializer):
    invited_user_id = serializers.IntegerField()

class RespondToInvitationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(status.value, status.name) for status in InvitationStatus])

class AcceptInvitationSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()  

class SendRequestSerializer(serializers.Serializer):
    req_company_id = serializers.IntegerField()

class AcceptRequestSerializer(serializers.Serializer):
    req_user_id = serializers.IntegerField()  

class RemoveMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()  

class LeaveCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField()  