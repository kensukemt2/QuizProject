# quiz_api/views.py
from rest_framework import viewsets, permissions, generics
from .models import Category, Question, Choice, QuizAttempt
from .serializers import CategorySerializer, QuestionSerializer, ChoiceSerializer, RegisterSerializer, UserSerializer, SaveQuizResultSerializer, QuizAttemptSerializer, UserLeaderboardSerializer, UserStatsSerializer, PublicLeaderboardSerializer
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum, Max, F, ExpressionWrapper, FloatField, Q, Case, When, Value
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

User = get_user_model()

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
        
        try:
            # シンプルな統計計算
            attempts = QuizAttempt.objects.filter(user=user)
            
            # ベストカテゴリーを取得（平均スコアが最も高いもの）
            best_category = None
            category_stats = []
            
            # カテゴリー別の統計を計算
            if attempts.exists():
                # percentage フィールドの代わりに計算式を使用
                categories = attempts.values('category', 'category__name').distinct()
                
                for cat in categories:
                    cat_attempts = attempts.filter(category=cat['category'])
                    cat_score_sum = cat_attempts.aggregate(Sum('score'))['score__sum'] or 0
                    cat_questions_sum = cat_attempts.aggregate(Sum('total_questions'))['total_questions__sum'] or 1
                    cat_percentage = (cat_score_sum / cat_questions_sum) * 100 if cat_questions_sum > 0 else 0
                    
                    cat_stats = {
                        'id': cat['category'],
                        'name': cat['category__name'],
                        'attempts_count': cat_attempts.count(),
                        'best_score': cat_attempts.aggregate(Max('score'))['score__max'] or 0,
                        'avg_percentage': round(cat_percentage, 1)
                    }
                    category_stats.append(cat_stats)
                    
                # 最高パーセンテージのカテゴリーを特定
                if category_stats:
                    best_cat = max(category_stats, key=lambda x: x['avg_percentage'])
                    best_category = best_cat['name']
            
            # 全体の平均パーセンテージを計算
            total_score = attempts.aggregate(Sum('score'))['score__sum'] or 0
            total_questions = attempts.aggregate(Sum('total_questions'))['total_questions__sum'] or 1
            avg_percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0
            
            # 全体統計
            overall_stats = {
                'total_attempts': attempts.count(),
                'total_categories_played': attempts.values('category').distinct().count(),
                'best_category': best_category,
                'avg_percentage': round(avg_percentage, 1),
                'category_stats': category_stats  # カテゴリー統計を追加
            }
            
            return overall_stats
            
        except Exception as e:
            # エラーのロギングと最小限のデータを返す
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in UserStatsView: {str(e)}")
            
            return {
                'total_attempts': 0,
                'total_categories_played': 0,
                'best_category': None,
                'avg_percentage': 0,
                'category_stats': [],
                'error': "統計情報の計算中にエラーが発生しました"
            }

class PublicLeaderboardView(generics.ListAPIView):
    """公開用リーダーボード（認証不要）"""
    permission_classes = [AllowAny]
    serializer_class = PublicLeaderboardSerializer
    
    def get_queryset(self):
        try:
            # 上位10名のデータを返す
            return User.objects.annotate(
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
            ).filter(total_attempts__gt=0).order_by('-avg_percentage')[:10]
        
        except Exception as e:
            # エラーを出力
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PublicLeaderboardView: {str(e)}")
            # 空のクエリセットを返す
            return User.objects.none()