from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from accounts.models import CustomUser
from accounts.permissions import NoAuthenticationNeeded
from accounts.serializers import AvatarUploadSerializer, UserSerializer
from accounts.utils import log_to_logger
from companies.models import Company
from invitations.models import CompanyInvitation, InvitationStatus
from invitations.serializers import AcceptInvitationSerializer, LeaveCompanySerializer, SendRequestSerializer


class UserPagination(PageNumberPagination):
    page_size = 5

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
        return [permission() for permission in self.permission_classes_by_action.get(self.action, 
                                                                                     self.permission_classes)]

    def password_reset(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

        reset_email_subject = 'Reset Your Password'
        reset_email_body = f'Please follow this link to reset your password: {reset_url}'
        send_mail(reset_email_subject, reset_email_body, 'bondkyrylo@gmail.com', [email])

        return Response({'message': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)

    def password_reset_confirm(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        password = request.data.get('password')

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

    @action(detail=True, methods=['post'])
    def accept_invitation(self, request, pk=None):
        serializer = AcceptInvitationSerializer(data=request.data)
        if serializer.is_valid():
            invited_user = self.request.user 
            company_id = serializer.validated_data['company_id']
            
            try:
                invitation = CompanyInvitation.objects.prefetch_related('company', 'invited_user').get(
                    company=company_id, 
                    invited_user=invited_user, 
                    status=InvitationStatus.INVITED
                    )
                company = invitation.company
                invitation.status = InvitationStatus.ACCEPTED
                invitation.save()

                company.members.add(invited_user)
                return Response({'message': 'Invitation accepted successfully'}, status=status.HTTP_200_OK)
            except CompanyInvitation.DoesNotExist:
                return Response({'error': 'Invitation not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def decline_invitation(self, request, pk=None):
        serializer = AcceptInvitationSerializer(data=request.data)
        if serializer.is_valid():
            invited_user = self.request.user  
            company_id = serializer.validated_data['company_id']
            
            try:
                invitation = CompanyInvitation.objects.prefetch_related('company', 'invited_user').get(
                    company=company_id, 
                    invited_user=invited_user, 
                    status=InvitationStatus.INVITED
                    )
                    
                invitation.status = InvitationStatus.REJECTED
                invitation.save()
                return Response({'message': 'Invitation declined successfully'}, status=status.HTTP_200_OK)
            except CompanyInvitation.DoesNotExist:
                return Response({'error': 'Invitation not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def send_request(self, request, pk=None):
        serializer = SendRequestSerializer(data=request.data)
        if serializer.is_valid():
            invited_user = self.request.user  
            req_company_id = serializer.validated_data['req_company_id']
            req_company = Company.objects.get(pk=req_company_id)
            
            invitation = CompanyInvitation(
                company=req_company, 
                invited_user=invited_user, 
                status=InvitationStatus.REQUESTED
                )
            invitation.save()
            
            return Response({'message': 'Request sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def revoke_request(self, request, pk=None):
        serializer = SendRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            req_company_id = serializer.validated_data['req_company_id']
            req_company = Company.objects.get(pk=req_company_id)
            try:
                invitation = CompanyInvitation.objects.prefetch_related('company', 'invited_user').get(
                    company=req_company, 
                    invited_user=user, 
                    status=InvitationStatus.REQUESTED
                    )
                invitation.status = InvitationStatus.CANCELED
                invitation.save()
                return Response({'message': 'Invitation revoked successfully'}, status=status.HTTP_200_OK)
            except CompanyInvitation.DoesNotExist:
                return Response({'error': 'Invitation not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def leave_company(self, request, pk=None):
        serializer = LeaveCompanySerializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()  
            company_id = serializer.validated_data['company_id']
            company = Company.objects.prefetch_related('members').get(pk=company_id)
            if company.members.filter(id=user.id).exists():
                company.members.remove(user.id)
                return Response({'message': 'Member left successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not a member of the company'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_requests(self, request, pk=None):
        user = self.get_object()
        invitations = CompanyInvitation.objects.prefetch_related('company', 'invited_user').filter(
            invited_user=user, 
            status=CompanyInvitation.REQUESTED
            )
        serializer = AcceptInvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_invites(self, request, pk=None):
        user = self.get_object()
        invitations = CompanyInvitation.objects.prefetch_related('company', 'invited_user').filter(
            invited_user=user, 
            status=CompanyInvitation.INVITED
            )
        serializer = AcceptInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_avatar(self, request, pk=None):
        serializer = AvatarUploadSerializer(data=request.data)

        if serializer.is_valid():
            user = self.get_object()
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response({'message': 'Avatar uploaded successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    