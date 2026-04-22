# Gitセットアップとリポジトリ初期化ガイド

## 📋 前提条件

このガイドは、マジカルクイズプロジェクトをGitで管理するための手順です。

---

## 🔧 Gitのインストール

### WSL/Ubuntu の場合
```bash
sudo apt-get update
sudo apt-get install git
```

### 確認
```bash
git --version
# git version 2.x.x と表示されればOK
```

---

## ⚙️ Git初期設定

### ユーザー情報の設定
```bash
# グローバル設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 確認
git config --list
```

### 推奨設定
```bash
# デフォルトブランチ名を main に設定
git config --global init.defaultBranch main

# カラー出力を有効化
git config --global color.ui auto

# エディタを設定 (例: vim)
git config --global core.editor "vim"

# 改行コードの自動変換を無効化 (推奨)
git config --global core.autocrlf input
```

---

## 📦 リポジトリの初期化

### プロジェクトディレクトリで実行

```bash
cd /home/kensukemt2/django

# Gitリポジトリを初期化
git init

# 初期ブランチを main に変更 (既に設定している場合は不要)
git branch -M main
```

---

## 📝 初回コミット

### ステージング
```bash
# すべてのファイルを追加
git add .

# 追加されるファイルを確認
git status
```

### コミット
```bash
# 初回コミット
git commit -m "feat: 初期コミット - マジカルクイズアプリケーション

- Django 5.2.3 バックエンド
- Vue.js 3 フロントエンド
- REST API with JWT認証
- クイズ機能、リーダーボード機能
- 自動テストスイート (24テスト)
- デプロイメントドキュメント完備"
```

---

## 🌐 GitHubリポジトリとの連携

### GitHub上でリポジトリを作成

1. https://github.com にアクセス
2. 「New repository」をクリック
3. リポジトリ名を入力 (例: `magical-quiz`)
4. 「Create repository」をクリック

### リモートリポジトリを追加
```bash
# HTTPSの場合
git remote add origin https://github.com/your-username/magical-quiz.git

# SSHの場合
git remote add origin git@github.com:your-username/magical-quiz.git

# 確認
git remote -v
```

### プッシュ
```bash
# 初回プッシュ
git push -u origin main

# 以降は
git push
```

---

## 🌿 ブランチ戦略の実装

### developブランチを作成
```bash
# developブランチを作成
git checkout -b develop

# GitHubにプッシュ
git push -u origin develop

# mainブランチに戻る
git checkout main
```

### ブランチ保護設定 (GitHub上で)

#### mainブランチの保護
1. リポジトリ設定 → Branches
2. Add rule
3. Branch name pattern: `main`
4. 設定:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Include administrators

#### developブランチの保護
同様の手順で `develop` も保護

---

## 📋 コミット規約

### コミットメッセージの形式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (必須)
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの意味に影響しない変更 (フォーマット等)
- `refactor`: リファクタリング
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

### 例
```bash
# 機能追加
git commit -m "feat: クイズタイマー機能を追加"

# バグ修正
git commit -m "fix: リーダーボードのソート順が逆だった問題を修正"

# ドキュメント更新
git commit -m "docs: デプロイメントガイドを更新"

# テスト追加
git commit -m "test: リーダーボードAPIのテストを追加"
```

---

## 🔄 日常的なGit操作

### 機能開発の流れ
```bash
# 1. 最新状態を取得
git checkout develop
git pull origin develop

# 2. 機能ブランチを作成
git checkout -b feature/quiz-timer

# 3. 開発
# ... コーディング ...

# 4. ステージング & コミット
git add .
git commit -m "feat: クイズタイマー機能を実装"

# 5. リモートにプッシュ
git push -u origin feature/quiz-timer

# 6. GitHub上でPull Requestを作成
# - feature/quiz-timer → develop

# 7. レビュー & マージ後、ローカルを更新
git checkout develop
git pull origin develop

# 8. 機能ブランチを削除
git branch -d feature/quiz-timer
```

### よく使うコマンド
```bash
# 状態確認
git status

# 変更履歴
git log --oneline --graph --all

# 差分確認
git diff

# 特定のファイルの変更を取り消す
git checkout -- <file>

# ステージングを取り消す
git reset HEAD <file>

# 直前のコミットを修正
git commit --amend

# ブランチ一覧
git branch -a

# ブランチ切り替え
git checkout <branch-name>
```

---

## 🚀 現在の状態をGitに登録

### 手順

1. **Gitのインストール確認**
```bash
git --version
```

2. **Git設定**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

3. **プロジェクトディレクトリに移動**
```bash
cd /home/kensukemt2/django
```

4. **Gitリポジトリを初期化**
```bash
git init
git branch -M main
```

5. **ファイルを追加**
```bash
# .gitignore が正しく設定されているか確認
cat .gitignore

# すべてのファイルを追加
git add .

# 追加されるファイルを確認
git status
```

6. **初回コミット**
```bash
git commit -m "feat: 初期コミット - マジカルクイズアプリケーション

## 機能
- Django 5.2.3 REST APIバックエンド
- Vue.js 3 フロントエンド
- JWT認証システム
- クイズ機能 (カテゴリ別、画像問題対応)
- リーダーボード (カテゴリフィルタリング対応)
- ユーザープロフィール
- クイズ履歴

## テスト
- 自動テストスイート (24テスト、100%合格)
- テスト実行スクリプト (run_tests.sh)
- カバレッジ測定対応

## ドキュメント
- TESTING.md: テストドキュメント
- DEPLOYMENT.md: デプロイメントガイド
- DEPLOYMENT_CHECKLIST.md: デプロイチェックリスト
- .env.example: 環境変数テンプレート
- README.md: プロジェクト概要

## セキュリティ
- .gitignore で秘密情報を除外
- 環境変数による設定管理
- セキュアな認証実装"
```

7. **developブランチを作成**
```bash
git checkout -b develop
git checkout main
```

8. **GitHubリポジトリを作成して連携**
```bash
# GitHubでリポジトリ作成後
git remote add origin https://github.com/your-username/magical-quiz.git

# プッシュ
git push -u origin main
git push -u origin develop
```

---

## 📊 現在のプロジェクト構成

### 追加されるファイル
```
/home/kensukemt2/django/
├── .gitignore                      # Git管理除外ファイル
├── .env.example                    # 環境変数テンプレート
├── run_tests.sh                    # テスト自動実行スクリプト
├── TESTING.md                      # テストドキュメント
├── DEPLOYMENT.md                   # デプロイメントガイド
├── DEPLOYMENT_CHECKLIST.md         # デプロイチェックリスト
├── GIT_SETUP.md                    # このファイル
├── quiz_project/                   # Djangoバックエンド
│   ├── manage.py
│   ├── quiz_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── quiz_api/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── admin.py
│       ├── tests.py                # 24個のテスト
│       └── urls.py
└── quiz-frontend/                  # Vue.jsフロントエンド
    ├── package.json
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.vue
    │   │   ├── Home.vue
    │   │   ├── Quiz.vue
    │   │   ├── Leaderboard.vue
    │   │   ├── Profile.vue
    │   │   ├── History.vue
    │   │   ├── About.vue
    │   │   ├── Contact.vue
    │   │   └── PrivacyPolicy.vue
    │   ├── router/
    │   │   └── index.js
    │   ├── store/
    │   └── App.vue
    └── public/
```

### 除外されるファイル (.gitignore)
```
- .env, .env.*              # 環境変数 (秘密情報)
- db.sqlite3                # データベース
- media/                    # アップロードファイル
- staticfiles/              # 静的ファイル (収集後)
- __pycache__/              # Python キャッシュ
- node_modules/             # Node.js 依存関係
- venv/, env/               # 仮想環境
- *.log                     # ログファイル
- *.sql                     # データベースバックアップ
```

---

## 🔒 セキュリティチェックリスト

コミット前に確認:

- [ ] `.env` ファイルがコミットされていない
- [ ] `db.sqlite3` がコミットされていない
- [ ] `SECRET_KEY` などの秘密情報が含まれていない
- [ ] `.gitignore` が正しく設定されている
- [ ] パスワードやAPIキーが含まれていない

### 確認コマンド
```bash
# コミット予定のファイルを確認
git status

# 秘密情報が含まれていないか検索
git diff --cached | grep -i "secret\|password\|key"
```

---

## 💡 トラブルシューティング

### 誤ってコミットしてしまった場合

```bash
# 直前のコミットを取り消す (変更は保持)
git reset --soft HEAD~1

# 直前のコミットを完全に取り消す
git reset --hard HEAD~1
```

### 秘密情報をコミットしてしまった場合

```bash
# 履歴から完全に削除 (BFG Repo-Cleaner を使用)
# https://rtyley.github.io/bfg-repo-cleaner/

# または git filter-branch (非推奨だが利用可能)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

⚠️ **注意**: 履歴を書き換えた場合は、強制プッシュが必要
```bash
git push --force-with-lease origin main
```

---

## 📚 参考資料

- [Git 公式ドキュメント](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ✅ 完了確認

以下をすべて完了したら、Gitセットアップ完了です:

- [ ] Gitのインストール
- [ ] Git初期設定
- [ ] リポジトリの初期化
- [ ] 初回コミット
- [ ] GitHubリポジトリとの連携
- [ ] developブランチの作成
- [ ] ブランチ保護設定

**お疲れさまでした! 🎉**
