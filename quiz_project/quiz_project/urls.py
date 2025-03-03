"""
URL configuration for quiz_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# quiz_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from quiz_api.views import CategoryViewSet, QuestionViewSet, SaveQuizResultView, QuizHistoryView, QuizAttemptDetailView, LeaderboardView, UserStatsView, RegisterView, UserProfileView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # 既存のURLパターン
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),
    
]
# 過去のクイズ結果の保存
urlpatterns += [
    path('api/quiz/save-result/', SaveQuizResultView.as_view(), name='save_quiz_result'),
    path('api/quiz/history/', QuizHistoryView.as_view(), name='quiz_history'),
    path('api/quiz/history/<int:pk>/', QuizAttemptDetailView.as_view(), name='quiz_attempt_detail'),
]
# リーダーボード
urlpatterns += [
    path('api/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
#ユーザープロフィールとパフォーマンス統計
urlpatterns += [
    path('api/user/stats/', UserStatsView.as_view(), name='user_stats'),
]
