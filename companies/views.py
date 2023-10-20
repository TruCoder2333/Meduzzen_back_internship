from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from companies.models import Company
from companies.serializers import CompanySerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

class CompanyPagination(PageNumberPagination):
    page_size = 2

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.prefetch_related('owner').all()
    permission_classes = [IsAuthenticated]
    pagination_class = CompanyPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def delete_company(self, request, pk=None):
        try:
            company = self.get_object()
            if request.user == company.owner:
                company.delete()
                return Response({'message': 'Company deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'You do not have permission to delete this company.'}, 
                status=status.HTTP_403_FORBIDDEN)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset.filter(is_visible=True))

            if page:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanySerializer
        return self.serializer_class

    def toggle_visibility(self, request, pk=None):
        company = self.get_object()
        if company.owner == request.user:
            company.is_visible = not company.is_visible
            company.save()
            return Response({'message': 'Visibility toggled successfully.'})
        return Response({'error': 'You are not the owner of this company.'}, status=status.HTTP_403_FORBIDDEN)