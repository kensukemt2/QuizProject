# データベーススキーマ

このドキュメントでは、クイズアプリケーションのデータベース設計とスキーマについて詳しく説明します。

## 📋 目次

- [データベース概要](#データベース概要)
- [ER図](#er図)
- [テーブル定義](#テーブル定義)
- [リレーション](#リレーション)
- [インデックス](#インデックス)
- [制約](#制約)
- [マイグレーション履歴](#マイグレーション履歴)

## データベース概要

### 使用データベース

- **開発環境**: SQLite 3
- **本番環境推奨**: PostgreSQL 12+ または MySQL 8+

### 文字エンコーディング

- **SQLite**: UTF-8
- **PostgreSQL**: UTF-8
- **MySQL**: utf8mb4

### タイムゾーン設定

```python
# settings.py
USE_TZ = True
TIME_ZONE = 'UTC'
```

すべての日時データはUTCで保存され、アプリケーション層で変換されます。

## ER図

### 全体構成

```
┌─────────────────┐
│      User       │ Django標準
│   (auth_user)   │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────────────┐
│      QuizAttempt            │
│   (quiz_api_quizattempt)    │
└────────┬────────────────────┘
         │ 1
         │
         │ N
┌────────▼────────────────────┐
│   QuestionResponse          │
│(quiz_api_questionresponse)  │
└────────┬────────────────────┘
         │
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│    Question     │ N  1 │    Category     │
│(quiz_api_question)│◄────┤(quiz_api_category)│
└────────┬────────┘      └─────────────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│     Choice      │
│(quiz_api_choice)│
└─────────────────┘

┌─────────────────────────────┐
│      QuizSession            │
│ (quiz_api_quiz_session)     │
│         (M:N)               │
│  ├─ Question (M:N)          │
│  └─ User (Optional)         │
└─────────────────────────────┘
```

### リレーション詳細図

```
User (Django標準)
  ├── QuizAttempt (1:N)
  └── QuizSession (1:N, optional)

Category
  └── Question (1:N)

Question
  ├── Choice (1:N)
  ├── QuestionResponse (1:N)
  └── QuizSession (M:N)

QuizAttempt
  └── QuestionResponse (1:N)

Choice
  └── QuestionResponse (1:N)
```

## テーブル定義

### 1. auth_user (Django標準)

Djangoの組み込みユーザーモデル。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | ユーザーID |
| username | VARCHAR(150) | UNIQUE, NOT NULL | ユーザー名 |
| email | VARCHAR(254) | NOT NULL | メールアドレス |
| password | VARCHAR(128) | NOT NULL | ハッシュ化パスワード |
| first_name | VARCHAR(150) | | 名 |
| last_name | VARCHAR(150) | | 姓 |
| is_staff | BOOLEAN | DEFAULT FALSE | スタッフ権限 |
| is_active | BOOLEAN | DEFAULT TRUE | アクティブ状態 |
| is_superuser | BOOLEAN | DEFAULT FALSE | 管理者権限 |
| date_joined | DATETIME | NOT NULL | 登録日時 |
| last_login | DATETIME | NULL | 最終ログイン日時 |

**インデックス**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `username`

---

### 2. quiz_api_category

クイズのカテゴリ。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | カテゴリID |
| name | VARCHAR(100) | NOT NULL | カテゴリ名 |

**モデル定義**:
```python
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
```

**インデックス**:
- PRIMARY KEY: `id`

**デフォルトソート**: `name` 昇順

---

### 3. quiz_api_question

クイズの問題。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | 問題ID |
| category_id | INTEGER | FK, NOT NULL | カテゴリID |
| text | VARCHAR(500) | NOT NULL | 問題文 |
| image | VARCHAR(100) | NULL | 画像パス |

**モデル定義**:
```python
class Question(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(max_length=500)
    image = models.ImageField(
        upload_to='question_images/',
        blank=True,
        null=True
    )
```

**インデックス**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `category_id` → `quiz_api_category.id`

**関連名**:
- `category.questions` - カテゴリから問題を取得

**削除時の動作**:
- カテゴリが削除されると、関連する問題も削除される（CASCADE）

---

### 4. quiz_api_choice

問題の選択肢。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | 選択肢ID |
| question_id | INTEGER | FK, NOT NULL | 問題ID |
| text | VARCHAR(200) | NOT NULL | 選択肢テキスト |
| is_correct | BOOLEAN | DEFAULT FALSE | 正解フラグ |

**モデル定義**:
```python
class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
```

**インデックス**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `question_id` → `quiz_api_question.id`

**関連名**:
- `question.choices` - 問題から選択肢を取得

**削除時の動作**:
- 問題が削除されると、関連する選択肢も削除される（CASCADE）

**制約**:
- 各問題には少なくとも2つの選択肢が必要（アプリケーションレベル）
- 各問題には1つだけ正解がある（アプリケーションレベル）

---

### 5. quiz_api_quizattempt

クイズの受験記録。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | 受験ID |
| user_id | INTEGER | FK, NOT NULL | ユーザーID |
| category_id | INTEGER | FK, NOT NULL | カテゴリID |
| score | INTEGER | NOT NULL | 正解数 |
| total_questions | INTEGER | NOT NULL | 総問題数 |
| percentage | FLOAT | NOT NULL | 正解率(%) |
| created_at | DATETIME | NOT NULL | 受験日時 |

**モデル定義**:
```python
class QuizAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

**インデックス**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `auth_user.id`
- FOREIGN KEY: `category_id` → `quiz_api_category.id`

**デフォルトソート**: `created_at` 降順（新しい順）

**関連名**:
- `user.quiz_attempts` - ユーザーの受験履歴
- `category.quizattempt_set` - カテゴリの受験履歴

**削除時の動作**:
- ユーザーが削除されると、受験記録も削除される（CASCADE）
- カテゴリが削除されると、受験記録も削除される（CASCADE）

---

### 6. quiz_api_questionresponse

各問題への回答記録。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | 回答ID |
| quiz_attempt_id | INTEGER | FK, NOT NULL | 受験ID |
| question_id | INTEGER | FK, NOT NULL | 問題ID |
| selected_choice_id | INTEGER | FK, NOT NULL | 選択した選択肢ID |
| is_correct | BOOLEAN | NOT NULL | 正解フラグ |

**モデル定義**:
```python
class QuestionResponse(models.Model):
    quiz_attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE
    )
    is_correct = models.BooleanField()
```

**インデックス**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `quiz_attempt_id` → `quiz_api_quizattempt.id`
- FOREIGN KEY: `question_id` → `quiz_api_question.id`
- FOREIGN KEY: `selected_choice_id` → `quiz_api_choice.id`

**関連名**:
- `quiz_attempt.responses` - 受験の全回答
- `question.questionresponse_set` - 問題への全回答
- `choice.questionresponse_set` - 選択肢が選ばれた回数

**削除時の動作**:
- QuizAttemptが削除されると、回答記録も削除される（CASCADE）
- Question/Choiceが削除されると、回答記録も削除される（CASCADE）

---

### 7. quiz_api_quiz_session

セッション管理（重複なし出題用）。

| カラム名 | 型 | 制約 | 説明 |
|---------|----|----|------|
| id | INTEGER | PK, AUTO_INCREMENT | セッションID |
| session_id | VARCHAR(100) | UNIQUE, NOT NULL | セッション識別子 |
| user_id | INTEGER | FK, NULL | ユーザーID（任意） |
| category_id | INTEGER | FK, NULL | カテゴリID（任意） |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**モデル定義**:
```python
class QuizSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    used_questions = models.ManyToManyField(
        Question,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quiz_api_quiz_session'
```

**インデックス**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `session_id`
- FOREIGN KEY: `user_id` → `auth_user.id`
- FOREIGN KEY: `category_id` → `quiz_api_category.id`

**中間テーブル** (quiz_api_quiz_session_used_questions):
| カラム名 | 型 | 制約 |
|---------|----|----|
| id | INTEGER | PK, AUTO_INCREMENT |
| quizsession_id | INTEGER | FK, NOT NULL |
| question_id | INTEGER | FK, NOT NULL |

**用途**:
- セッションごとに出題済み問題を追跡
- 重複なし出題を保証
- ゲストユーザーもセッションID文字列で管理可能

---

## リレーション

### 1. User → QuizAttempt (1:N)

```python
user = User.objects.get(id=1)
attempts = user.quiz_attempts.all()  # ユーザーの全受験記録
```

### 2. Category → Question (1:N)

```python
category = Category.objects.get(id=1)
questions = category.questions.all()  # カテゴリの全問題
```

### 3. Question → Choice (1:N)

```python
question = Question.objects.get(id=1)
choices = question.choices.all()  # 問題の全選択肢
correct = question.choices.filter(is_correct=True).first()  # 正解
```

### 4. QuizAttempt → QuestionResponse (1:N)

```python
attempt = QuizAttempt.objects.get(id=1)
responses = attempt.responses.all()  # 受験の全回答
correct_count = attempt.responses.filter(is_correct=True).count()
```

### 5. QuizSession ← → Question (M:N)

```python
session = QuizSession.objects.get(session_id='abc123')
used = session.used_questions.all()  # 出題済み問題
session.used_questions.add(question)  # 問題を追加
```

## インデックス

### 自動生成されるインデックス

Django ORMが自動的に作成するインデックス:

1. すべてのPRIMARY KEY
2. すべてのFOREIGN KEY
3. すべてのUNIQUE制約

### 推奨する追加インデックス（パフォーマンス向上）

本番環境で大量データを扱う場合、以下のインデックスを追加推奨:

```sql
-- QuizAttemptの検索高速化
CREATE INDEX idx_quizattempt_user_category
ON quiz_api_quizattempt(user_id, category_id);

CREATE INDEX idx_quizattempt_created
ON quiz_api_quizattempt(created_at DESC);

-- QuestionResponseの集計高速化
CREATE INDEX idx_questionresponse_quiz_attempt
ON quiz_api_questionresponse(quiz_attempt_id);

CREATE INDEX idx_questionresponse_is_correct
ON quiz_api_questionresponse(is_correct);

-- Questionの検索高速化
CREATE INDEX idx_question_category
ON quiz_api_question(category_id);

-- QuizSessionの検索高速化
CREATE INDEX idx_quizsession_session_id
ON quiz_api_quiz_session(session_id);
```

Django Migrationでの追加方法:

```python
# migrations/XXXX_add_indexes.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('quiz_api', 'previous_migration'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(
                fields=['user', 'category'],
                name='idx_quizattempt_user_category'
            ),
        ),
    ]
```

## 制約

### NOT NULL制約

以下のカラムはNULL不可:
- すべてのPRIMARY KEY
- すべてのFOREIGN KEY（user_id, category_idなど例外あり）
- `text`, `name`などのコンテンツカラム
- `is_correct`, `score`などの値カラム

### UNIQUE制約

- `auth_user.username` - ユーザー名の重複不可
- `quiz_api_quiz_session.session_id` - セッションIDの重複不可

### CHECK制約（アプリケーションレベル）

以下の制約はDjangoモデル/シリアライザで検証:

```python
# QuizAttempt
- score >= 0
- score <= total_questions
- total_questions > 0
- percentage >= 0.0
- percentage <= 100.0

# Question
- 最低2つの選択肢が必要
- 1つの正解が必要

# Choice
- is_correctはTrue/False
```

### 外部キー制約

すべての外部キーは`CASCADE`削除を使用:

```python
on_delete=models.CASCADE
```

これにより、親レコード削除時に子レコードも自動削除されます。

## マイグレーション履歴

### 初期マイグレーション

#### 0001_initial.py

初期モデルの作成:
- Category
- Question
- Choice

#### 0002_quizattempt_questionresponse.py

受験記録機能の追加:
- QuizAttempt
- QuestionResponse

#### 0003_quizattempt_quiz_api_qu_user_id_eed165_idx_and_more.py

インデックス追加（後に削除）

#### 0004_remove_quizattempt_quiz_api_qu_user_id_eed165_idx_and_more.py

インデックスの削除（シンプル化）

#### 0005_alter_category_options_question_image.py

- Category: orderingオプション追加
- Question: imageフィールド追加

#### 0006_quizsession.py

セッション管理機能の追加:
- QuizSession
- used_questions (M:N)

### マイグレーション実行方法

```bash
# マイグレーションファイル作成
python manage.py makemigrations

# マイグレーション実行
python manage.py migrate

# マイグレーション状態確認
python manage.py showmigrations

# 特定のマイグレーションに戻す
python manage.py migrate quiz_api 0005
```

## データベースバックアップ

### SQLiteのバックアップ

```bash
# バックアップ
cp db.sqlite3 db.sqlite3.backup

# 復元
cp db.sqlite3.backup db.sqlite3
```

### PostgreSQLのバックアップ

```bash
# バックアップ
pg_dump -U username dbname > backup.sql

# 復元
psql -U username dbname < backup.sql
```

## データベース最適化

### クエリ最適化

#### N+1問題の解決

```python
# 悪い例（N+1問題）
questions = Question.objects.all()
for q in questions:
    print(q.category.name)  # 各questionごとにクエリ実行

# 良い例
questions = Question.objects.select_related('category').all()
for q in questions:
    print(q.category.name)  # 1回のJOINで取得
```

#### 関連データの効率的な取得

```python
# 1:N, M:Nの関連取得
questions = Question.objects.prefetch_related('choices').all()

# 複合
questions = Question.objects\
    .select_related('category')\
    .prefetch_related('choices')\
    .all()
```

### VACUUM（SQLite）

```bash
# データベースの最適化
sqlite3 db.sqlite3 "VACUUM;"
```

### ANALYZE（統計情報更新）

```bash
# クエリプランナーの最適化
sqlite3 db.sqlite3 "ANALYZE;"
```

## データ整合性チェック

### 孤立レコードのチェック

```python
# 選択肢のない問題
Question.objects.annotate(
    choice_count=Count('choices')
).filter(choice_count=0)

# 正解のない問題
Question.objects.exclude(
    choices__is_correct=True
)

# 正解が複数ある問題
Question.objects.annotate(
    correct_count=Count('choices', filter=Q(choices__is_correct=True))
).filter(correct_count__gt=1)
```

### 統計情報の整合性チェック

```python
# スコアとパーセンテージの整合性
QuizAttempt.objects.exclude(
    percentage=(F('score') * 100.0 / F('total_questions'))
)
```

---

このデータベーススキーマドキュメントは、データベースの理解と保守に重要な資料です。スキーマ変更時は必ずこのドキュメントも更新してください。
