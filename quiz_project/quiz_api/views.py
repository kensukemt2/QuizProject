# quiz_api/views.py
from rest_framework import viewsets, permissions, generics
from .models import Category, Question, Choice, QuizAttempt
from .serializers import CategorySerializer, QuestionSerializer, ChoiceSerializer, RegisterSerializer, UserSerializer, SaveQuizResultSerializer, QuizAttemptSerializer, UserLeaderboardSerializer, UserStatsSerializer
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, FloatField, Q, Case, When, Value

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')  # 名前でソート
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
class LeaderboardView(generics.ListAPIView):
    """全ユーザーの成績を集計したリーダーボードを提供するAPI"""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserLeaderboardSerializer
    
    def get_queryset(self):
        category = self.request.query_params.get('category')
        
        # 基本的なクエリ - 単純化
        queryset = User.objects.annotate(
            total_attempts=Count('quiz_attempts'),
            total_score=Sum('quiz_attempts__score', default=0),
            total_questions=Sum('quiz_attempts__total_questions', default=0),
            avg_percentage=Case(
                When(total_questions__gt=0, 
                    then=ExpressionWrapper(
                        F('total_score') * 100.0 / F('total_questions'), 
                        output_field=FloatField()
                    )
                ),
                default=Value(0.0),
                output_field=FloatField()
            )
        )
        
        # カテゴリフィルターはシンプルに保持
        if category and category != 'all' and category.isdigit():
            queryset = queryset.filter(quiz_attempts__category_id=category)
            
        # 少なくとも1つの試行があるユーザーのみ表示
        queryset = queryset.filter(total_attempts__gt=0).distinct()
        
        # 平均パーセンテージでソート（降順）
        return queryset.order_by('-avg_percentage')

#ユーザープロフィールとパフォーマンス統計
class UserStatsView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserStatsSerializer
    
    def get_object(self):
        user = self.request.user
        
        # シンプルな統計計算
        attempts = QuizAttempt.objects.filter(user=user)
        categories_played = attempts.values('category').distinct().count()
        
        # ベストカテゴリーを取得（平均パーセンテージが最も高いもの）
        best_category = None
        if attempts.exists():
            category_avg = attempts.values('category__name').annotate(
                avg=Avg('percentage')
            ).order_by('-avg')
            if category_avg:
                best_category = category_avg[0]['category__name']
        
        # 全体統計
        overall_stats = {
            'total_attempts': attempts.count(),
            'total_categories_played': categories_played,
            'best_category': best_category,
            'avg_percentage': attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
        }
        
        return overall_stats