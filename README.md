# クイズアプリケーション

Django REST Framework + Vue.js で構築された、カテゴリ別クイズシステムです。ユーザー認証、スコア管理、リーダーボード機能を備えています。

## 📋 目次

- [プロジェクト概要](#プロジェクト概要)
- [主な機能](#主な機能)
- [技術スタック](#技術スタック)
- [クイックスタート](#クイックスタート)
- [ドキュメント](#ドキュメント)
- [ライセンス](#ライセンス)

## プロジェクト概要

このアプリケーションは、複数カテゴリのクイズを提供し、ユーザーの学習進捗を管理できるシステムです。管理者は問題の追加・編集、ユーザーは自分のペースで学習し、成績を確認できます。

### システム構成

```
quiz-app/
├── quiz_project/          # Django バックエンド
│   ├── quiz_api/         # メインアプリケーション
│   └── quiz_project/     # プロジェクト設定
└── quiz-frontend/         # Vue.js フロントエンド
```

## 主な機能

### ユーザー機能
- ユーザー登録・ログイン（JWT認証）
- カテゴリ別クイズの受験
- 問題のランダム出題（重複なし）
- クイズ履歴の閲覧
- スコア統計の確認
- リーダーボード表示

### 管理者機能
- カテゴリの管理（追加・編集・削除）
- 問題の管理（追加・編集・削除）
- 選択肢の管理
- 問題画像のアップロード
- ユーザー管理
- データのインポート/エクスポート

### 技術的特徴
- セッション管理による重複なし出題
- ランダム問題取得API（複数モード）
- カテゴリ別統計集計
- レスポンシブデザイン
- RESTful API設計

## 技術スタック

### バックエンド
- **Python** 3.11+
- **Django** 5.1.6
- **Django REST Framework** - REST API構築
- **djangorestframework-simplejwt** - JWT認証
- **django-cors-headers** - CORS設定
- **django-import-export** - データインポート/エクスポート
- **django-extensions** - 開発支援ツール
- **SQLite** - データベース（開発環境）

### フロントエンド
- **Vue.js** 3.2
- **Vue Router** 4.5 - ルーティング
- **Vuex** 4.1 - 状態管理
- **Axios** 1.8 - HTTP通信
- **vue-toastification** - 通知UI

## クイックスタート

### 前提条件
- Python 3.11以上
- Node.js 14以上
- npm または yarn

### 1. バックエンドのセットアップ

```bash
# リポジトリをクローン
cd quiz_project

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install django djangorestframework django-cors-headers
pip install djangorestframework-simplejwt django-import-export django-extensions

# データベースのマイグレーション
python manage.py migrate

# 管理者ユーザーの作成
python manage.py createsuperuser

# 開発サーバーの起動
python manage.py runserver
```

バックエンドは http://localhost:8000 で起動します。

### 2. フロントエンドのセットアップ

```bash
# フロントエンドディレクトリに移動
cd quiz-frontend

# 依存パッケージのインストール
npm install

# 開発サーバーの起動
npm run serve
```

フロントエンドは http://localhost:8080 で起動します。

### 3. 初期データの登録

管理画面（http://localhost:8000/admin）にアクセスして、以下を登録します:

1. カテゴリの作成
2. 問題の作成
3. 各問題に選択肢を追加（正解を1つ設定）

または、データのインポート機能を使用して一括登録も可能です。

## ドキュメント

詳細なドキュメントは以下を参照してください:

- [ARCHITECTURE.md](./ARCHITECTURE.md) - システムアーキテクチャと設計
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API仕様とエンドポイント
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - データベース設計
- [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) - 開発ガイドとベストプラクティス

## プロジェクト構造

```
.
├── quiz_project/                 # Djangoバックエンド
│   ├── manage.py                # Django管理コマンド
│   ├── db.sqlite3              # SQLiteデータベース
│   ├── media/                  # アップロードファイル
│   ├── quiz_api/               # メインアプリケーション
│   │   ├── models.py          # データモデル
│   │   ├── views.py           # APIビュー
│   │   ├── serializers.py     # シリアライザ
│   │   ├── urls.py            # URLルーティング
│   │   └── admin.py           # 管理画面設定
│   └── quiz_project/          # プロジェクト設定
│       ├── settings.py        # Django設定
│       └── urls.py            # ルートURL設定
│
└── quiz-frontend/              # Vue.jsフロントエンド
    ├── public/                # 静的ファイル
    ├── src/
    │   ├── components/        # Vueコンポーネント
    │   │   ├── Home.vue      # ホーム画面
    │   │   ├── Quiz.vue      # クイズ画面
    │   │   ├── Login.vue     # ログイン画面
    │   │   ├── Register.vue  # 登録画面
    │   │   ├── Profile.vue   # プロフィール画面
    │   │   ├── History.vue   # 履歴画面
    │   │   └── Leaderboard.vue # リーダーボード
    │   ├── store/            # Vuex ストア
    │   │   ├── modules/
    │   │   │   ├── auth.js  # 認証モジュール
    │   │   │   ├── quiz.js  # クイズモジュール
    │   │   │   └── user.js  # ユーザーモジュール
    │   │   └── index.js     # ストア設定
    │   ├── router/          # Vue Router
    │   ├── utils/           # ユーティリティ
    │   └── main.js          # エントリーポイント
    └── package.json         # npm設定

```

## API エンドポイント概要

### 認証
- `POST /api/register/` - ユーザー登録
- `POST /api/token/` - ログイン（トークン取得）
- `POST /api/token/refresh/` - トークン更新

### クイズ
- `GET /api/categories/` - カテゴリ一覧
- `GET /api/questions/` - 問題一覧
- `GET /api/questions/random_questions/` - ランダム問題取得
- `GET /api/questions/session_questions/` - セッション管理問題取得
- `POST /api/quiz/save-result/` - 結果保存

### ユーザー
- `GET /api/user/profile/` - プロフィール取得
- `GET /api/user/stats/` - 統計情報取得
- `GET /api/quiz/history/` - クイズ履歴
- `GET /api/quiz/leaderboard/` - リーダーボード

詳細は [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) を参照してください。

## 環境変数

本番環境では以下の環境変数を設定してください:

```bash
# Django設定
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# データベース（本番環境）
DATABASE_URL=postgres://user:password@localhost/dbname
```

## テスト

```bash
# バックエンドのテスト
cd quiz_project
python manage.py test

# フロントエンドのテスト
cd quiz-frontend
npm run test
```

## デプロイ

詳細なデプロイ手順は [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) を参照してください。

### 本番環境での注意事項
- `DEBUG = False` に設定
- `SECRET_KEY` を安全な値に変更
- `ALLOWED_HOSTS` を適切に設定
- PostgreSQLまたはMySQLの使用を推奨
- 静的ファイルの収集（`python manage.py collectstatic`）
- HTTPS接続の設定

## トラブルシューティング

### CORS エラー
フロントエンドとバックエンドが異なるポートで動作しているため、CORS設定が重要です。
`quiz_project/settings.py` の `CORS_ALLOWED_ORIGINS` を確認してください。

### データベースマイグレーションエラー
```bash
python manage.py makemigrations
python manage.py migrate
```

### 静的ファイルが表示されない
```bash
python manage.py collectstatic
```

## コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## サポート

問題が発生した場合は、以下を確認してください:
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API使用方法
- [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) - 開発ガイド
- GitHubのIssues

## 作成者

開発チーム

## 更新履歴

- 2025年 - 初版リリース
  - ユーザー認証機能
  - カテゴリ別クイズ機能
  - リーダーボード機能
  - セッション管理による重複なし出題
