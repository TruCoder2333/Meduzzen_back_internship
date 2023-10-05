from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from rest_framework.exceptions import NotFound
from log_app.models import Logger
from log_app.serializers import LoggerSerializer
from accounts.utils import log_to_logger

class UserPagination(PageNumberPagination):
    page_size = 1

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    
    pagination_class = UserPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except NotFound:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                log_message = f'New user created: {instance.username}'
                log_to_logger('INFO', log_message)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            log_message = f'Failed to create user. Error: {str(e)}'
            log_to_logger('ERROR', log_message)
            return Response({'error': 'Failed to create user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try: 
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                self.perform_update(serializer)
                log_message = f'User updated: {instance.username}'
                log_to_logger('INFO', log_message)
                return Response(serializer.data)
        except Exception as e:
            log_message = f'Failed to update user. Error: {str(e)}'
            log_to_logger('ERROR', log_message)
            return Response({'error': 'Failed to update user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




