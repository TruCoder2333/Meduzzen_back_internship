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
from accounts.permissions import NoAuthenticationNeeded
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator

class UserPagination(PageNumberPagination):
    page_size = 1

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    pagination_class = UserPagination

    permission_classes_by_action = {
        'create': [NoAuthenticationNeeded],  
        }

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
                instance = CustomUser.objects.create_user(**serializer.validated_data)
                log_message = f'New user created: {instance.username}'
                log_to_logger('INFO', log_message)
                return Response(UserSerializer(instance).data, status=status.HTTP_201_CREATED)
            return Response({'error': f'Failed {serializer.errors}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

    def get_permissions(self):
        return [permission() for permission in self.permission_classes_by_action.get(self.action, self.permission_classes)]

    def password_reset(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        #Does email exist?
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        #Generating reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        #Building the reset URL
        reset_url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

        #Sending reset email
        reset_email_subject = 'Reset Your Password'
        reset_email_body = f'Please follow this link to reset your password: {reset_url}'
        send_mail(reset_email_subject, reset_email_body, 'from@example.com', [email])

        return Response({'message': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)

    def password_reset_confirm(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        password = request.data.get('password')

        # Decode uid and get the user
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the reset token is valid
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid reset token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(password)
        user.save()

        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)