from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from companies.models import Company

from .models import Quiz, QuizResult
from .utils import get_current_quiz_attempt


class QuizAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="user", password="password")
        self.company = Company.objects.create(
            name='Test Quiz Company', 
            description='TestDesc', 
            owner=self.user, 
            is_visible=True)
        self.company.members.add(self.user)

        self.quiz = Quiz.objects.create(title='Test Quiz', 
            description='Quiz description', 
            company=self.company, 
            frequency_in_days=1)
        
        self.quiz2 = Quiz.objects.create(title='Test Quiz 2', 
            description='Quiz description', 
            company=self.company, 
            frequency_in_days=1)
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

    def test_start_attempt(self):
        url = f'/quizzes/{self.quiz.id}/start_attempt/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submit_answers(self):
        url = f'/quizzes/{self.quiz.id}/create_question/'  
        data = {
            "text": "Test Question",
            "quiz": self.quiz.id,
        }
        self.client.post(url, data, format='json')
        question = self.quiz.questions.first()

        url = f'/quizzes/{self.quiz.id}/create_answer/'  
        data = {
            "text": "Correct answer",
            "is_correct": True,
            "question": question.id,
        }
        self.client.post(url, data, format='json')

        data = {
            "text": "Incorrect answer",
            "is_correct": False,
            "question": question.id,
        }
        self.client.post(url, data, format='json')
        answer = question.answers.first()

        url = f'/quizzes/{self.quiz.id}/submit_answers/'
        data = [
                {
                    "question": question.id,
                    "chosen_answer": answer.id,
                    "quiz_attempt": get_current_quiz_attempt(self.user, self.quiz).id
            }
        ]

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_score_by_company(self):
        QuizResult.objects.create(
            quiz=self.quiz, 
            user=self.user, 
            score=0,
            company=self.company,
            )

        #First question
        url = f'/quizzes/{self.quiz.id}/create_question/'  
        data = {
            "text": "Test Question 1",
            "quiz": self.quiz.id,
        }
        self.client.post(url, data, format='json')
        question1 = self.quiz.questions.first()
        url = f'/quizzes/{self.quiz.id}/create_answer/'  
        data = {
            "text": "Correct answer",
            "is_correct": True,
            "question": question1.id,
        }
        self.client.post(url, data, format='json')

        data = {
            "text": "Incorrect answer",
            "is_correct": False,
            "question": question1.id,
        }
        self.client.post(url, data, format='json')
        answer1 = question1.answers.first()

        #Second question
        url = f'/quizzes/{self.quiz.id}/create_question/'  
        data = {
            "text": "Test Question 2",
            "quiz": self.quiz.id,
        }
        self.client.post(url, data, format='json')
        question2 = self.quiz.questions.last()
        url = f'/quizzes/{self.quiz.id}/create_answer/'  
        data = {
            "text": "Correct answer",
            "is_correct": True,
            "question": question2.id,
        }
        self.client.post(url, data, format='json')

        data = {
            "text": "Incorrect answer",
            "is_correct": False,
            "question": question2.id,
        }
        self.client.post(url, data, format='json')
        answer2 = question2.answers.last()


        url = f'/quizzes/{self.quiz.id}/submit_answers/'
        data = [
                {
                    "question": question1.id,
                    "chosen_answer": answer1.id,
                    "quiz_attempt": get_current_quiz_attempt(self.user, self.quiz).id
                },
                {
                    "question": question2.id,
                    "chosen_answer": answer2.id,
                    "quiz_attempt": get_current_quiz_attempt(self.user, self.quiz).id
                }
        ]

        response = self.client.post(url, data, format='json')
        url = f'/company/{self.company.id}/average_score/?user_id={self.user.id}'

        response = self.client.get(url)
        #We have 2 questions in one quiz, if we count average by quiz the result should be 1, if by questions then 0.5
        self.assertEqual(response.data["average_score"], 0.5)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_score_overall(self):
        QuizResult.objects.create(
            quiz=self.quiz, 
            user=self.user, 
            score=0,
            company=self.company,
            )

        url = f'/quizzes/{self.quiz.id}/create_question/'  
        data = {
            "text": "Test Question 1",
            "quiz": self.quiz.id,
        }
        self.client.post(url, data, format='json')
        question1 = self.quiz.questions.first()
        url = f'/quizzes/{self.quiz.id}/create_answer/'  
        data = {
            "text": "Correct answer",
            "is_correct": True,
            "question": question1.id,
        }
        self.client.post(url, data, format='json')

        data = {
            "text": "Incorrect answer",
            "is_correct": False,
            "question": question1.id,
        }
        self.client.post(url, data, format='json')
        answer1 = question1.answers.first()

        url = f'/quizzes/{self.quiz.id}/submit_answers/'
        data = [
                {
                    "question": question1.id,
                    "chosen_answer": answer1.id,
                    "quiz_attempt": get_current_quiz_attempt(self.user, self.quiz).id
                },
        ]

        response = self.client.post(url, data, format='json')

        url = f'/users/{self.user.id}/average-score-all-companies/'

        response = self.client.get(url)

        self.assertEqual(response.data["average_score_all_companies"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)