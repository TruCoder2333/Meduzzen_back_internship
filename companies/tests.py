from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from companies.models import Company


class CompanyViewSetTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username = 'testuser', password="user_password")
        self.user1 = CustomUser.objects.create(username="user1", password="user1_password")
        self.user2 = CustomUser.objects.create(username="user2", password="user2_password")
        
        
        self.token, created = Token.objects.get_or_create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list(self):
        Company.objects.create(name='Company 1', description='Desc 1', owner=self.user, is_visible=True)
        Company.objects.create(name='Company 2', description='Desc 2', owner=self.user, is_visible=False)

        response = self.client.get('/company/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

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
        updated_data = {'name': 'testUpd',
                'description': 'descrUpd'}

        response = self.client.put(f'/company/{company.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])
        self.assertEqual(response.data['description'], updated_data['description'])

    def test_delete(self):
        company = Company.objects.create(name='Company 6', description='Desc 6', owner=self.user, is_visible=True)
        response = self.client.delete(f'/company/{company.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_appoint_administrator(self):
        company = Company.objects.create(name='Company 1', description='Desc 1', owner=self.user, is_visible=True)
        company.members.add(self.user1)
        url = f'/company/{company.id}/appoint_administrator/'
        data = {'user_id': self.user1.id}
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(company.administrators.filter(id=self.user1.id).exists())

    def test_remove_administrator(self):
        company = Company.objects.create(name='Company 1', description='Desc 1', owner=self.user, is_visible=True)
        company.members.add(self.user1)
        url = f'/company/{company.id}/appoint_administrator/'
        data = {'user_id': self.user1.id}
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')

        url = f'/company/{company.id}/remove_administrator/'
        data = {'user_id': self.user1.id}
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(company.administrators.filter(id=self.user1.id).exists())
        

        