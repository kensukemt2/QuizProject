from django.urls import path, include
from . import views
from .views import (
    CategoryViewSet, QuestionViewSet, RegisterView, UserProfileView,
    SaveQuizResultView, QuizHistoryView, QuizAttemptDetailView,
    LeaderboardView, UserStatsView, PublicLeaderboardView  # PublicLeaderboardViewを追加
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('quiz/save-result/', SaveQuizResultView.as_view(), name='save-quiz-result'),
    path('quiz/history/', QuizHistoryView.as_view(), name='quiz-history'),
    path('quiz/attempt/<int:pk>/', QuizAttemptDetailView.as_view(), name='quiz-attempt-detail'),
    path('quiz/leaderboard/', PublicLeaderboardView.as_view(), name='public-leaderboard'),  # 公開リーダーボード
    path('quiz/leaderboard/authenticated/', LeaderboardView.as_view(), name='leaderboard'),  # 認証必要なリーダーボード
    path('user/stats/', UserStatsView.as_view(), name='user-stats'),  # ユーザー統計のパスも追加
]

urlpatterns += router.urls