# テスト自動化ガイド

このドキュメントでは、プロジェクトのテスト自動化について説明します。

## 📋 目次

1. [テストの実行](#テストの実行)
2. [カバレッジ測定](#カバレッジ測定)
3. [CI/CD](#cicd)
4. [テストの種類](#テストの種類)

---

## テストの実行

### 基本的なテスト実行

```bash
# すべてのテストを実行
python manage.py test

# 特定のアプリのみ
python manage.py test quiz_api

# 詳細出力
python manage.py test quiz_api --verbosity=2
```

### テストの内容

現在、以下の19個のテストが実装されています：

#### モデルテスト
- ✅ カテゴリーの作成と順序付け
- ✅ 問題の作成（画像付き含む）
- ✅ 選択肢の作成と正解判定
- ✅ クイズ結果の保存とソート
- ✅ クイズセッションの管理

#### APIテスト
- ✅ カテゴリー一覧API
- ✅ 問題一覧API
- ✅ 問題のカテゴリーフィルタリング
- ✅ ユーザー登録API
- ✅ クイズ結果保存API
- ✅ ユーザー統計API

#### 認証テスト
- ✅ 未認証アクセスの拒否
- ✅ JWT トークン認証

---

## カバレッジ測定

### カバレッジの実行

```bash
# カバレッジ付きでテストを実行
coverage run manage.py test quiz_api

# レポート表示
coverage report

# HTMLレポート生成
coverage html
```

### HTMLレポートの確認

```bash
# ブラウザでHTMLレポートを開く
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 現在のカバレッジ状況

| モジュール | カバレッジ |
|-----------|----------|
| モデル | 100% ✅ |
| シリアライザー | 95.79% |
| ビュー | 37.25% |
| **全体** | **42.58%** |

### カバレッジ設定

`.coveragerc` ファイルでカバレッジ測定の設定をカスタマイズできます：

```ini
[run]
source = quiz_api
omit =
    */migrations/*
    */tests.py
```

---

## CI/CD

### GitHub Actions

プロジェクトには GitHub Actions のワークフローが設定されています：

**ファイル**: `.github/workflows/django-tests.yml`

#### トリガー条件
- `main` または `develop` ブランチへのプッシュ
- プルリクエストの作成

#### 実行内容
1. ✅ Python 3.10, 3.11, 3.12 でテスト
2. ✅ Djangoテストの実行
3. ✅ カバレッジ測定とレポート
4. ✅ コード品質チェック（flake8）
5. ✅ セキュリティスキャン（bandit, safety）

#### ワークフローの確認

GitHubリポジトリの「Actions」タブで実行結果を確認できます。

---

## テストの種類

### 1. 単体テスト (Unit Tests)

個々の関数やメソッドをテストします。

```python
class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Test")
        self.assertEqual(str(category), "Test")
```

### 2. 統合テスト (Integration Tests)

複数のコンポーネントの連携をテストします。

```python
class QuizAPITest(APITestCase):
    def test_save_quiz_result(self):
        # APIを通じてクイズ結果を保存
        response = self.client.post('/api/quiz/save-result/', data)
        self.assertEqual(response.status_code, 201)
```

### 3. 認証テスト

認証・認可の動作をテストします。

```python
class AuthenticationTest(APITestCase):
    def test_unauthenticated_access(self):
        response = self.client.get('/api/user/stats/')
        self.assertEqual(response.status_code, 401)
```

---

## テストの追加方法

### 新しいテストの作成

`quiz_api/tests.py` に新しいテストクラスを追加：

```python
class NewFeatureTest(TestCase):
    def setUp(self):
        # テスト前の準備
        self.user = User.objects.create_user(username='test')

    def test_new_feature(self):
        # テストロジック
        result = my_function()
        self.assertEqual(result, expected_value)
```

### テストのベストプラクティス

1. **明確なテスト名**: 何をテストしているか分かる名前にする
2. **独立性**: テスト間で依存関係を持たない
3. **高速**: テストは素早く実行できるようにする
4. **信頼性**: 同じ結果が再現できるようにする

---

## トラブルシューティング

### テストが失敗する場合

```bash
# 詳細なエラー情報を表示
python manage.py test quiz_api --verbosity=2

# 特定のテストのみ実行
python manage.py test quiz_api.tests.CategoryModelTest.test_category_creation
```

### カバレッジが表示されない

```bash
# .coverage ファイルを削除して再実行
rm .coverage
coverage run manage.py test quiz_api
coverage report
```

---

## 本番環境へのデプロイ前チェックリスト

- [ ] すべてのテストが成功している
- [ ] カバレッジが目標値（例: 80%以上）に達している
- [ ] CI/CD パイプラインが成功している
- [ ] セキュリティスキャンでエラーがない
- [ ] マイグレーションが正しく適用される
- [ ] 静的ファイルが収集されている

---

## 参考リンク

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
