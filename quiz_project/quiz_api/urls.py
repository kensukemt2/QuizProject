from django.urls import path, include
from . import views
from .views import (
    CategoryViewSet, QuestionViewSet, RegisterView, UserProfileView,
    SaveQuizResultView, QuizHistoryView, QuizAttemptDetailView,
    LeaderboardView, UserStatsView  # LeaderboardViewを追加
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
    path('quiz/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),  # この行を追加
    path('user/stats/', UserStatsView.as_view(), name='user-stats'),  # ユーザー統計のパスも追加
]

urlpatterns += router.urls