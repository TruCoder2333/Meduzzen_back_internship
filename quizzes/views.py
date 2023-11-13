import csv
import json

from django.db.models import Case, Count, FloatField, Prefetch, Sum, Value, When
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import CustomUser

from .models import Answer, Question, Quiz, QuizResult
from .serializers import (
    AnswerSerializer,
    QuestionSerializer,
    QuizAttemptSerializer,
    QuizResultSerializer,
    QuizSerializer,
    UserAnswerSerializer,
)
from .utils import save_user_answer_to_redis


class QuizPagination(PageNumberPagination):
    page_size = 1


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.prefetch_related('questions__answers').all()
    serializer_class = QuizSerializer
    #permission_classes = [IsCompanyOwnerOrAdministrator]        
    pagination_class = QuizPagination

    def perform_create(self, serializer):
        if serializer.is_valid:
            quiz = serializer.save()
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        questions_data = self.request.data.get('questions', [])
        questions = []

        for question_data in questions_data:
            question = Question(quiz=quiz, text=question_data['text'])
            question.save()
            questions.append(question)

            answers_data = question_data.get('answers', [])
            answers = [Answer(
                question=question, 
                text=answer_data['text'], 
                is_correct=answer_data['is_correct']) 
                for answer_data in answers_data]
            Answer.objects.bulk_create(answers)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def update(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        quiz = self.get_object()
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)  

        if page is not None:
            serializer = QuizSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = QuizSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def retrieve(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def create_question(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            question = serializer.save(quiz=quiz)
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def create_answer(self, request, pk=None):
        self.get_object()
        serializer = AnswerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_attempt(self, request, pk=None):
        quiz = self.get_object()

        serializer = QuizAttemptSerializer(data={'user': request.user.id, 'quiz': quiz.id})
        if serializer.is_valid():
            quiz_attempt = serializer.save()

            return Response({'quiz_attempt_id': quiz_attempt.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        quiz = self.get_object()

        serializer = UserAnswerSerializer(data=request.data, many=True)
        if serializer.is_valid():
            user_answers = serializer.save()
            total_score = 0

            for user_answer in user_answers:
                question = user_answer.question
                chosen_answer = user_answer.chosen_answer
                correct_answers = question.answers.filter(is_correct=True).prefetch_related(None)
                if correct_answers.filter(id=chosen_answer.id).exists():
                    total_score += 1

                    save_user_answer_to_redis(
                        user_id=request.user.id,
                        quiz_id=quiz.id,
                        question_id=question.id,
                        answer=chosen_answer.id,
                        is_correct=True,  
                        company_id= quiz.company.id,
                    )
                else:
                    save_user_answer_to_redis(
                        user_id=request.user.id,
                        quiz_id=quiz.id,
                        question_id=question.id,
                        answer=chosen_answer.id,
                        is_correct=False,  
                        company_id= quiz.company.id,
                    )
            quiz_result = QuizResult(
                quiz=quiz, 
                user=request.user, 
                score=total_score, 
                quiz_attempt=user_answer.quiz_attempt
                )
            quiz_result.save()
            return Response({'message': 'Answers submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'], url_path='user-score')
    def get_user_score(self, request, pk=None):
        quiz = self.get_object()
        quiz_results_prefetch = Prefetch(
            'quizresult_set',
            queryset=QuizResult.objects.filter(user=request.user),
            to_attr='user_quiz_results'
        )

        quiz_with_user_results = Quiz.objects.filter(id=quiz.id).prefetch_related(quiz_results_prefetch).get()

        try:
            quiz_result = quiz_with_user_results.user_quiz_results[0]
            quiz_result_data = QuizResultSerializer(quiz_result).data
            quiz_data = QuizSerializer(quiz).data

            response_data = {
                'quiz_title': quiz_data['title'],  
                'user_score': quiz_result_data['score'],
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except QuizResult.DoesNotExist:
            return Response({'Not found': quiz_result.title, 'user_score': None}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def list_quiz_results(self, request, pk=None):
        quiz = self.get_object()
        quiz_results = QuizResult.objects.prefetch_related('quiz').filter(quiz=quiz)
        serializer = QuizResultSerializer(quiz_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['get'], url_path='export/csv', url_name='export-csv')
    def export_results_to_csv(self, request):
        quiz_results = QuizResult.objects.filter(user=request.user).prefetch_related(
            Prefetch('user', queryset=CustomUser.objects.only('id', 'username')),
            Prefetch('quiz', queryset=Quiz.objects.only('id', 'title')),
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="quiz_results.csv"'

        writer = csv.writer(response)
        writer.writerow(["Id", "User", "Quiz", "Score", "Company", "Date Passed"])

        for result in quiz_results:
            writer.writerow([
                result.id,
                result.user.username, 
                result.quiz.title, 
                result.score, 
                result.company, 
                result.timestamp
                ])

        return response

    @action(detail=False, methods=['get'], url_path='export/json', url_name='export-json')
    def export_results_to_json(self, request):
        quiz_results = QuizResult.objects.filter(user=request.user).prefetch_related(
            Prefetch('user', queryset=CustomUser.objects.only('id', 'username')),
            Prefetch('quiz', queryset=Quiz.objects.only('id', 'title')),
            )

        data = [
            {
                "user": result.user.username,
                "company": result.company,
                "quiz": result.quiz.title,
                "score": result.score,
                "date_passed": result.timestamp
            }
            for result in quiz_results
        ]

        return HttpResponse(json.dumps(data), content_type="application/json")


    @action(detail=True, methods=['get'], url_path='average-scores-over-time')
    def get_average_scores_over_time(self, request, pk=None):
        quiz = self.get_object()
        user = request.user

        quiz_results = (
            QuizResult.objects
            .filter(quiz=quiz, user=user)
            .annotate(
                date=TruncDate('timestamp')
            )
            .values('date')
            .annotate(
                total_correct_answers=Sum(
                    Case(
                        When(
                            quiz_attempt__useranswer__chosen_answer__in=Answer.objects.filter(is_correct=True),
                            then=Value(1.0),
                        ),
                        default=Value(0.0),
                        output_field=FloatField()
                    )
                    ),
                total_answers=Count(
                    'quiz_attempt__useranswer'
                ),
            )
            .order_by('date')
        )
        results_data = []
        cumulative_total_correct = 0
        cumulative_total_answers = 0

        for result in quiz_results:
            cumulative_total_correct += result['total_correct_answers']
            cumulative_total_answers += result['total_answers']
            average_score = cumulative_total_correct / cumulative_total_answers if cumulative_total_answers > 0 else 0

            results_data.append({
                'date': result['date'],
                'average_score': average_score,
            })

       

        return Response(results_data)
    

   