from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Answer, Question, Quiz, QuizAttempt, QuizResult
from .serializers import (
    AnswerSerializer,
    QuestionSerializer,
    QuizAttemptSerializer,
    QuizResultSerializer,
    QuizSerializer,
    UserAnswerSerializer,
)


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
            user_answers = serializer.save(quiz_attempt=self.get_current_quiz_attempt(request, quiz))
            total_score = 0

            for user_answer in user_answers:
                question = user_answer.question
                chosen_answer = user_answer.chosen_answer
                try:
                    correct_answer = Answer.objects.get(question=question, is_correct=True)
                except Answer.DoesNotExist:
                    return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

                if chosen_answer == correct_answer:
                    total_score += 1  

            #quiz_result_data = {
            #    'quiz': quiz.id,
            #    'user': request.user.id,
            #    'score': total_score,
            #}

            #quiz_result_serializer = QuizResultSerializer(data=quiz_result_data)

            quiz_result = QuizResult(quiz=quiz, user=request.user, score=total_score)
            quiz_result.save()
            #if quiz_result_serializer.is_valid():
            #    quiz_result_serializer.save()
            #   return Response({'message': 'Answers submitted successfully'}, status=status.HTTP_201_CREATED)
            #else:
            #     return Response(quiz_result_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_current_quiz_attempt(self, request, quiz):
        user = request.user  
        try:
            current_attempt = QuizAttempt.objects.get(user=user, quiz=quiz)
            return current_attempt
        except QuizAttempt.DoesNotExist:
            new_attempt = QuizAttempt(user=user, quiz=quiz)
            new_attempt.save()
            return new_attempt

    @action(detail=True, methods=['get'], url_path='user-score')
    def get_user_score(self, request, pk=None):
        quiz = self.get_object()

        try:
            quiz_result = QuizResult.objects.get(quiz=quiz, user=request.user)

            # Serialize the quiz_result using QuizResultSerializer
            quiz_result_data = QuizResultSerializer(quiz_result).data

            # Serialize the quiz object using QuizSerializer
            quiz_data = QuizSerializer(quiz).data

            response_data = {
                'quiz_title': quiz_data['title'],  # Assuming 'title' is the field to retrieve from the quiz
                'user_score': quiz_result_data['score'],
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except QuizResult.DoesNotExist:
            return Response({'Not found': quiz_result.title, 'user_score': None}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def list_quiz_results(self, request, pk=None):
        quiz = self.get_object()
        quiz_results = QuizResult.objects.filter(quiz=quiz)
        serializer = QuizResultSerializer(quiz_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
