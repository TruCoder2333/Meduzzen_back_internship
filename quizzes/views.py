from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Answer, Question, Quiz
from .permissions import IsCompanyOwnerOrAdministrator
from .serializers import AnswerSerializer, QuestionSerializer, QuizSerializer


class QuizPagination(PageNumberPagination):
    page_size = 1


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.prefetch_related('questions__answers').all()
    serializer_class = QuizSerializer
    permission_classes = [IsCompanyOwnerOrAdministrator]        
    pagination_class = QuizPagination

    def perform_create(self, serializer):
        quiz = serializer.save()

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
        
    @action(detail=True, methods=['post'], url_path='create-question')
    def create_question(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            question = serializer.save(quiz=quiz)
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='create-answer')
    def create_answer(self, request, pk=None):
        self.get_object()
        serializer = AnswerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


