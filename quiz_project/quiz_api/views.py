# quiz_api/views.py
import logging
import random

from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum, Max, F, ExpressionWrapper, FloatField, IntegerField, Q, Case, When, Value

from .models import Category, Question, Choice, QuizAttempt, QuizSession
from .serializers import (
    CategorySerializer, QuestionSerializer, ChoiceSerializer,
    RegisterSerializer, UserSerializer, SaveQuizResultSerializer,
    QuizAttemptSerializer, UserLeaderboardSerializer, UserStatsSerializer,
    PublicLeaderboardSerializer,
)

logger = logging.getLogger(__name__)


def select_random_questions(queryset, limit):
    """クエリセットからランダムにlimit件を選択して返す共通ユーティリティ"""
    all_items = list(queryset)
    if len(all_items) <= limit:
        selected = all_items
    else:
        selected = random.sample(all_items, limit)
    random.shuffle(selected)
    return selected


def filter_questions_with_choices(queryset, category=None):
    """カテゴリフィルターと選択肢ありフィルターを適用する共通ユーティリティ"""
    qs = queryset.select_related('category').prefetch_related('choices')
    if category and category != 'all':
        try:
            qs = qs.filter(category__id=int(category))
        except ValueError:
            pass
    return qs.filter(choices__isnull=False).distinct()


def parse_limit(value, default=10, maximum=50):
    """limit パラメータを安全にパースする"""
    try:
        return max(1, min(int(value), maximum))
    except (ValueError, TypeError):
        return default


class AuthRateThrottle(AnonRateThrottle):
    """認証エンドポイント専用のレート制限"""
    rate = '5/minute'

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')  # 名前でソート
    serializer_class = CategorySerializer

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        queryset = Question.objects.all()
        category = self.request.query_params.get('category', None)
        random_order = self.request.query_params.get('random', None)
        limit = self.request.query_params.get('limit', None)
        force_order = self.request.query_params.get('order', None)
        
        # カテゴリーフィルター
        if category is not None:
            queryset = queryset.filter(category__id=category)
        
        # 順序制御（デフォルトをランダムに変更）
        if force_order == 'id':
            # 明示的にID順が指定された場合のみID順
            queryset = queryset.order_by('id')
        elif random_order and random_order.lower() == 'false':
            # 明示的にランダムを無効化
            queryset = queryset.order_by('id')
        else:
            # デフォルトはランダム（カテゴリー指定時のみ）
            if category is not None:
                queryset = queryset.order_by('?')
            else:
                queryset = queryset.order_by('id')
        
        # 件数制限
        if limit is not None:
            try:
                limit_num = int(limit)
                if limit_num > 0:
                    queryset = queryset[:min(limit_num, 50)]
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def unique_random(self, request):
        """重複なしランダム問題取得（強化版）"""
        category = request.query_params.get('category', None)
        limit_num = parse_limit(request.query_params.get('limit', '10'))
        seed = request.query_params.get('seed', None)

        queryset = filter_questions_with_choices(Question.objects.all(), category)

        # シード値が指定されている場合は再現可能なランダム
        if seed:
            try:
                random.seed(int(seed))
            except ValueError:
                random.seed(hash(seed) % (2**32))

        all_questions = list(queryset)
        if not all_questions:
            return Response({
                'count': 0,
                'results': [],
                'message': '指定された条件に合う問題が見つかりませんでした'
            })

        selected_questions = select_random_questions(queryset, limit_num)

        # シード値をリセット
        if seed:
            random.seed()

        serializer = self.get_serializer(selected_questions, many=True)
        return Response({
            'count': len(selected_questions),
            'results': serializer.data,
            'total_available': len(all_questions),
            'message': f'{len(selected_questions)}問の問題をランダムに取得しました（重複なし保証）'
        })
    
    @action(detail=False, methods=['get'])
    def session_questions(self, request):
        """セッション管理による完全重複なし問題取得"""
        import uuid

        category = request.query_params.get('category', None)
        session_id = request.query_params.get('session_id', '') or f"quiz_{uuid.uuid4().hex[:12]}"
        limit_num = parse_limit(request.query_params.get('limit', '10'), maximum=20)
        reset_session = request.query_params.get('reset', 'false')

        # セッションを取得または作成
        session, created = QuizSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'category_id': int(category) if category and category != 'all' else None
            }
        )

        if reset_session.lower() == 'true':
            session.used_questions.clear()
            session.save()

        queryset = filter_questions_with_choices(Question.objects.all(), category)

        # 既に使用した問題を除外
        used_question_ids = session.used_questions.values_list('id', flat=True)
        available_queryset = queryset.exclude(id__in=used_question_ids)

        # 利用可能な問題がない場合
        message_suffix = ''
        if not available_queryset.exists():
            if not queryset.exists():
                return Response({
                    'count': 0, 'results': [], 'session_id': session_id,
                    'message': '指定された条件に合う問題が見つかりませんでした',
                    'total_available': 0, 'used_count': 0
                })
            session.used_questions.clear()
            session.save()
            available_queryset = queryset
            message_suffix = '（すべての問題を出題済みのため、セッションをリセットしました）'

        selected_questions = select_random_questions(available_queryset, limit_num)

        if selected_questions:
            session.used_questions.add(*selected_questions)
            session.save()

        serializer = self.get_serializer(selected_questions, many=True)
        return Response({
            'count': len(selected_questions),
            'results': serializer.data,
            'session_id': session_id,
            'total_available': queryset.count(),
            'used_count': session.used_questions.count(),
            'remaining': queryset.count() - session.used_questions.count(),
            'message': f'{len(selected_questions)}問の問題を取得しました（セッション管理による重複なし保証）{message_suffix}'
        })
    
    @action(detail=False, methods=['get'])
    def random_questions(self, request):
        """ランダムな問題を取得するAPI"""
        category = request.query_params.get('category', None)
        limit_num = parse_limit(request.query_params.get('limit', '10'))
        exclude = request.query_params.get('exclude', '')

        queryset = filter_questions_with_choices(Question.objects.all(), category)

        # 除外する問題があれば除外
        if exclude:
            try:
                exclude_ids = [int(x.strip()) for x in exclude.split(',') if x.strip()]
                if exclude_ids:
                    queryset = queryset.exclude(id__in=exclude_ids)
            except ValueError:
                pass

        questions = select_random_questions(queryset, limit_num)
        serializer = self.get_serializer(questions, many=True)
        return Response({
            'count': len(questions),
            'results': serializer.data,
            'message': f'{len(questions)}問の問題をランダムに取得しました'
        })
    
    @action(detail=False, methods=['get'])
    def quiz_session(self, request):
        """クイズセッション用の問題取得（重複除外機能付き）"""
        category = request.query_params.get('category', None)
        session_id = request.query_params.get('session_id', '')
        question_count = parse_limit(request.query_params.get('count', '10'), maximum=20)
        exclude_recent = request.query_params.get('exclude_recent', 'true')

        queryset = filter_questions_with_choices(Question.objects.all(), category)

        # 最近出題された問題を除外（認証ユーザーの場合）
        if exclude_recent.lower() == 'true' and request.user.is_authenticated:
            from datetime import timedelta
            from django.utils import timezone

            recent_time = timezone.now() - timedelta(hours=1)
            recent_attempts = QuizAttempt.objects.filter(
                user=request.user,
                created_at__gte=recent_time
            ).values_list('responses__question_id', flat=True)

            if recent_attempts:
                queryset = queryset.exclude(id__in=recent_attempts)

        total_questions = queryset.count()
        if total_questions == 0:
            return Response({
                'count': 0, 'results': [],
                'message': '指定された条件に合う問題が見つかりませんでした',
                'total_available': 0
            })

        questions = select_random_questions(queryset, question_count)
        serializer = self.get_serializer(questions, many=True)
        return Response({
            'count': len(questions),
            'results': serializer.data,
            'session_id': session_id or f'session_{random.randint(1000, 9999)}',
            'total_available': total_questions,
            'message': f'{len(questions)}問の問題を取得しました（利用可能: {total_questions}問）'
        })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AuthRateThrottle]
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
        return (
            QuizAttempt.objects.filter(user=self.request.user)
            .select_related('user', 'category')
            .prefetch_related('responses__question', 'responses__selected_choice')
        )

class QuizAttemptDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        return (
            QuizAttempt.objects.filter(user=self.request.user)
            .select_related('user', 'category')
            .prefetch_related('responses__question', 'responses__selected_choice')
        )
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
            logger.error(f"Error in UserStatsView: {e}", exc_info=True)
            
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
            # カテゴリフィルターを取得
            category_id = self.request.query_params.get('category', None)

            # ベースとなる全体統計を計算
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

            # カテゴリフィルターが指定されている場合
            if category_id and category_id != 'all':
                try:
                    category_id_int = int(category_id)
                    queryset = queryset.annotate(
                        category_attempts=Count('quiz_attempts', filter=Q(quiz_attempts__category_id=category_id_int)),
                        category_score=Sum('quiz_attempts__score', filter=Q(quiz_attempts__category_id=category_id_int), default=0),
                        category_questions=Sum('quiz_attempts__total_questions', filter=Q(quiz_attempts__category_id=category_id_int), default=0),
                        category_percentage=Case(
                            When(category_questions__gt=0,
                                then=ExpressionWrapper(
                                    F('category_score') * 100.0 / F('category_questions'),
                                    output_field=FloatField()
                                )
                            ),
                            default=Value(0.0),
                            output_field=FloatField()
                        )
                    ).filter(category_attempts__gt=0).order_by('-category_percentage')[:10]
                except ValueError:
                    # カテゴリIDが無効な場合は全体統計を使用
                    queryset = queryset.annotate(
                        category_attempts=Value(0, output_field=IntegerField()),
                        category_score=Value(0, output_field=IntegerField()),
                        category_questions=Value(0, output_field=IntegerField()),
                        category_percentage=Value(0.0, output_field=FloatField())
                    ).filter(total_attempts__gt=0).order_by('-avg_percentage')[:10]
            else:
                # カテゴリフィルターが指定されていない場合はデフォルト値を設定
                queryset = queryset.annotate(
                    category_attempts=Value(0, output_field=IntegerField()),
                    category_score=Value(0, output_field=IntegerField()),
                    category_questions=Value(0, output_field=IntegerField()),
                    category_percentage=Value(0.0, output_field=FloatField())
                ).filter(total_attempts__gt=0).order_by('-avg_percentage')[:10]

            return queryset

        except Exception as e:
            logger.error(f"Error in PublicLeaderboardView: {e}", exc_info=True)
            return User.objects.none()