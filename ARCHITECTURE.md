# システムアーキテクチャ

このドキュメントでは、クイズアプリケーションのシステムアーキテクチャ、技術構成、コンポーネント間の相互作用について詳しく説明します。

## 📋 目次

- [システム概要](#システム概要)
- [アーキテクチャパターン](#アーキテクチャパターン)
- [技術スタック詳細](#技術スタック詳細)
- [バックエンドアーキテクチャ](#バックエンドアーキテクチャ)
- [フロントエンドアーキテクチャ](#フロントエンドアーキテクチャ)
- [データフロー](#データフロー)
- [認証フロー](#認証フロー)
- [セキュリティ設計](#セキュリティ設計)

## システム概要

### システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                        クライアント                          │
│                     (Webブラウザ)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/HTTPS
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   Vue.js Frontend                            │
│                  (http://localhost:8080)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Components   │  │ Vuex Store   │  │ Vue Router   │     │
│  │ (UI Layer)   │◄─┤ (State Mgmt) │  │ (Routing)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                                 │
│         └──────────────────┴─────────────────────┐          │
│                                                   │          │
│                                         ┌─────────▼────────┐ │
│                                         │   Axios (API)    │ │
│                                         └─────────┬────────┘ │
└───────────────────────────────────────────────────┼─────────┘
                                                    │
                                   REST API (JSON) │
                                   JWT Authentication
                                                    │
┌───────────────────────────────────────────────────▼─────────┐
│              Django REST Framework Backend                   │
│                 (http://localhost:8000)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Layer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐     │  │
│  │  │ ViewSets │  │  Views   │  │ Serializers   │     │  │
│  │  └──────────┘  └──────────┘  └───────────────┘     │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              Business Logic Layer                     │  │
│  │  ┌─────────────┐  ┌──────────────┐                  │  │
│  │  │   Models    │  │ Permissions  │                  │  │
│  │  │  (ORM)      │  │  & Auth      │                  │  │
│  │  └─────────────┘  └──────────────┘                  │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │                 Data Layer                            │  │
│  │            Django ORM + SQLite                        │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   SQLite Database     │
              │     (db.sqlite3)      │
              └───────────────────────┘
```

## アーキテクチャパターン

### 全体アーキテクチャ: マイクロサービス的分離

- **フロントエンド**: SPA (Single Page Application)
- **バックエンド**: RESTful API サーバー
- **分離の利点**:
  - 独立した開発・デプロイが可能
  - スケーラビリティの向上
  - 技術スタックの柔軟性

### バックエンド: MVT (Model-View-Template) パターン

Djangoの標準的なMVTパターンを採用していますが、REST APIではTemplateの代わりにシリアライザを使用:

- **Model**: データベース構造とビジネスロジック
- **View**: リクエスト処理とレスポンス生成
- **Serializer**: データのJSON変換（Templateの代替）

### フロントエンド: MVVM (Model-View-ViewModel) パターン

Vue.jsの標準的なパターン:

- **Model**: Vuexストア（状態管理）
- **View**: Vueコンポーネント（UIテンプレート）
- **ViewModel**: Vueコンポーネントのスクリプト部分

## 技術スタック詳細

### バックエンド技術スタック

```
┌─────────────────────────────────────────────────────┐
│                    Python 3.11+                      │
├─────────────────────────────────────────────────────┤
│              Django 5.1.6 (Web Framework)            │
├─────────────────────────────────────────────────────┤
│         Django REST Framework (API Layer)            │
│  ┌────────────────┐  ┌──────────────────────┐      │
│  │   ViewSets     │  │   Serializers        │      │
│  │   Routers      │  │   Pagination         │      │
│  └────────────────┘  └──────────────────────┘      │
├─────────────────────────────────────────────────────┤
│                  認証・セキュリティ                  │
│  ┌────────────────────────────────────────┐         │
│  │ djangorestframework-simplejwt          │         │
│  │ (JWT認証)                              │         │
│  └────────────────────────────────────────┘         │
│  ┌────────────────────────────────────────┐         │
│  │ django-cors-headers                    │         │
│  │ (CORS制御)                             │         │
│  └────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────┤
│                  拡張機能                            │
│  ┌───────────────┐  ┌──────────────────┐           │
│  │ import_export │  │ django_extensions│           │
│  └───────────────┘  └──────────────────┘           │
├─────────────────────────────────────────────────────┤
│          ORM (Object-Relational Mapping)             │
│                  Django ORM                          │
├─────────────────────────────────────────────────────┤
│                 Database Driver                      │
│                SQLite3 (開発環境)                    │
│         PostgreSQL/MySQL (本番環境推奨)             │
└─────────────────────────────────────────────────────┘
```

### フロントエンド技術スタック

```
┌─────────────────────────────────────────────────────┐
│                    Vue.js 3.2                        │
│              (Progressive Framework)                 │
├─────────────────────────────────────────────────────┤
│                  コアライブラリ                      │
│  ┌────────────────┐  ┌──────────────────────┐      │
│  │  Vue Router 4  │  │      Vuex 4          │      │
│  │  (ルーティング) │  │   (状態管理)         │      │
│  └────────────────┘  └──────────────────────┘      │
├─────────────────────────────────────────────────────┤
│                  HTTP通信                            │
│  ┌────────────────────────────────────────┐         │
│  │         Axios 1.8                      │         │
│  │    (HTTP Client)                       │         │
│  └────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────┤
│                   UI/UX                              │
│  ┌────────────────────────────────────────┐         │
│  │    vue-toastification                  │         │
│  │    (通知・トースト)                     │         │
│  └────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────┤
│                ビルドツール                          │
│  ┌────────────────────────────────────────┐         │
│  │      Vue CLI 5.0                       │         │
│  │      Babel                             │         │
│  │      ESLint                            │         │
│  └────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────┘
```

## バックエンドアーキテクチャ

### ディレクトリ構造

```
quiz_project/
├── manage.py                    # Django管理コマンド
├── db.sqlite3                  # SQLiteデータベース
├── media/                      # アップロードファイル
│   └── question_images/        # 問題画像
├── quiz_api/                   # メインアプリケーション
│   ├── __init__.py
│   ├── models.py              # データモデル定義
│   ├── views.py               # APIビュー実装
│   ├── serializers.py         # シリアライザ定義
│   ├── urls.py                # URLルーティング
│   ├── admin.py               # 管理画面設定
│   ├── apps.py                # アプリケーション設定
│   ├── pagination.py          # ページネーション設定
│   ├── resources.py           # インポート/エクスポート設定
│   ├── tests.py               # テストコード
│   └── migrations/            # データベースマイグレーション
└── quiz_project/              # プロジェクト設定
    ├── __init__.py
    ├── settings.py           # Django設定
    ├── urls.py               # ルートURLconf
    ├── wsgi.py               # WSGI設定
    └── asgi.py               # ASGI設定
```

### レイヤー構成

#### 1. API Layer (views.py)

**ViewSets**:
```python
CategoryViewSet        # カテゴリ管理（読み取り専用）
QuestionViewSet        # 問題管理（拡張カスタムアクション付き）
```

**Generic Views**:
```python
RegisterView           # ユーザー登録
UserProfileView        # プロフィール取得
SaveQuizResultView     # 結果保存
QuizHistoryView        # 履歴一覧
QuizAttemptDetailView  # 履歴詳細
LeaderboardView        # リーダーボード
UserStatsView          # ユーザー統計
PublicLeaderboardView  # 公開リーダーボード
```

**カスタムアクション** (QuestionViewSet):
```python
@action unique_random()      # 重複なしランダム問題（シード対応）
@action session_questions()  # セッション管理型問題取得
@action random_questions()   # 基本ランダム問題
@action quiz_session()       # クイズセッション（最近の除外機能付き）
```

#### 2. Business Logic Layer (models.py)

**データモデル**:
```python
Category          # カテゴリ
Question          # 問題
Choice            # 選択肢
QuizAttempt       # クイズ試行記録
QuestionResponse  # 問題ごとの回答記録
QuizSession       # セッション管理
```

**リレーション**:
- Category 1:N Question
- Question 1:N Choice
- User 1:N QuizAttempt
- QuizAttempt 1:N QuestionResponse
- QuizSession M:N Question

#### 3. Data Serialization Layer (serializers.py)

```python
CategorySerializer           # カテゴリシリアライズ
QuestionSerializer          # 問題シリアライズ（choices含む）
ChoiceSerializer            # 選択肢シリアライズ
RegisterSerializer          # ユーザー登録
UserSerializer              # ユーザー情報
SaveQuizResultSerializer    # 結果保存
QuizAttemptSerializer       # 履歴シリアライズ
UserLeaderboardSerializer   # リーダーボード
UserStatsSerializer         # 統計情報
PublicLeaderboardSerializer # 公開リーダーボード
```

### 認証システム

```
┌─────────────────────────────────────────────────┐
│         JWT (JSON Web Token) 認証                │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. ユーザーログイン                              │
│     POST /api/token/                             │
│     → Access Token (有効期限: 1日)               │
│     → Refresh Token (有効期限: 7日)              │
│                                                  │
│  2. API リクエスト                               │
│     Header: Authorization: Bearer <token>        │
│                                                  │
│  3. トークン更新                                 │
│     POST /api/token/refresh/                     │
│     → 新しい Access Token                        │
│                                                  │
└─────────────────────────────────────────────────┘
```

### パフォーマンス最適化

#### クエリ最適化
```python
# select_related (1:1, N:1)
Question.objects.select_related('category')

# prefetch_related (1:N, M:N)
Question.objects.prefetch_related('choices')

# 複合
queryset = Question.objects.select_related('category').prefetch_related('choices')
```

#### ページネーション
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

#### キャッシュ
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

## フロントエンドアーキテクチャ

### ディレクトリ構造

```
quiz-frontend/
├── public/                    # 静的ファイル
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── main.js               # エントリーポイント
│   ├── App.vue               # ルートコンポーネント
│   ├── components/           # Vueコンポーネント
│   │   ├── Navbar.vue       # ナビゲーション
│   │   ├── Home.vue         # ホーム画面
│   │   ├── Quiz.vue         # クイズ画面
│   │   ├── Login.vue        # ログイン
│   │   ├── Register.vue     # ユーザー登録
│   │   ├── Profile.vue      # プロフィール
│   │   ├── History.vue      # 履歴
│   │   ├── Leaderboard.vue  # リーダーボード
│   │   ├── About.vue        # アバウト
│   │   ├── Contact.vue      # お問い合わせ
│   │   └── PrivacyPolicy.vue # プライバシーポリシー
│   ├── router/              # ルーティング
│   │   └── index.js
│   ├── store/               # Vuex状態管理
│   │   ├── index.js         # ストア設定
│   │   └── modules/
│   │       ├── auth.js      # 認証モジュール
│   │       ├── quiz.js      # クイズモジュール
│   │       └── user.js      # ユーザーモジュール
│   └── utils/
│       └── api.js           # API通信設定
├── package.json
├── babel.config.js
└── vue.config.js
```

### コンポーネント階層

```
App.vue
├── Navbar.vue (常に表示)
└── <router-view> (動的コンポーネント)
    ├── Home.vue
    ├── Quiz.vue
    ├── Login.vue
    ├── Register.vue
    ├── Profile.vue
    ├── History.vue
    ├── Leaderboard.vue
    ├── About.vue
    ├── Contact.vue
    └── PrivacyPolicy.vue
```

### Vuex ストア構造

```javascript
store/
├── index.js (root store)
└── modules/
    ├── auth.js
    │   ├── state: { token, refreshToken, user }
    │   ├── mutations: { SET_TOKEN, SET_USER, LOGOUT }
    │   ├── actions: { login, logout, refresh }
    │   └── getters: { isAuthenticated, currentUser }
    │
    ├── quiz.js
    │   ├── state: { categories, questions, currentQuiz }
    │   ├── mutations: { SET_CATEGORIES, SET_QUESTIONS }
    │   ├── actions: { fetchCategories, fetchQuestions }
    │   └── getters: { allCategories, quizQuestions }
    │
    └── user.js
        ├── state: { profile, stats, history }
        ├── mutations: { SET_PROFILE, SET_STATS }
        ├── actions: { fetchProfile, fetchStats }
        └── getters: { userProfile, userStats }
```

### ルーティング設定

```javascript
routes: [
  { path: '/', component: Home },
  { path: '/quiz', component: Quiz, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/history', component: History, meta: { requiresAuth: true } },
  { path: '/leaderboard', component: Leaderboard },
  // ...
]
```

## データフロー

### クイズ受験フロー

```
┌──────────────┐
│   ユーザー    │
└──────┬───────┘
       │ 1. カテゴリ選択
       ▼
┌──────────────────────────────────┐
│  Home.vue                         │
│  - カテゴリ一覧表示                │
│  - GET /api/categories/          │
└──────┬───────────────────────────┘
       │ 2. クイズ開始
       ▼
┌──────────────────────────────────┐
│  Quiz.vue                         │
│  - 問題取得                        │
│  - GET /api/questions/           │
│    session_questions/            │
│    ?category=X&limit=10          │
└──────┬───────────────────────────┘
       │ 3. 回答
       ▼
┌──────────────────────────────────┐
│  Quiz.vue (State Management)     │
│  - 回答を保存                      │
│  - 次の問題へ                      │
│  - スコア計算                      │
└──────┬───────────────────────────┘
       │ 4. 結果送信
       ▼
┌──────────────────────────────────┐
│  POST /api/quiz/save-result/     │
│  {                               │
│    category_id: X,               │
│    score: Y,                     │
│    responses: [...]              │
│  }                               │
└──────┬───────────────────────────┘
       │ 5. 結果表示
       ▼
┌──────────────────────────────────┐
│  Quiz.vue (Result Display)       │
│  - スコア表示                      │
│  - 正解/不正解の詳細               │
│  - 再挑戦オプション                │
└──────────────────────────────────┘
```

### 認証フロー

```
┌─────────────┐
│ Login.vue   │
└──────┬──────┘
       │ POST /api/token/
       │ { username, password }
       ▼
┌──────────────────────────────────┐
│  Django Backend                   │
│  - ユーザー認証                    │
│  - JWTトークン生成                 │
└──────┬───────────────────────────┘
       │ { access, refresh }
       ▼
┌──────────────────────────────────┐
│  Vuex Store (auth module)        │
│  - トークン保存                    │
│  - localStorage保存               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Axios Interceptor               │
│  - 全リクエストにトークン付与       │
│  - Header: Authorization         │
└──────────────────────────────────┘
```

### データ取得フロー（例: ユーザー統計）

```
Component (Profile.vue)
    │
    │ dispatch('user/fetchStats')
    ▼
Vuex Action (user.js)
    │
    │ axios.get('/api/user/stats/')
    ▼
API Utils (api.js)
    │
    │ + Authorization Header
    ▼
Django Backend
    │
    │ UserStatsView.get()
    ▼
Database Query
    │
    │ QuizAttempt集計
    ▼
Serializer (UserStatsSerializer)
    │
    │ JSON変換
    ▼
API Response
    │
    │ { total_attempts, avg_percentage, ... }
    ▼
Vuex Mutation
    │
    │ commit('SET_STATS', data)
    ▼
Component Re-render
```

## セキュリティ設計

### 認証・認可

```
┌─────────────────────────────────────────────────┐
│            認証レイヤー                          │
├─────────────────────────────────────────────────┤
│  JWT (JSON Web Token)                           │
│  - Access Token: 1日有効                        │
│  - Refresh Token: 7日有効                       │
│  - トークンベース認証（ステートレス）             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│            認可レイヤー                          │
├─────────────────────────────────────────────────┤
│  DRF Permission Classes:                        │
│  - IsAuthenticated: 認証必須エンドポイント       │
│  - AllowAny: 公開エンドポイント                 │
│  - IsAdminUser: 管理者専用                      │
└─────────────────────────────────────────────────┘
```

### CORS (Cross-Origin Resource Sharing)

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # 開発環境
]

# 本番環境では実際のドメインを設定
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
]
```

### CSRF保護

- REST APIではトークンベース認証を使用
- セッションベース認証ではCSRFトークン必須

### データ保護

```python
# パスワードハッシュ化
AUTH_PASSWORD_VALIDATORS = [
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',
]
```

### 入力検証

- シリアライザレベルでのバリデーション
- モデルレベルでのバリデーション
- フロントエンドでの基本検証

## スケーラビリティ考慮

### 水平スケーリング

```
Load Balancer
    │
    ├─── Frontend Server 1 (Vue.js)
    ├─── Frontend Server 2 (Vue.js)
    └─── Frontend Server N

    ├─── Backend Server 1 (Django)
    ├─── Backend Server 2 (Django)
    └─── Backend Server N
         │
         └─── Database (PostgreSQL)
              - Read Replicas
```

### キャッシュ戦略

```
Redis Cache
├── カテゴリ一覧 (TTL: 1時間)
├── 問題データ (TTL: 30分)
└── リーダーボード (TTL: 5分)
```

### データベース最適化

- インデックス設定
- クエリ最適化（N+1問題対策）
- コネクションプーリング
- 読み取りレプリカの活用

## 監視・ロギング

### ログレベル

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'quiz_api': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

### メトリクス監視

- APIレスポンスタイム
- エラー率
- ユーザー数
- クイズ受験数

## 今後の拡張性

### 検討可能な機能追加

1. **リアルタイム機能**: WebSocketを使用したリアルタイムクイズ
2. **マルチメディア対応**: 動画・音声問題
3. **AI機能**: 難易度自動調整、パーソナライズ出題
4. **ソーシャル機能**: 友達対戦、グループクイズ
5. **ゲーミフィケーション**: バッジ、実績、レベルシステム

### 技術的改善

1. **GraphQL API**: RESTからGraphQLへの移行
2. **マイクロサービス化**: 機能ごとのサービス分割
3. **コンテナ化**: Docker, Kubernetes
4. **CI/CD**: 自動テスト・デプロイパイプライン

---

このアーキテクチャドキュメントは、システムの全体像を理解するための重要な資料です。新しいメンバーのオンボーディングや、機能追加時の設計判断に活用してください。
