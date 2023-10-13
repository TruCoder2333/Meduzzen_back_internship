from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class CustomUserViewSetTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username = 'testuser')
        self.user.set_password('Test123')
        self.user.save()
        
        self.token, created = Token.objects.get_or_create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        response = self.client.get(f'/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)    

    def test_create(self):
        data = {
            'username': 'abobus',
            'password': 'abobus22',
        }
        response = self.client.post('/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

    def test_update(self):
        data = {'username': 'Boris'}

        response = self.client.put(f'/users/{self.user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        response = self.client.delete(f'/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        