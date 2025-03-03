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
        # カテゴリーによるフィルタリング（オプション）
        category_id = self.request.query_params.get('category')
        
        # ユーザーとそのクイズ結果を集計
        queryset = User.objects.annotate(
            total_attempts=Count('quiz_attempts', distinct=True),
            total_score=Sum('quiz_attempts__score'),
            total_questions=Sum('quiz_attempts__total_questions'),
            avg_percentage=Round(
                ExpressionWrapper(
                    Avg('quiz_attempts__percentage'), 
                    output_field=FloatField()
                ), 
                precision=1
            )
        ).filter(total_attempts__gt=0)
        
        # カテゴリーフィルターが指定されている場合
        if category_id:
            queryset = queryset.annotate(
                category_attempts=Count(
                    'quiz_attempts', 
                    filter=models.Q(quiz_attempts__category_id=category_id),
                    distinct=True
                ),
                category_score=Sum(
                    'quiz_attempts__score',
                    filter=models.Q(quiz_attempts__category_id=category_id)
                ),
                category_questions=Sum(
                    'quiz_attempts__total_questions',
                    filter=models.Q(quiz_attempts__category_id=category_id)
                ),
                category_percentage=Round(
                    ExpressionWrapper(
                        Avg(
                            'quiz_attempts__percentage',
                            filter=models.Q(quiz_attempts__category_id=category_id)
                        ), 
                        output_field=FloatField()
                    ), 
                    precision=1
                )
            ).filter(category_attempts__gt=0)
            
            # カテゴリー内の成績でソート
            return queryset.order_by('-category_percentage', '-category_score')
        
        # 全体の成績でソート
        return queryset.order_by('-avg_percentage', '-total_score')
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