# quiz_api/views.py
from rest_framework import viewsets, permissions, generics
from .models import Category, Question, Choice, QuizAttempt
from .serializers import CategorySerializer, QuestionSerializer, ChoiceSerializer, RegisterSerializer, UserSerializer, SaveQuizResultSerializer, QuizAttemptSerializer, UserLeaderboardSerializer, UserStatsSerializer
from django.contrib.auth.models import User


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        queryset = Question.objects.all()
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__id=category)
        return queryset

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
# 過去のクイズ結果の保存
class SaveQuizResultView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SaveQuizResultSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class QuizHistoryView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuizAttemptSerializer
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

class QuizAttemptDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuizAttemptSerializer
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)
# リーダーボード
from django.db import models
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, FloatField, Q
from django.db.models.functions import Round


class LeaderboardView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserLeaderboardSerializer
    
    def get_queryset(self):
        # クエリパラメータからカテゴリを取得
        category = self.request.query_params.get('category')
        
        # ベースクエリ - ユーザーごとの結果集計
        queryset = User.objects.annotate(
            total_attempts=Count('quizattempt'),
            avg_score=Avg('quizattempt__percentage'),
            total_score=Sum('quizattempt__score')
        ).order_by('-avg_score')  # 平均スコアで降順ソート
        
        # カテゴリフィルター（'all'でない場合）
        if category and category != 'all' and category.isdigit():
            queryset = queryset.filter(quizattempt__category_id=category)
        
        return queryset
#ユーザープロフィールとパフォーマンス統計
# quiz_api/views.py に追加
class UserStatsView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserStatsSerializer
    
    def get_object(self):
        user = self.request.user
        
        # カテゴリーごとの統計を計算
        category_stats = []
        categories = Category.objects.all()
        
        for category in categories:
            attempts = QuizAttempt.objects.filter(
                user=user,
                category=category
            )
            
            if attempts.exists():
                category_stats.append({
                    'id': category.id,
                    'name': category.name,
                    'attempts_count': attempts.count(),
                    'best_score': attempts.order_by('-score').first().score if attempts.exists() else 0,
                    'avg_score': attempts.aggregate(avg=Avg('score'))['avg'],
                    'avg_percentage': attempts.aggregate(avg=Avg('percentage'))['avg']
                })
        
        # ユーザーの全体統計
        overall_stats = {
            'total_attempts': QuizAttempt.objects.filter(user=user).count(),
            'total_categories_played': len(category_stats),
            'best_category': max(category_stats, key=lambda x: x['avg_percentage'])['name'] if category_stats else None,
            'avg_percentage': QuizAttempt.objects.filter(user=user).aggregate(avg=Avg('percentage'))['avg'] or 0,
            'category_stats': category_stats
        }
        
        return overall_stats