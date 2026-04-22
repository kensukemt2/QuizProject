from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from .models import Category, Question, Choice, QuizAttempt, QuizSession, QuestionResponse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class CategoryModelTest(TestCase):
    """カテゴリーモデルのテスト"""

    def test_category_creation(self):
        """カテゴリーが正しく作成されるか"""
        category = Category.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")

    def test_category_ordering(self):
        """カテゴリーが名前順にソートされるか"""
        Category.objects.create(name="Zebra")
        Category.objects.create(name="Apple")
        Category.objects.create(name="Mango")

        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Apple")
        self.assertEqual(categories[1].name, "Mango")
        self.assertEqual(categories[2].name, "Zebra")


class QuestionModelTest(TestCase):
    """問題モデルのテスト"""

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_question_creation(self):
        """問題が正しく作成されるか"""
        question = Question.objects.create(
            category=self.category,
            text="Test Question"
        )
        self.assertEqual(str(question), "Test Question")
        self.assertEqual(question.category, self.category)

    def test_question_with_image(self):
        """画像付き問題が作成できるか"""
        question = Question.objects.create(
            category=self.category,
            text="Test Question with Image",
            image="test.jpg"
        )
        self.assertEqual(question.image, "test.jpg")


class ChoiceModelTest(TestCase):
    """選択肢モデルのテスト"""

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.question = Question.objects.create(
            category=self.category,
            text="Test Question"
        )

    def test_choice_creation(self):
        """選択肢が正しく作成されるか"""
        choice = Choice.objects.create(
            question=self.question,
            text="Choice 1",
            is_correct=True
        )
        self.assertEqual(str(choice), "Choice 1")
        self.assertTrue(choice.is_correct)

    def test_multiple_choices(self):
        """複数の選択肢が設定できるか"""
        Choice.objects.create(question=self.question, text="Choice 1", is_correct=True)
        Choice.objects.create(question=self.question, text="Choice 2", is_correct=False)
        Choice.objects.create(question=self.question, text="Choice 3", is_correct=False)

        self.assertEqual(self.question.choices.count(), 3)
        correct_choices = self.question.choices.filter(is_correct=True)
        self.assertEqual(correct_choices.count(), 1)


class QuizAttemptModelTest(TestCase):
    """クイズ結果モデルのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Math")

    def test_quiz_attempt_creation(self):
        """クイズ結果が正しく保存されるか"""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            category=self.category,
            score=7,
            total_questions=10,
            percentage=70.0
        )
        self.assertEqual(attempt.score, 7)
        self.assertEqual(attempt.total_questions, 10)
        self.assertEqual(attempt.percentage, 70.0)

    def test_quiz_attempt_string_representation(self):
        """クイズ結果の文字列表現が正しいか"""
        attempt = QuizAttempt.objects.create(
            user=self.user,
            category=self.category,
            score=8,
            total_questions=10,
            percentage=80.0
        )
        expected = f"testuser - Math - 8/10"
        self.assertEqual(str(attempt), expected)

    def test_quiz_attempt_ordering(self):
        """クイズ結果が新しい順にソートされるか"""
        attempt1 = QuizAttempt.objects.create(
            user=self.user, category=self.category,
            score=5, total_questions=10, percentage=50.0
        )
        attempt2 = QuizAttempt.objects.create(
            user=self.user, category=self.category,
            score=8, total_questions=10, percentage=80.0
        )

        attempts = QuizAttempt.objects.all()
        self.assertEqual(attempts[0], attempt2)  # 新しい方が先


class QuizSessionModelTest(TestCase):
    """クイズセッションモデルのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Science")
        self.question1 = Question.objects.create(category=self.category, text="Q1")
        self.question2 = Question.objects.create(category=self.category, text="Q2")

    def test_quiz_session_creation(self):
        """クイズセッションが作成できるか"""
        session = QuizSession.objects.create(
            session_id="test_session_123",
            user=self.user,
            category=self.category
        )
        self.assertEqual(session.session_id, "test_session_123")
        self.assertEqual(session.used_questions.count(), 0)

    def test_quiz_session_track_questions(self):
        """使用した問題を記録できるか"""
        session = QuizSession.objects.create(
            session_id="test_session_456",
            user=self.user,
            category=self.category
        )
        session.used_questions.add(self.question1)
        session.used_questions.add(self.question2)

        self.assertEqual(session.used_questions.count(), 2)
        self.assertIn(self.question1, session.used_questions.all())


class QuizAPITest(APITestCase):
    """クイズAPIのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category")
        self.client = APIClient()

    def get_tokens_for_user(self, user):
        """JWT トークンを取得"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_category_list_api(self):
        """カテゴリー一覧APIが動作するか"""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ページネーションされているので results キーをチェック
        self.assertEqual(len(response.data['results']), 1)

    def test_question_list_api(self):
        """問題一覧APIが動作するか"""
        question = Question.objects.create(
            category=self.category,
            text="Test Question"
        )
        response = self.client.get('/api/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_filter_by_category(self):
        """カテゴリーで問題をフィルタリングできるか"""
        category2 = Category.objects.create(name="Another Category")

        q1 = Question.objects.create(category=self.category, text="Q1")
        q2 = Question.objects.create(category=category2, text="Q2")

        response = self.client.get(f'/api/questions/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_user_registration(self):
        """ユーザー登録APIが動作するか"""
        from unittest.mock import patch
        with patch('quiz_api.views.AuthRateThrottle.allow_request', return_value=True):
            data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'SecurePass123',
                'password2': 'SecurePass123'
            }
            response = self.client.post('/api/register/', data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(User.objects.filter(username='newuser').exists())


class QuizResultAPITest(APITestCase):
    """クイズ結果関連APIのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Math")
        self.question = Question.objects.create(
            category=self.category,
            text="What is 2+2?"
        )
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text="4",
            is_correct=True
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text="5",
            is_correct=False
        )

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_save_quiz_result(self):
        """クイズ結果が保存できるか"""
        data = {
            'category_id': self.category.id,
            'score': 7,
            'total_questions': 10,
            'responses': [
                {
                    'question_id': self.question.id,
                    'selected_choice_id': self.correct_choice.id,
                    'is_correct': True
                }
            ]
        }
        response = self.client.post('/api/quiz/save-result/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(QuizAttempt.objects.count(), 1)

    def test_user_quiz_history(self):
        """ユーザーのクイズ履歴が取得できるか"""
        QuizAttempt.objects.create(
            user=self.user,
            category=self.category,
            score=8,
            total_questions=10,
            percentage=80.0
        )

        response = self.client.get('/api/user/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticationTest(APITestCase):
    """認証のテスト"""

    def test_unauthenticated_access(self):
        """未認証でのアクセスが拒否されるか"""
        response = self.client.get('/api/user/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_authentication(self):
        """トークン認証が正しく動作するか"""
        user = User.objects.create_user(username='testuser', password='testpass')
        refresh = RefreshToken.for_user(user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/user/stats/')
        # 認証は通るはず（データがなくても200が返る）
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LeaderboardAPITest(APITestCase):
    """リーダーボードAPIのテスト"""

    def setUp(self):
        # ユーザーを作成
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')

        # カテゴリを作成
        self.category1 = Category.objects.create(name="Math")
        self.category2 = Category.objects.create(name="Science")

        # クイズ結果を作成
        # User1: Math で高スコア、Science でも参加
        QuizAttempt.objects.create(
            user=self.user1, category=self.category1,
            score=9, total_questions=10, percentage=90.0
        )
        QuizAttempt.objects.create(
            user=self.user1, category=self.category2,
            score=7, total_questions=10, percentage=70.0
        )

        # User2: Math で中スコア
        QuizAttempt.objects.create(
            user=self.user2, category=self.category1,
            score=6, total_questions=10, percentage=60.0
        )

        # User3: Science のみ
        QuizAttempt.objects.create(
            user=self.user3, category=self.category2,
            score=8, total_questions=10, percentage=80.0
        )

        self.client = APIClient()

    def test_public_leaderboard_all_categories(self):
        """全カテゴリのリーダーボードが取得できるか"""
        response = self.client.get('/api/quiz/leaderboard/?category=all')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_leaderboard_category_filtering(self):
        """カテゴリフィルタリングが正しく動作するか"""
        response = self.client.get(f'/api/quiz/leaderboard/?category={self.category1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        # Math カテゴリに参加したユーザーのみが表示されるはず
        self.assertGreater(len(results), 0)

        # User1 が最高スコアなので1位のはず
        if len(results) > 0:
            top_user = results[0]
            self.assertEqual(top_user['username'], 'user1')
            self.assertEqual(top_user['category_attempts'], 1)
            self.assertGreater(top_user['category_percentage'], 0)

    def test_leaderboard_shows_category_stats(self):
        """カテゴリ別統計が正しく表示されるか"""
        response = self.client.get(f'/api/quiz/leaderboard/?category={self.category1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        if len(results) > 0:
            user_data = results[0]
            # カテゴリ別統計が含まれているか確認
            self.assertIn('category_attempts', user_data)
            self.assertIn('category_score', user_data)
            self.assertIn('category_questions', user_data)
            self.assertIn('category_percentage', user_data)

    def test_leaderboard_different_categories(self):
        """異なるカテゴリで異なる結果が返るか"""
        response_math = self.client.get(f'/api/quiz/leaderboard/?category={self.category1.id}')
        response_science = self.client.get(f'/api/quiz/leaderboard/?category={self.category2.id}')

        self.assertEqual(response_math.status_code, status.HTTP_200_OK)
        self.assertEqual(response_science.status_code, status.HTTP_200_OK)

        # 両方とも結果があることを確認
        self.assertGreater(len(response_math.data['results']), 0)
        self.assertGreater(len(response_science.data['results']), 0)

    def test_leaderboard_ordering(self):
        """リーダーボードが正しくソートされているか"""
        response = self.client.get(f'/api/quiz/leaderboard/?category={self.category1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        if len(results) >= 2:
            # パーセンテージが降順になっているか確認
            self.assertGreaterEqual(
                results[0]['category_percentage'],
                results[1]['category_percentage']
            )


class RandomQuestionsAPITest(APITestCase):
    """ランダム問題取得APIのテスト"""

    def setUp(self):
        self.category = Category.objects.create(name="Math")
        # 選択肢付きの問題を5つ作成
        for i in range(5):
            q = Question.objects.create(category=self.category, text=f"Q{i+1}")
            Choice.objects.create(question=q, text="A", is_correct=True)
            Choice.objects.create(question=q, text="B", is_correct=False)

    def test_random_questions_endpoint(self):
        """random_questionsエンドポイントが動作するか"""
        response = self.client.get('/api/questions/random_questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_random_questions_with_limit(self):
        """件数制限が正しく動作するか"""
        response = self.client.get('/api/questions/random_questions/?limit=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_random_questions_with_category(self):
        """カテゴリフィルターが動作するか"""
        other_cat = Category.objects.create(name="Science")
        q = Question.objects.create(category=other_cat, text="SciQ")
        Choice.objects.create(question=q, text="A", is_correct=True)

        response = self.client.get(f'/api/questions/random_questions/?category={other_cat.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_random_questions_exclude(self):
        """除外IDが正しく動作するか"""
        all_q = Question.objects.all()
        exclude_ids = ','.join(str(q.id) for q in all_q[:3])
        response = self.client.get(f'/api/questions/random_questions/?exclude={exclude_ids}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_unique_random_endpoint(self):
        """unique_randomエンドポイントが動作するか"""
        response = self.client.get('/api/questions/unique_random/?limit=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        # 重複がないことを確認
        ids = [q['id'] for q in response.data['results']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unique_random_with_seed(self):
        """シード値指定で再現可能なランダムが動作するか"""
        r1 = self.client.get('/api/questions/unique_random/?limit=3&seed=42')
        r2 = self.client.get('/api/questions/unique_random/?limit=3&seed=42')
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

    def test_unique_random_empty_category(self):
        """問題のないカテゴリで空結果が返るか"""
        empty_cat = Category.objects.create(name="Empty")
        response = self.client.get(f'/api/questions/unique_random/?category={empty_cat.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class InputValidationTest(APITestCase):
    """入力バリデーションのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name="Math")
        self.question = Question.objects.create(category=self.category, text="Q1")
        self.choice = Choice.objects.create(question=self.question, text="A", is_correct=True)
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_save_result_score_exceeds_total(self):
        """スコアが問題数を超える場合にエラーになるか"""
        data = {
            'category_id': self.category.id,
            'score': 15,
            'total_questions': 10,
            'responses': []
        }
        response = self.client.post('/api/quiz/save-result/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_result_negative_score(self):
        """負のスコアがエラーになるか"""
        data = {
            'category_id': self.category.id,
            'score': -1,
            'total_questions': 10,
            'responses': []
        }
        response = self.client.post('/api/quiz/save-result/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_result_zero_total_questions(self):
        """問題数0がエラーになるか"""
        data = {
            'category_id': self.category.id,
            'score': 0,
            'total_questions': 0,
            'responses': []
        }
        response = self.client.post('/api/quiz/save-result/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_result_invalid_category(self):
        """存在しないカテゴリIDがエラーになるか"""
        data = {
            'category_id': 99999,
            'score': 5,
            'total_questions': 10,
            'responses': []
        }
        response = self.client.post('/api/quiz/save-result/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_result_unauthenticated(self):
        """未認証でのクイズ結果保存が拒否されるか"""
        self.client.credentials()  # 認証解除
        data = {
            'category_id': self.category.id,
            'score': 5,
            'total_questions': 10,
            'responses': []
        }
        response = self.client.post('/api/quiz/save-result/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_question_limit_negative(self):
        """負のlimit値が無視されるか"""
        response = self.client.get('/api/questions/?limit=-5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_limit_invalid(self):
        """不正なlimit値が無視されるか"""
        response = self.client.get('/api/questions/?limit=abc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_password_mismatch(self):
        """パスワード不一致でエラーになるか"""
        data = {
            'username': 'newuser',
            'password': 'SecurePass123',
            'password2': 'DifferentPass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_username(self):
        """重複ユーザー名でエラーになるか"""
        data = {
            'username': 'testuser',  # 既存ユーザー
            'password': 'SecurePass123',
            'password2': 'SecurePass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class QuizHistoryAPITest(APITestCase):
    """クイズ履歴APIのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.category = Category.objects.create(name="Math")
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_history_only_shows_own_attempts(self):
        """他のユーザーの履歴が見えないか"""
        QuizAttempt.objects.create(
            user=self.user, category=self.category,
            score=8, total_questions=10, percentage=80.0
        )
        QuizAttempt.objects.create(
            user=self.other_user, category=self.category,
            score=6, total_questions=10, percentage=60.0
        )
        response = self.client.get('/api/quiz/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_history_unauthenticated(self):
        """未認証で履歴にアクセスできないか"""
        self.client.credentials()
        response = self.client.get('/api/quiz/history/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_attempt_detail(self):
        """クイズ結果の詳細を取得できるか"""
        attempt = QuizAttempt.objects.create(
            user=self.user, category=self.category,
            score=8, total_questions=10, percentage=80.0
        )
        response = self.client.get(f'/api/quiz/history/{attempt.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 8)

    def test_attempt_detail_other_user(self):
        """他のユーザーの結果詳細にアクセスできないか"""
        attempt = QuizAttempt.objects.create(
            user=self.other_user, category=self.category,
            score=6, total_questions=10, percentage=60.0
        )
        response = self.client.get(f'/api/quiz/history/{attempt.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class QuestionResponseModelTest(TestCase):
    """回答レスポンスモデルのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Math")
        self.question = Question.objects.create(category=self.category, text="Q1")
        self.choice = Choice.objects.create(question=self.question, text="A", is_correct=True)
        self.attempt = QuizAttempt.objects.create(
            user=self.user, category=self.category,
            score=1, total_questions=1, percentage=100.0
        )

    def test_question_response_creation(self):
        """回答レスポンスが正しく作成されるか"""
        response = QuestionResponse.objects.create(
            quiz_attempt=self.attempt,
            question=self.question,
            selected_choice=self.choice,
            is_correct=True
        )
        self.assertTrue(response.is_correct)
        self.assertIn('正解', str(response))

    def test_question_response_incorrect(self):
        """不正解の回答レスポンス"""
        wrong_choice = Choice.objects.create(
            question=self.question, text="B", is_correct=False
        )
        response = QuestionResponse.objects.create(
            quiz_attempt=self.attempt,
            question=self.question,
            selected_choice=wrong_choice,
            is_correct=False
        )
        self.assertFalse(response.is_correct)
        self.assertIn('不正解', str(response))
