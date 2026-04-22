# テストドキュメント - マジカルクイズアプリケーション

## 📋 目次
1. [概要](#概要)
2. [テストの種類](#テストの種類)
3. [セットアップ](#セットアップ)
4. [テストの実行](#テストの実行)
5. [テストカバレッジ](#テストカバレッジ)
6. [テスト詳細](#テスト詳細)

---

## 概要

このドキュメントは、マジカルクイズアプリケーションの自動テストについて説明します。
バックエンド(Django)、フロントエンド(Vue.js)、および統合テストをカバーしています。

### テスト統計
- **総テスト数**: 24個
- **合格率**: 100%
- **実行時間**: 約20秒

---

## テストの種類

### 1. バックエンドテスト (Django)

#### モデルテスト
- **CategoryModelTest**: カテゴリーモデルの作成、順序
- **QuestionModelTest**: 問題モデルの作成、画像サポート
- **ChoiceModelTest**: 選択肢モデルの作成、複数選択肢
- **QuizAttemptModelTest**: クイズ結果の保存、文字列表現、順序
- **QuizSessionModelTest**: セッション作成、問題追跡

#### APIテスト
- **QuizAPITest**: カテゴリ一覧、問題一覧、フィルタリング、ユーザー登録
- **QuizResultAPITest**: 結果保存、履歴取得
- **AuthenticationTest**: 認証、トークン認証
- **LeaderboardAPITest**: リーダーボード全体表示、カテゴリフィルタリング、統計表示、ソート

### 2. API統合テスト
- カテゴリAPI (`/api/categories/`)
- リーダーボードAPI (`/api/quiz/leaderboard/`)
- 問題取得API (`/api/questions/session_questions/`)
- 認証エンドポイント

### 3. フロントエンドテスト
- ESLintコードチェック
- 本番ビルドテスト

---

## セットアップ

### 必要な環境
```bash
# Python 3.11+
# Node.js 14+
# Django 5.2.3
# Vue.js 3.2.13
```

### テストに必要なパッケージ
```bash
# バックエンド
pip install django djangorestframework djangorestframework-simplejwt
pip install coverage  # カバレッジ測定用 (オプション)

# フロントエンド
cd quiz-frontend
npm install
```

---

## テストの実行

### 🚀 すべてのテストを一括実行

```bash
# プロジェクトルートで実行
./run_tests.sh
```

このスクリプトは以下を自動実行します:
1. Djangoユニットテスト
2. コードカバレッジ測定 (coverageがインストールされている場合)
3. API統合テスト
4. ESLintチェック
5. 本番ビルドテスト

### バックエンドテストのみ実行

```bash
cd quiz_project
source ../venv/bin/activate
python manage.py test quiz_api.tests
```

#### 特定のテストクラスを実行
```bash
# リーダーボードテストのみ
python manage.py test quiz_api.tests.LeaderboardAPITest

# 特定のテストメソッド
python manage.py test quiz_api.tests.LeaderboardAPITest.test_leaderboard_category_filtering
```

#### 詳細出力
```bash
python manage.py test quiz_api.tests --verbosity=2
```

### フロントエンドテストのみ実行

```bash
cd quiz-frontend

# ESLint
npm run lint

# 本番ビルド
npm run build
```

### API統合テスト (手動)

サーバーが起動している状態で実行:

```bash
# カテゴリAPI
curl http://localhost:8000/api/categories/

# リーダーボード (全体)
curl "http://localhost:8000/api/quiz/leaderboard/?category=all"

# リーダーボード (カテゴリ別)
curl "http://localhost:8000/api/quiz/leaderboard/?category=1"

# 問題取得
curl "http://localhost:8000/api/questions/session_questions/?category=1&limit=5"
```

---

## テストカバレッジ

### カバレッジレポートの生成

```bash
cd quiz_project
source ../venv/bin/activate

# カバレッジ測定
coverage run --source='quiz_api' manage.py test quiz_api.tests

# レポート表示 (ターミナル)
coverage report

# HTMLレポート生成
coverage html
```

HTMLレポートは `quiz_project/htmlcov/index.html` に生成されます。

### 期待されるカバレッジ
- **Models**: 95%+
- **Views**: 90%+
- **Serializers**: 90%+
- **全体**: 85%+

---

## テスト詳細

### レジスタードテスト一覧

#### 1. CategoryModelTest (2テスト)
- `test_category_creation`: カテゴリーが正しく作成されるか
- `test_category_ordering`: カテゴリーが名前順にソートされるか

#### 2. QuestionModelTest (2テスト)
- `test_question_creation`: 問題が正しく作成されるか
- `test_question_with_image`: 画像付き問題が作成できるか

#### 3. ChoiceModelTest (2テスト)
- `test_choice_creation`: 選択肢が正しく作成されるか
- `test_multiple_choices`: 複数の選択肢が設定できるか

#### 4. QuizAttemptModelTest (3テスト)
- `test_quiz_attempt_creation`: クイズ結果が正しく保存されるか
- `test_quiz_attempt_string_representation`: 文字列表現が正しいか
- `test_quiz_attempt_ordering`: 新しい順にソートされるか

#### 5. QuizSessionModelTest (2テスト)
- `test_quiz_session_creation`: クイズセッションが作成できるか
- `test_quiz_session_track_questions`: 使用した問題を記録できるか

#### 6. QuizAPITest (4テスト)
- `test_category_list_api`: カテゴリー一覧APIが動作するか
- `test_question_list_api`: 問題一覧APIが動作するか
- `test_question_filter_by_category`: カテゴリーでフィルタリングできるか
- `test_user_registration`: ユーザー登録APIが動作するか

#### 7. QuizResultAPITest (2テスト)
- `test_save_quiz_result`: クイズ結果が保存できるか
- `test_user_quiz_history`: ユーザーのクイズ履歴が取得できるか

#### 8. AuthenticationTest (2テスト)
- `test_unauthenticated_access`: 未認証でのアクセスが拒否されるか
- `test_token_authentication`: トークン認証が正しく動作するか

#### 9. LeaderboardAPITest (5テスト) ⭐ 新規追加
- `test_public_leaderboard_all_categories`: 全カテゴリのリーダーボードが取得できるか
- `test_leaderboard_category_filtering`: カテゴリフィルタリングが正しく動作するか
- `test_leaderboard_shows_category_stats`: カテゴリ別統計が正しく表示されるか
- `test_leaderboard_different_categories`: 異なるカテゴリで異なる結果が返るか
- `test_leaderboard_ordering`: リーダーボードが正しくソートされているか

---

## テストデータ

テストでは以下のデータが自動生成されます:
- テストユーザー (user1, user2, user3, testuser)
- テストカテゴリ (Math, Science, Test Category)
- テスト問題と選択肢
- テストクイズ結果

全テストはテスト専用データベースで実行されるため、本番データには影響しません。

---

## CI/CD統合

### GitHub Actions設定例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11

    - name: Install dependencies
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

    - name: Run tests
      run: |
        cd quiz_project
        source ../venv/bin/activate
        python manage.py test quiz_api.tests
```

---

## トラブルシューティング

### よくある問題

#### 1. "Port already in use" エラー
サーバーが既に起動している場合:
```bash
pkill -f "manage.py runserver"
```

#### 2. データベースロックエラー
テスト用データベースをクリア:
```bash
rm quiz_project/db.sqlite3
python manage.py migrate
```

#### 3. テスト失敗時
詳細ログを確認:
```bash
python manage.py test quiz_api.tests --verbosity=2 --debug-mode
```

---

## ベストプラクティス

### テストを書く際のガイドライン

1. **各テストは独立させる**: テスト間で依存関係を持たせない
2. **セットアップとクリーンアップ**: `setUp()` と `tearDown()` を適切に使用
3. **明確な命名**: テスト名から何をテストしているか分かるように
4. **適切なアサーション**: `assertEqual`, `assertTrue`, `assertIn` などを使い分ける
5. **エッジケースもテスト**: 正常系だけでなく異常系もカバー

### テストを追加する手順

1. `quiz_project/quiz_api/tests.py` を開く
2. 適切なテストクラスを追加/編集
3. テストメソッドを追加 (メソッド名は `test_` で開始)
4. `setUp()` でテストデータを準備
5. テストを実行して確認
6. コミット前に全テストを実行

---

## 連絡先

テストに関する質問や問題があれば、開発チームに連絡してください。

**テストステータス**: ✅ すべて合格 (24/24)
**最終更新**: 2025-11-25
