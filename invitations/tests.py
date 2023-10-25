from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import CustomUser
from companies.models import Company
from invitations.models import CompanyInvitation, InvitationStatus

class InvitationsViewSetTest(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create(username="owner", password="owner_password")
        self.user1 = CustomUser.objects.create(username="user1", password="user1_password")
        self.user2 = CustomUser.objects.create(username="user2", password="user2_password")

        self.company = Company.objects.create(owner=self.owner, name="Company 1", description="Description 1")
        self.company.members.add(self.owner)

    def test_send_invitation(self):
        url = f'/company/{self.company.id}/send_invitation/'
        data = {'invited_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.INVITED).exists()
            )
    
    def test_accept_invitation(self):
        url = f'/company/{self.company.id}/send_invitation/'
        data = {'invited_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.INVITED).exists()
            )

        url = f'/users/{self.user1.id}/accept_invitation/'
        data = {'company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Company.objects.filter(members=self.user1).exists())

    def test_decline_invitation(self):
        url = f'/company/{self.company.id}/send_invitation/'
        data = {'invited_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.INVITED).exists()
            )

        url = f'/users/{self.user1.id}/decline_invitation/'
        data = {'company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Company.objects.filter(members=self.user1).exists())  

    def test_revoke_invitation(self):
        url = f'/company/{self.company.id}/send_invitation/'
        data = {'invited_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        
        url = f'/company/{self.company.id}/revoke_invitation/'
        data = {'invited_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.INVITED).exists()
            )

    def test_send_request(self):
        url = f'/users/{self.user1.id}/send_request/'
        data = {'req_company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.REQUESTED).exists()
            )

    def test_revoke_request(self):
        url = f'/users/{self.user1.id}/send_request/'
        data = {'req_company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.REQUESTED).exists()
            )

        url = f'/users/{self.user1.id}/revoke_request/'
        data = {'req_company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.REQUESTED).exists()
            )


    def test_accept_request(self):
        url = f'/users/{self.user1.id}/send_request/'
        data = {'req_company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.REQUESTED).exists()
            )

        url = f'/company/{self.company.id}/accept_request/'
        data = {'req_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Company.objects.filter(members=self.user1).exists())

    def test_reject_request(self):
        url = f'/users/{self.user1.id}/send_request/'
        data = {'req_company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.REQUESTED).exists()
            )

        url = f'/company/{self.company.id}/reject_request/'
        data = {'req_user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CompanyInvitation.objects.filter(
            invited_user=self.user1, 
            status=InvitationStatus.REQUESTED).exists()
            )

    def test_remove_user(self):
        self.company.members.add(self.user1)
        url = f'/company/{self.company.id}/remove_member/'
        data = {'user_id': self.user1.id}
        self.client.force_authenticate(self.owner)  
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Company.objects.filter(members=self.user1).exists())

    def test_leave_company(self):
        self.company.members.add(self.user1)
        url = f'/users/{self.user1.id}/leave_company/'
        data = {'company_id': self.company.id}
        self.client.force_authenticate(self.user1)  
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Company.objects.filter(members=self.user1).exists())
        
