from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from companies.models import Company
from companies.serializers import (
    AdministratorSerializer,
    AppointAdministratorSerializer,
    CompanySerializer,
    RemoveAdministratorSerializer,
)
from invitations.models import CompanyInvitation, InvitationStatus
from invitations.serializers import AcceptRequestSerializer, RemoveMemberSerializer, SendInvitationSerializer
from quizzes.models import Quiz, UserAnswer
from quizzes.serializers import QuizResultSerializer, QuizSerializer


class CompanyPagination(PageNumberPagination):
    page_size = 2

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.prefetch_related('owner').all()
    pagination_class = CompanyPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['delete'], name='Delete Company')
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

    @action(detail=True, methods=['post'])
    def toggle_visibility(self, request, pk=None):
        company = self.get_object()
        if company.owner == request.user:
            company.is_visible = not company.is_visible
            company.save()
            return Response({'message': 'Visibility toggled successfully.'})
        return Response({'error': 'You are not the owner of this company.'}, status=status.HTTP_403_FORBIDDEN)
   
    @action(detail=True, methods=['post'])
    def send_invitation(self, request, pk=None):
        serializer = SendInvitationSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()
            invited_user_id = serializer.validated_data['invited_user_id']
            invited_user = CustomUser.objects.get(pk=invited_user_id)
            
            invitation = CompanyInvitation(company=company, invited_user=invited_user, status=InvitationStatus.INVITED)
            invitation.save()
            
            return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'])
    def revoke_invitation(self, request, pk=None):
        serializer = SendInvitationSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()
            invited_user_id = serializer.validated_data['invited_user_id']
            
            try:
                invitation = CompanyInvitation.objects.prefetch_related('company', 'invited_user').get(
                    company=company, 
                    invited_user=invited_user_id, 
                    status=InvitationStatus.INVITED
                    )
                invitation.status = InvitationStatus.CANCELED
                invitation.save()
            
                return Response({'message': 'Invitation revoked successfully'}, status=status.HTTP_200_OK)
            except CompanyInvitation.DoesNotExist:
                return Response({'error': 'Invitation not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_invitations(self, request, pk=None):
        company = self.get_object()
        invitations = CompanyInvitation.objects.prefetch_related('company', 'invited_user').filter(
            company=company, 
            status=InvitationStatus.INVITED
            )
        serializer = SendInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
  
    @action(detail=True, methods=['post'])
    def accept_request(self, request, pk=None):
        serializer = AcceptRequestSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()
            req_user_id = serializer.validated_data['req_user_id']
            req_user = CustomUser.objects.get(pk=req_user_id)
            try:
                invitation = CompanyInvitation.objects.prefetch_related('company', 'invited_user').get(
                    company=company, 
                    invited_user=req_user_id, 
                    status=InvitationStatus.REQUESTED
                    )
                invitation.status = InvitationStatus.ACCEPTED
                invitation.save()

                company.members.add(req_user)
                return Response({'message': 'Request accepted successfully'}, status=status.HTTP_200_OK)
            except CompanyInvitation.DoesNotExist:
                return Response({'error': 'Request not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        serializer = AcceptRequestSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()
            req_user_id = serializer.validated_data['req_user_id']
            try:
                invitation = CompanyInvitation.objects.prefetch_related('company', 'invited_user').get(
                    company=company, 
                    invited_user=req_user_id, 
                    status=InvitationStatus.REQUESTED
                    )
                invitation.status = InvitationStatus.REJECTED
                invitation.save()

                return Response({'message': 'Request rejected successfully'}, status=status.HTTP_200_OK)
            except CompanyInvitation.DoesNotExist:
                return Response({'error': 'Request not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_requests(self, request, pk=None):
        company = self.get_object()
        invitations = CompanyInvitation.objects.prefetch_related('company', 'invited_user').filter(
            company=company, 
            status=InvitationStatus.REQUESTED
            )
        serializer = SendInvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        serializer = RemoveMemberSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()  # Retrieve the company
            user_id = serializer.validated_data['user_id']
            
            if company.members.filter(id=user_id).exists():
                company.members.remove(user_id)
                return Response({'message': 'Member removed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not a member of the company'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_members(self, request, pk=None):
        company = self.get_object()
        members = company.members.all()  
        serializer = UserSerializer(members, many=True)  
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def appoint_administrator(self, request, pk=None):
        serializer = AppointAdministratorSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()
            user_id = serializer.validated_data['user_id']
            try:
                user = CustomUser.objects.filter(pk=user_id).prefetch_related(
                    'companies', 
                    'administered_companies').first()
                if user in company.members.all() and user != company.owner:
                    company.administrators.add(user)
                    return Response({'message': 'Administrator appointed successfully'}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid user or action not allowed'}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'])
    def remove_administrator(self, request, pk=None):
        serializer = RemoveAdministratorSerializer(data=request.data)
        if serializer.is_valid():
            company = self.get_object()
            user_id = serializer.validated_data['user_id']

            try:
                user = CustomUser.objects.filter(pk=user_id).prefetch_related(
                    'companies', 
                    'administered_companies').first()
                if user in company.administrators.all():
                    company.administrators.remove(user)
                    return Response({'message': 'Administrator removed successfully'}, status=status.HTTP_200_OK)
                return Response({'error': 'User is not an administrator'}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_administrators(self, request, pk=None):
        company = self.get_object()
        administrators = company.administrators.all()
        serializer = AdministratorSerializer(administrators, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='list-quizzes')
    def list_quizzes(self, request, pk=None):
        company = self.get_object()
        quizzes = Quiz.objects.filter(company=company)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='average_score')
    def company_average_user_score(self, request, pk=None):
        company = self.get_object() 

        user_id = request.query_params.get('user_id', None)
        if user_id is None:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        company_with_results = Company.objects.prefetch_related(
            'members__quizresult_set',  
        ).get(id=company.id)

        user = company_with_results.members.get(id=user_id)
        quiz_results = user.quizresult_set.all()

        total_correct_answers = UserAnswer.objects.filter(
            quiz_attempt__user=user,
            question__quiz__company=company,
            chosen_answer__is_correct=True
        ).count()

        total_answers = UserAnswer.objects.filter(
            quiz_attempt__user=user,
            question__quiz__company=company
        ).count()

        average_score = total_correct_answers / total_answers if total_answers > 0 else 0

        quiz_results_serializer = QuizResultSerializer(quiz_results, many=True)

        response_data = {
            'company_id': company.id,
            'user_id': user_id,
            'average_score': average_score,
            'quiz_results': quiz_results_serializer.data,  
        }

        return Response(response_data, status=status.HTTP_200_OK)
