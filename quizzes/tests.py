from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from companies.models import Company

from .models import Quiz


class QuizAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="user", password="password")
        self.company = Company.objects.create(
            name='Test Quiz Company', 
            description='TestDesc', 
            owner=self.user, 
            is_visible=True)
        self.client.force_authenticate(self.user)
        
    def test_create_quiz(self):
        url = '/quizzes/'  
        data = {
            "title": "Sample Quiz",
            "description": "A test quiz.",
            "frequency_in_days": 7,
            "company": self.company.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        quiz = Quiz.objects.filter(title="Sample Quiz").prefetch_related('questions__answers').first()
        self.assertEqual(quiz.description, "A test quiz.")

    def test_edit_quiz(self):
        url = '/quizzes/'  
        data = {
            "title": "Sample Quiz",
            "description": "A test quiz.",
            "frequency_in_days": 7,
            "company": self.company.id,
        }
        response = self.client.post(url, data, format='json')
        quiz = Quiz.objects.filter(title="Sample Quiz").prefetch_related('questions__answers').first()


        url = f'/quizzes/{quiz.id}/'  
        data = {
            "title": "Updated Quiz",
            "description": "An updated quiz.",
            "frequency_in_days": 14,
            "company": self.company.id,
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        quiz.refresh_from_db()
        self.assertEqual(quiz.title, "Updated Quiz")
        self.assertEqual(quiz.frequency_in_days, 14)

    def test_delete_quiz(self):
        url = '/quizzes/'  
        data = {
            "title": "Sample Quiz",
            "description": "A test quiz.",
            "frequency_in_days": 7,
            "company": self.company.id,
        }
        response = self.client.post(url, data, format='json')
        quiz = Quiz.objects.filter(title="Sample Quiz").prefetch_related('questions__answers').first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = f'/quizzes/{quiz.id}/'  
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_question(self):
        url = '/quizzes/'  
        data = {
            "title": "Sample Quiz",
            "description": "A test quiz.",
            "frequency_in_days": 7,
            "company": self.company.id,
        }
        response = self.client.post(url, data, format='json')
        quiz = Quiz.objects.filter(title="Sample Quiz").prefetch_related('questions__answers').first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = f'/quizzes/{quiz.id}/create_question/'  
        data = {
            "text": "Test Question",
            "quiz": quiz.id,
        }
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(quiz.questions.first().text, "Test Question")

    def test_create_answer(self):
        url = '/quizzes/'  
        data = {
            "title": "Sample Quiz",
            "description": "A test quiz.",
            "frequency_in_days": 7,
            "company": self.company.id,
        }
        response = self.client.post(url, data, format='json')
        quiz = Quiz.objects.filter(title="Sample Quiz").prefetch_related('questions__answers').first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = f'/quizzes/{quiz.id}/create_question/'  
        data = {
            "text": "Test Question",
            "quiz": quiz.id,
        }
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        question = quiz.questions.first()
        self.assertEqual(question.text, "Test Question")

        url = f'/quizzes/{quiz.id}/create_answer/'  
        data = {
            "text": "Test Answer",
            "is_correct": True,
            "question": question.id,
        }
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(quiz.questions.first().answers.first().text, "Test Answer")

