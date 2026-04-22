# API ドキュメント

このドキュメントでは、クイズアプリケーションのREST APIの詳細仕様を説明します。

## 📋 目次

- [API概要](#api概要)
- [認証](#認証)
- [エンドポイント一覧](#エンドポイント一覧)
- [認証API](#認証api)
- [カテゴリAPI](#カテゴリapi)
- [問題API](#問題api)
- [クイズAPI](#クイズapi)
- [ユーザーAPI](#ユーザーapi)
- [エラーレスポンス](#エラーレスポンス)

## API概要

### ベースURL

```
開発環境: http://localhost:8000/api/
本番環境: https://your-domain.com/api/
```

### レスポンス形式

すべてのレスポンスはJSON形式です。

```json
{
  "data": {...},
  "status": "success",
  "message": "操作が成功しました"
}
```

### HTTPステータスコード

| コード | 説明 |
|--------|------|
| 200 | OK - リクエスト成功 |
| 201 | Created - リソース作成成功 |
| 204 | No Content - 削除成功 |
| 400 | Bad Request - リクエストが不正 |
| 401 | Unauthorized - 認証が必要 |
| 403 | Forbidden - アクセス権限なし |
| 404 | Not Found - リソースが存在しない |
| 500 | Internal Server Error - サーバーエラー |

## 認証

### JWT認証

このAPIはJWT (JSON Web Token) を使用した認証を採用しています。

#### トークンの種類

1. **Access Token**: API呼び出しに使用（有効期限: 24時間）
2. **Refresh Token**: Access Tokenの更新に使用（有効期限: 7日間）

#### 認証ヘッダー

```http
Authorization: Bearer <access_token>
```

#### 認証が不要なエンドポイント

- `POST /api/register/` - ユーザー登録
- `POST /api/token/` - ログイン
- `POST /api/token/refresh/` - トークン更新
- `GET /api/categories/` - カテゴリ一覧
- `GET /api/questions/` - 問題一覧（一部）

## エンドポイント一覧

### 認証

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/api/register/` | ユーザー登録 | 不要 |
| POST | `/api/token/` | ログイン | 不要 |
| POST | `/api/token/refresh/` | トークン更新 | 不要 |

### カテゴリ

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/api/categories/` | カテゴリ一覧 | 不要 |
| GET | `/api/categories/{id}/` | カテゴリ詳細 | 不要 |

### 問題

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/api/questions/` | 問題一覧 | 不要 |
| GET | `/api/questions/{id}/` | 問題詳細 | 不要 |
| GET | `/api/questions/random_questions/` | ランダム問題取得 | 不要 |
| GET | `/api/questions/unique_random/` | 重複なしランダム | 不要 |
| GET | `/api/questions/session_questions/` | セッション管理型 | 不要 |
| GET | `/api/questions/quiz_session/` | クイズセッション | 任意 |

### クイズ

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/api/quiz/save-result/` | 結果保存 | 必要 |
| GET | `/api/quiz/history/` | 履歴一覧 | 必要 |
| GET | `/api/quiz/attempt/{id}/` | 履歴詳細 | 必要 |
| GET | `/api/quiz/leaderboard/` | リーダーボード | 必要 |

### ユーザー

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/api/user/profile/` | プロフィール取得 | 必要 |
| GET | `/api/user/stats/` | 統計情報取得 | 必要 |

---

## 認証API

### ユーザー登録

新規ユーザーを登録します。

**エンドポイント**: `POST /api/register/`

**リクエストボディ**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securePassword123",
  "password2": "securePassword123"
}
```

**レスポンス** (201 Created):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "message": "ユーザー登録が完了しました"
}
```

**バリデーション**:
- `username`: 必須、ユニーク、150文字以内
- `email`: 必須、有効なメールアドレス
- `password`: 必須、8文字以上
- `password2`: passwordと一致する必要あり

---

### ログイン（トークン取得）

ログインしてJWTトークンを取得します。

**エンドポイント**: `POST /api/token/`

**リクエストボディ**:
```json
{
  "username": "testuser",
  "password": "securePassword123"
}
```

**レスポンス** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**エラー** (401 Unauthorized):
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### トークン更新

Refresh Tokenを使用してAccess Tokenを更新します。

**エンドポイント**: `POST /api/token/refresh/`

**リクエストボディ**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**レスポンス** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## カテゴリAPI

### カテゴリ一覧取得

すべてのカテゴリを取得します。

**エンドポイント**: `GET /api/categories/`

**クエリパラメータ**: なし

**レスポンス** (200 OK):
```json
[
  {
    "id": 1,
    "name": "プログラミング",
    "questions_count": 50
  },
  {
    "id": 2,
    "name": "データベース",
    "questions_count": 30
  }
]
```

---

### カテゴリ詳細取得

特定のカテゴリの詳細を取得します。

**エンドポイント**: `GET /api/categories/{id}/`

**レスポンス** (200 OK):
```json
{
  "id": 1,
  "name": "プログラミング",
  "questions_count": 50
}
```

---

## 問題API

### 問題一覧取得

問題一覧を取得します。

**エンドポイント**: `GET /api/questions/`

**クエリパラメータ**:
| パラメータ | 型 | 説明 | デフォルト |
|-----------|----|----|-----------|
| `category` | integer | カテゴリID | - |
| `limit` | integer | 取得件数 | - |
| `random` | boolean | ランダム順 | true (カテゴリ指定時) |
| `order` | string | 並び順 (id) | - |

**例**: `GET /api/questions/?category=1&limit=10`

**レスポンス** (200 OK):
```json
[
  {
    "id": 1,
    "category": {
      "id": 1,
      "name": "プログラミング"
    },
    "text": "Pythonの基本的なデータ型はどれですか？",
    "image": null,
    "choices": [
      {
        "id": 1,
        "text": "int, str, list",
        "is_correct": true
      },
      {
        "id": 2,
        "text": "number, text, array",
        "is_correct": false
      }
    ]
  }
]
```

---

### ランダム問題取得

ランダムに問題を取得します（基本版）。

**エンドポイント**: `GET /api/questions/random_questions/`

**クエリパラメータ**:
| パラメータ | 型 | 説明 | デフォルト |
|-----------|----|----|-----------|
| `category` | integer/string | カテゴリID または 'all' | all |
| `limit` | integer | 取得件数（最大50） | 10 |
| `exclude` | string | 除外する問題ID（カンマ区切り） | - |

**例**: `GET /api/questions/random_questions/?category=1&limit=10&exclude=1,2,3`

**レスポンス** (200 OK):
```json
{
  "count": 10,
  "results": [
    {
      "id": 5,
      "category": {...},
      "text": "問題文",
      "image": null,
      "choices": [...]
    }
  ],
  "message": "10問の問題をランダムに取得しました"
}
```

---

### 重複なしランダム問題取得

完全に重複のないランダム問題を取得します（シード対応）。

**エンドポイント**: `GET /api/questions/unique_random/`

**クエリパラメータ**:
| パラメータ | 型 | 説明 | デフォルト |
|-----------|----|----|-----------|
| `category` | integer/string | カテゴリID または 'all' | all |
| `limit` | integer | 取得件数（最大50） | 10 |
| `seed` | integer/string | ランダムシード値（再現性） | - |

**例**: `GET /api/questions/unique_random/?category=1&limit=10&seed=12345`

**レスポンス** (200 OK):
```json
{
  "count": 10,
  "results": [...],
  "total_available": 50,
  "message": "10問の問題をランダムに取得しました（重複なし保証）"
}
```

**特徴**:
- Pythonの`random.sample()`を使用した完全ランダム選択
- 同じseedで再現可能
- N+1問題対策済み（select_related, prefetch_related）

---

### セッション管理型問題取得

セッションを使用して重複を完全に排除します。

**エンドポイント**: `GET /api/questions/session_questions/`

**クエリパラメータ**:
| パラメータ | 型 | 説明 | デフォルト |
|-----------|----|----|-----------|
| `category` | integer/string | カテゴリID または 'all' | all |
| `limit` | integer | 取得件数（最大20） | 10 |
| `session_id` | string | セッションID | 自動生成 |
| `reset` | boolean | セッションリセット | false |

**例**: `GET /api/questions/session_questions/?category=1&limit=10&session_id=quiz_abc123`

**レスポンス** (200 OK):
```json
{
  "count": 10,
  "results": [...],
  "session_id": "quiz_abc123",
  "total_available": 50,
  "used_count": 10,
  "remaining": 40,
  "message": "10問の問題を取得しました（セッション管理による重複なし保証）"
}
```

**動作**:
1. 初回: `session_id`を生成、問題を返す
2. 2回目以降: 同じ`session_id`で使用済み問題を除外
3. 全問出題済み: 自動リセットして最初から
4. 手動リセット: `reset=true`でセッションクリア

---

### クイズセッション（最近の除外機能付き）

最近出題された問題を除外して取得します。

**エンドポイント**: `GET /api/questions/quiz_session/`

**クエリパラメータ**:
| パラメータ | 型 | 説明 | デフォルト |
|-----------|----|----|-----------|
| `category` | integer/string | カテゴリID または 'all' | all |
| `count` | integer | 取得件数（最大20） | 10 |
| `session_id` | string | セッションID | 自動生成 |
| `exclude_recent` | boolean | 最近の問題を除外 | true |

**例**: `GET /api/questions/quiz_session/?category=1&count=10&exclude_recent=true`

**レスポンス** (200 OK):
```json
{
  "count": 10,
  "results": [...],
  "session_id": "session_1234",
  "total_available": 45,
  "message": "10問の問題を取得しました（利用可能: 45問）"
}
```

**特徴**:
- 認証ユーザー: 過去1時間以内の出題を除外
- ゲストユーザー: 通常のランダム出題

---

## クイズAPI

### クイズ結果保存

クイズの結果を保存します。

**エンドポイント**: `POST /api/quiz/save-result/`

**認証**: 必要

**リクエストボディ**:
```json
{
  "category_id": 1,
  "score": 8,
  "total_questions": 10,
  "percentage": 80.0,
  "responses": [
    {
      "question_id": 1,
      "selected_choice_id": 2,
      "is_correct": true
    },
    {
      "question_id": 2,
      "selected_choice_id": 5,
      "is_correct": false
    }
  ]
}
```

**レスポンス** (201 Created):
```json
{
  "id": 123,
  "user": {
    "id": 1,
    "username": "testuser"
  },
  "category": {
    "id": 1,
    "name": "プログラミング"
  },
  "score": 8,
  "total_questions": 10,
  "percentage": 80.0,
  "created_at": "2025-01-15T10:30:00Z",
  "responses": [...]
}
```

**バリデーション**:
- `category_id`: 存在するカテゴリID
- `score`: 0以上、total_questions以下
- `responses`: 各問題に対する回答（question_id, selected_choice_id, is_correct）

---

### クイズ履歴一覧

自分のクイズ履歴一覧を取得します。

**エンドポイント**: `GET /api/quiz/history/`

**認証**: 必要

**クエリパラメータ**:
| パラメータ | 型 | 説明 |
|-----------|----|----|
| `page` | integer | ページ番号 |

**レスポンス** (200 OK):
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/quiz/history/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "category": {
        "id": 1,
        "name": "プログラミング"
      },
      "score": 8,
      "total_questions": 10,
      "percentage": 80.0,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

### クイズ履歴詳細

特定のクイズ結果の詳細を取得します。

**エンドポイント**: `GET /api/quiz/attempt/{id}/`

**認証**: 必要

**レスポンス** (200 OK):
```json
{
  "id": 123,
  "user": {
    "id": 1,
    "username": "testuser"
  },
  "category": {
    "id": 1,
    "name": "プログラミング"
  },
  "score": 8,
  "total_questions": 10,
  "percentage": 80.0,
  "created_at": "2025-01-15T10:30:00Z",
  "responses": [
    {
      "id": 1,
      "question": {
        "id": 1,
        "text": "Pythonの基本的なデータ型は？",
        "category": {...}
      },
      "selected_choice": {
        "id": 2,
        "text": "int, str, list",
        "is_correct": true
      },
      "is_correct": true
    }
  ]
}
```

---

### リーダーボード

全ユーザーのランキングを取得します。

**エンドポイント**: `GET /api/quiz/leaderboard/`

**認証**: 必要

**クエリパラメータ**:
| パラメータ | 型 | 説明 |
|-----------|----|----|
| `category` | integer/string | カテゴリID または 'all' |

**例**: `GET /api/quiz/leaderboard/?category=1`

**レスポンス** (200 OK):
```json
[
  {
    "id": 1,
    "username": "topuser",
    "total_attempts": 50,
    "total_score": 450,
    "total_questions": 500,
    "avg_percentage": 90.0
  },
  {
    "id": 2,
    "username": "seconduser",
    "total_attempts": 40,
    "total_score": 340,
    "total_questions": 400,
    "avg_percentage": 85.0
  }
]
```

**ソート**: `avg_percentage` 降順

---

## ユーザーAPI

### プロフィール取得

ログイン中のユーザー情報を取得します。

**エンドポイント**: `GET /api/user/profile/`

**認証**: 必要

**レスポンス** (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "date_joined": "2025-01-01T00:00:00Z"
}
```

---

### ユーザー統計取得

ユーザーのクイズ統計情報を取得します。

**エンドポイント**: `GET /api/user/stats/`

**認証**: 必要

**レスポンス** (200 OK):
```json
{
  "total_attempts": 25,
  "total_categories_played": 5,
  "best_category": "プログラミング",
  "avg_percentage": 82.5,
  "category_stats": [
    {
      "id": 1,
      "name": "プログラミング",
      "attempts_count": 10,
      "best_score": 10,
      "avg_percentage": 85.0
    },
    {
      "id": 2,
      "name": "データベース",
      "attempts_count": 8,
      "best_score": 9,
      "avg_percentage": 80.0
    }
  ]
}
```

**統計項目**:
- `total_attempts`: 総受験回数
- `total_categories_played`: プレイしたカテゴリ数
- `best_category`: 平均正解率が最も高いカテゴリ
- `avg_percentage`: 全体の平均正解率
- `category_stats`: カテゴリ別の詳細統計

---

## エラーレスポンス

### 共通エラー形式

```json
{
  "detail": "エラーメッセージ"
}
```

または

```json
{
  "field_name": [
    "エラーメッセージ1",
    "エラーメッセージ2"
  ]
}
```

### エラーコード例

#### 400 Bad Request

```json
{
  "password": [
    "このパスワードは短すぎます。最低 8 文字以上必要です。"
  ],
  "username": [
    "この項目は必須です。"
  ]
}
```

#### 401 Unauthorized

```json
{
  "detail": "認証情報が含まれていません。"
}
```

または

```json
{
  "detail": "認証トークンが無効です。"
}
```

#### 403 Forbidden

```json
{
  "detail": "この操作を実行する権限がありません。"
}
```

#### 404 Not Found

```json
{
  "detail": "見つかりませんでした。"
}
```

#### 500 Internal Server Error

```json
{
  "detail": "サーバーエラーが発生しました。"
}
```

---

## レート制限

現在、レート制限は実装されていませんが、本番環境では以下の制限を推奨します:

```
認証済みユーザー: 100リクエスト/分
未認証ユーザー: 20リクエスト/分
```

---

## ページネーション

リスト取得APIは自動的にページネーションされます。

**デフォルト設定**:
- 1ページあたり10件
- `page`パラメータでページ指定

**レスポンス形式**:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## APIバージョニング

現在はバージョニングなし（v1相当）。将来的に以下の形式を検討:

```
/api/v1/...
/api/v2/...
```

---

## CORS設定

開発環境では`http://localhost:8080`からのリクエストを許可しています。

本番環境では適切なドメインを設定してください。

---

## Postmanコレクション

このAPIのPostmanコレクションは[こちら](./postman_collection.json)からダウンロードできます（作成予定）。

---

## サンプルコード

### JavaScript (Axios)

```javascript
// ログイン
const login = async (username, password) => {
  const response = await axios.post('http://localhost:8000/api/token/', {
    username,
    password
  });
  return response.data;
};

// 問題取得
const getQuestions = async (categoryId, token) => {
  const response = await axios.get(
    'http://localhost:8000/api/questions/session_questions/',
    {
      params: { category: categoryId, limit: 10 },
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};

// 結果保存
const saveResult = async (resultData, token) => {
  const response = await axios.post(
    'http://localhost:8000/api/quiz/save-result/',
    resultData,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};
```

### Python (requests)

```python
import requests

# ログイン
def login(username, password):
    response = requests.post(
        'http://localhost:8000/api/token/',
        json={'username': username, 'password': password}
    )
    return response.json()

# 問題取得
def get_questions(category_id, token):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'category': category_id, 'limit': 10}
    response = requests.get(
        'http://localhost:8000/api/questions/session_questions/',
        headers=headers,
        params=params
    )
    return response.json()

# 結果保存
def save_result(result_data, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://localhost:8000/api/quiz/save-result/',
        headers=headers,
        json=result_data
    )
    return response.json()
```

---

このAPIドキュメントは、システムの保守・拡張時に重要な参考資料となります。新しいエンドポイントを追加した場合は、必ずこのドキュメントも更新してください。
