from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from companies.models import Company

class CompanyViewSetTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username = 'testuser')
        self.user.set_password('Test123')
        self.user.save()
        
        self.token, created = Token.objects.get_or_create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list(self):
        response = self.client.get('/company/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {
            'name': 'testCompany',
            'description': 'testDescr',
        }
        response = self.client.post('/company/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        company = Company.objects.create(name='Company 4', description='Desc 4', owner=self.user, is_visible=True)
        response = self.client.get(f'/company/{company.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)    

    def test_update(self):
        company = Company.objects.create(name='Company 5', description='Desc 5', owner=self.user, is_visible=True)
        data = {'name': 'testUpd',
                'description': 'descrUpd'}

        response = self.client.put(f'/company/{company.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        company = Company.objects.create(name='Company 6', description='Desc 6', owner=self.user, is_visible=True)
        response = self.client.delete(f'/company/{company.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        