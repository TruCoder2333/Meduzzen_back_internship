from rest_framework import serializers
from companies.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'owner', 'name', 'description']
        read_only_fields = ['owner']

class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name'] 