# 開発ガイド

このドキュメントでは、クイズアプリケーションの開発環境構築、開発フロー、ベストプラクティス、デプロイ方法について説明します。

## 📋 目次

- [開発環境構築](#開発環境構築)
- [開発フロー](#開発フロー)
- [コーディング規約](#コーディング規約)
- [テスト](#テスト)
- [デバッグ](#デバッグ)
- [デプロイ](#デプロイ)
- [トラブルシューティング](#トラブルシューティング)
- [ベストプラクティス](#ベストプラクティス)

## 開発環境構築

### 必要なソフトウェア

#### 必須
- **Python** 3.11以上
- **Node.js** 14以上
- **npm** または **yarn**
- **Git**

#### 推奨
- **Visual Studio Code** または **PyCharm**
- **Postman** または **Insomnia** (API テスト用)
- **DB Browser for SQLite** (データベース確認用)

### バックエンド環境構築

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd quiz-app
```

#### 2. 仮想環境の作成

```bash
# Linux/Mac
cd quiz_project
python3 -m venv venv
source venv/bin/activate

# Windows
cd quiz_project
python -m venv venv
venv\Scripts\activate
```

#### 3. 依存パッケージのインストール

```bash
pip install --upgrade pip
pip install django djangorestframework django-cors-headers
pip install djangorestframework-simplejwt django-import-export django-extensions
```

または requirements.txt がある場合:

```bash
pip install -r requirements.txt
```

#### 4. データベースのセットアップ

```bash
# マイグレーション実行
python manage.py migrate

# 管理者ユーザー作成
python manage.py createsuperuser
```

#### 5. 開発サーバーの起動

```bash
python manage.py runserver
```

サーバーは http://localhost:8000 で起動します。

#### 6. 管理画面へのアクセス

http://localhost:8000/admin にアクセスして、作成した管理者アカウントでログインします。

### フロントエンド環境構築

#### 1. フロントエンドディレクトリに移動

```bash
cd quiz-frontend
```

#### 2. 依存パッケージのインストール

```bash
npm install
```

または

```bash
yarn install
```

#### 3. 開発サーバーの起動

```bash
npm run serve
```

または

```bash
yarn serve
```

サーバーは http://localhost:8080 で起動します。

### 環境変数の設定

#### バックエンド (.env)

```bash
# quiz_project/.env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 本番環境
# DATABASE_URL=postgres://user:password@localhost/dbname
# CORS_ALLOWED_ORIGINS=https://your-domain.com
```

Django settings.py で環境変数を読み込む:

```python
import os
from pathlib import Path

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
```

#### フロントエンド (.env)

```bash
# quiz-frontend/.env
VUE_APP_API_BASE_URL=http://localhost:8000/api
```

### VSCode 設定（推奨）

#### .vscode/settings.json

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/quiz_project/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

#### 推奨拡張機能

- Python (Microsoft)
- Pylance
- Django
- Vetur (Vue.js)
- ESLint
- Prettier

---

## 開発フロー

### ブランチ戦略

```
main          # 本番環境
  │
  ├── develop    # 開発環境
  │     │
  │     ├── feature/new-feature    # 新機能開発
  │     ├── feature/another-feature
  │     └── bugfix/fix-issue       # バグ修正
  │
  └── hotfix/urgent-fix   # 緊急修正
```

### 開発の流れ

#### 1. 新機能開発

```bash
# developブランチから新しいブランチを作成
git checkout develop
git pull origin develop
git checkout -b feature/quiz-timer

# 開発作業...

# コミット
git add .
git commit -m "Add quiz timer feature"

# プッシュ
git push origin feature/quiz-timer

# プルリクエスト作成
```

#### 2. コードレビュー

- プルリクエストを作成
- チームメンバーがレビュー
- 必要に応じて修正
- 承認後にマージ

#### 3. マージ

```bash
# developにマージ
git checkout develop
git merge feature/quiz-timer
git push origin develop

# 不要なブランチを削除
git branch -d feature/quiz-timer
```

### コミットメッセージ規約

```
<type>: <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `style`: コードスタイル変更（機能に影響なし）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルド・設定変更

**例**:
```
feat: Add quiz timer functionality

- Add timer component to Quiz.vue
- Add timer state to Vuex quiz module
- Add API endpoint for timed quizzes

Closes #123
```

---

## コーディング規約

### Python (Django バックエンド)

#### PEP 8 準拠

```python
# 良い例
def calculate_quiz_score(user_id, quiz_id):
    """クイズスコアを計算する"""
    attempt = QuizAttempt.objects.get(id=quiz_id)
    return attempt.score / attempt.total_questions * 100

# 悪い例
def calcScore(uid,qid):
    a=QuizAttempt.objects.get(id=qid)
    return a.score/a.total_questions*100
```

#### インポート順序

```python
# 1. 標準ライブラリ
import os
import sys
from datetime import datetime

# 2. サードパーティ
from django.db import models
from rest_framework import serializers

# 3. ローカル
from .models import Question
from .serializers import QuestionSerializer
```

#### docstring

```python
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    問題のViewSet

    カテゴリ別のフィルタリング、ランダム取得などの
    カスタムアクションを提供します。
    """

    def get_queryset(self):
        """
        クエリセットを取得

        Returns:
            QuerySet: フィルタリングされた問題のクエリセット
        """
        pass
```

#### 命名規則

```python
# クラス: PascalCase
class QuizAttempt(models.Model):
    pass

# 関数・変数: snake_case
def calculate_score():
    total_questions = 10
    correct_answers = 8

# 定数: UPPER_SNAKE_CASE
MAX_QUESTIONS_PER_QUIZ = 50
DEFAULT_PAGE_SIZE = 10
```

### JavaScript (Vue.js フロントエンド)

#### ESLint設定

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  }
}
```

#### Vue コンポーネント構造

```vue
<template>
  <!-- テンプレート -->
</template>

<script>
export default {
  name: 'ComponentName',

  components: {
    // 子コンポーネント
  },

  props: {
    // プロパティ
  },

  data() {
    return {
      // データ
    }
  },

  computed: {
    // 算出プロパティ
  },

  watch: {
    // ウォッチャー
  },

  methods: {
    // メソッド
  },

  mounted() {
    // ライフサイクルフック
  }
}
</script>

<style scoped>
/* スタイル */
</style>
```

#### 命名規則

```javascript
// コンポーネント: PascalCase
import QuizCard from './QuizCard.vue'

// 変数・関数: camelCase
const quizScore = 80
const calculatePercentage = () => {}

// 定数: UPPER_SNAKE_CASE
const MAX_ATTEMPTS = 3
```

---

## テスト

### バックエンドテスト

#### ユニットテスト

```python
# quiz_api/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Question, Choice

class QuestionModelTest(TestCase):
    def setUp(self):
        """テストデータのセットアップ"""
        self.category = Category.objects.create(name="Test Category")
        self.question = Question.objects.create(
            category=self.category,
            text="Test question?"
        )

    def test_question_creation(self):
        """問題の作成テスト"""
        self.assertEqual(self.question.text, "Test question?")
        self.assertEqual(self.question.category, self.category)

    def test_question_str(self):
        """__str__メソッドのテスト"""
        self.assertEqual(str(self.question), "Test question?")

class QuizAPITest(TestCase):
    def setUp(self):
        """APIテストのセットアップ"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_get_categories(self):
        """カテゴリ一覧取得のテスト"""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)

    def test_save_quiz_result(self):
        """クイズ結果保存のテスト"""
        data = {
            'category_id': 1,
            'score': 8,
            'total_questions': 10,
            'percentage': 80.0,
            'responses': []
        }
        response = self.client.post('/api/quiz/save-result/', data)
        self.assertEqual(response.status_code, 201)
```

#### テストの実行

```bash
# 全テスト実行
python manage.py test

# 特定アプリのテスト
python manage.py test quiz_api

# 特定テストクラス
python manage.py test quiz_api.tests.QuestionModelTest

# カバレッジ測定
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### フロントエンドテスト

#### ユニットテスト（Jest）

```javascript
// tests/unit/Quiz.spec.js
import { mount } from '@vue/test-utils'
import Quiz from '@/components/Quiz.vue'

describe('Quiz.vue', () => {
  it('renders quiz questions', () => {
    const wrapper = mount(Quiz, {
      data() {
        return {
          questions: [
            { id: 1, text: 'Test question?' }
          ]
        }
      }
    })
    expect(wrapper.text()).toContain('Test question?')
  })

  it('calculates score correctly', () => {
    const wrapper = mount(Quiz)
    wrapper.vm.calculateScore([
      { is_correct: true },
      { is_correct: false },
      { is_correct: true }
    ])
    expect(wrapper.vm.score).toBe(2)
  })
})
```

#### テストの実行

```bash
# ユニットテスト
npm run test:unit

# E2Eテスト
npm run test:e2e
```

---

## デバッグ

### バックエンドデバッグ

#### Django Shell

```bash
python manage.py shell
```

```python
# モデルの操作
from quiz_api.models import Question, Category

# すべてのカテゴリを取得
categories = Category.objects.all()

# 問題の作成
category = Category.objects.first()
question = Question.objects.create(
    category=category,
    text="Debug question"
)

# クエリセットのSQL確認
print(Question.objects.all().query)
```

#### ログ出力

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'quiz_api': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

```python
# views.py
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
```

#### Django Debug Toolbar

```bash
pip install django-debug-toolbar
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

INTERNAL_IPS = [
    '127.0.0.1',
]
```

### フロントエンドデバッグ

#### Vue Devtools

ブラウザ拡張機能をインストール:
- Chrome: Vue.js devtools
- Firefox: Vue.js devtools

#### console.log デバッグ

```javascript
export default {
  methods: {
    async fetchQuestions() {
      console.log('Fetching questions...')
      const response = await api.get('/questions/')
      console.log('Response:', response.data)
    }
  }
}
```

---

## デプロイ

### 本番環境の準備

#### 1. 環境変数の設定

```bash
# 環境変数ファイル
export SECRET_KEY='your-production-secret-key'
export DEBUG=False
export ALLOWED_HOSTS='your-domain.com,www.your-domain.com'
export DATABASE_URL='postgres://user:password@localhost/dbname'
export CORS_ALLOWED_ORIGINS='https://your-domain.com'
```

#### 2. requirements.txt の生成

```bash
pip freeze > requirements.txt
```

#### 3. 静的ファイルの収集

```bash
python manage.py collectstatic --noinput
```

### バックエンドデプロイ（Heroku）

#### 1. Heroku CLIのインストール

```bash
# インストール
curl https://cli-assets.heroku.com/install.sh | sh

# ログイン
heroku login
```

#### 2. Heroku アプリの作成

```bash
heroku create quiz-app-backend
```

#### 3. 必要なファイルの準備

**Procfile**:
```
web: gunicorn quiz_project.wsgi
```

**runtime.txt**:
```
python-3.11.0
```

**requirements.txt に追加**:
```
gunicorn
psycopg2-binary
dj-database-url
whitenoise
```

#### 4. settings.py の調整

```python
import dj_database_url

# データベース設定
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600
    )
}

# 静的ファイル
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 追加
    # ...
]
```

#### 5. デプロイ

```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# マイグレーション実行
heroku run python manage.py migrate

# 管理者ユーザー作成
heroku run python manage.py createsuperuser
```

### フロントエンドデプロイ（Netlify/Vercel）

#### 1. ビルド

```bash
npm run build
```

#### 2. Netlify でのデプロイ

```bash
# Netlify CLI インストール
npm install -g netlify-cli

# デプロイ
netlify deploy --prod --dir=dist
```

#### 3. 環境変数の設定

Netlify ダッシュボードで環境変数を設定:
```
VUE_APP_API_BASE_URL=https://quiz-app-backend.herokuapp.com/api
```

### Docker デプロイ

#### Dockerfile (バックエンド)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "quiz_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: quizdb
      POSTGRES_USER: quizuser
      POSTGRES_PASSWORD: quizpass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./quiz_project
    command: gunicorn quiz_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./quiz_project:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://quizuser:quizpass@db:5432/quizdb
      - SECRET_KEY=your-secret-key
      - DEBUG=False
    depends_on:
      - db

  frontend:
    build: ./quiz-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### デプロイ

```bash
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. CORS エラー

**エラー**:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:8080' has been blocked by CORS policy
```

**解決方法**:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

#### 2. マイグレーションエラー

**エラー**:
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**解決方法**:
```bash
# データベースをリセット
rm db.sqlite3
python manage.py migrate
```

#### 3. npm インストールエラー

**エラー**:
```
npm ERR! code ELIFECYCLE
```

**解決方法**:
```bash
# node_modules とロックファイルを削除
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 4. 静的ファイルが表示されない

**解決方法**:
```bash
python manage.py collectstatic --clear --noinput
```

---

## ベストプラクティス

### セキュリティ

1. **SECRET_KEYを環境変数に**
   ```python
   SECRET_KEY = os.environ.get('SECRET_KEY')
   ```

2. **DEBUGを本番でFalseに**
   ```python
   DEBUG = False
   ```

3. **パスワードの複雑性を強制**
   ```python
   AUTH_PASSWORD_VALIDATORS = [...]
   ```

4. **HTTPS を使用**
   ```python
   SECURE_SSL_REDIRECT = True
   SECURE_HSTS_SECONDS = 31536000
   ```

### パフォーマンス

1. **select_related/prefetch_related の使用**
   ```python
   questions = Question.objects.select_related('category').prefetch_related('choices')
   ```

2. **ページネーション**
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 10,
   }
   ```

3. **キャッシュの活用**
   ```python
   from django.views.decorators.cache import cache_page

   @cache_page(60 * 15)  # 15分キャッシュ
   def my_view(request):
       pass
   ```

### コード品質

1. **DRY原則** (Don't Repeat Yourself)
2. **SOLID原則**
3. **適切なコメント**
4. **意味のある変数名**
5. **小さな関数・メソッド**

---

このガイドに従って開発を進めることで、保守性が高く品質の良いコードを維持できます。新しいベストプラクティスやツールが見つかった場合は、このドキュメントを更新してください。
