# デプロイメントガイド - 環境管理とソース管理

## 📋 目次
1. [環境の種類](#環境の種類)
2. [Git ブランチ戦略](#git-ブランチ戦略)
3. [環境別設定管理](#環境別設定管理)
4. [デプロイメントフロー](#デプロイメントフロー)
5. [環境変数管理](#環境変数管理)
6. [データベース管理](#データベース管理)
7. [CI/CD パイプライン](#cicd-パイプライン)

---

## 環境の種類

### 推奨される環境構成

```
開発環境 (Development) → テスト環境 (Staging) → 本番環境 (Production)
```

#### 1. **開発環境 (Development)**
- **目的**: 機能開発、バグ修正
- **場所**: ローカルマシン
- **データ**: テストデータ
- **デバッグ**: 有効
- **URL**: `localhost:8000`, `localhost:8082`

#### 2. **テスト環境 (Staging)**
- **目的**: 本番環境のシミュレーション、統合テスト
- **場所**: サーバー (本番環境と同じ構成)
- **データ**: 本番に近いテストデータ
- **デバッグ**: 無効
- **URL**: `staging.magicalquiz.example.com`

#### 3. **本番環境 (Production)**
- **目的**: エンドユーザーへのサービス提供
- **場所**: 本番サーバー
- **データ**: 実際のユーザーデータ
- **デバッグ**: 無効
- **URL**: `magicalquiz.example.com`

---

## Git ブランチ戦略

### Git Flow モデル (推奨)

```
main (本番環境)
  ↑
  └── release/* (リリース準備)
       ↑
       └── develop (テスト環境)
            ↑
            ├── feature/* (機能開発)
            ├── bugfix/* (バグ修正)
            └── hotfix/* (緊急修正)
```

### ブランチの役割

#### 1. **main ブランチ**
```bash
# 本番環境にデプロイされるブランチ
# 常に安定した状態を維持
# 直接コミットは禁止
```

**ルール**:
- ✅ `release/*` または `hotfix/*` からのマージのみ
- ✅ すべてのテストが合格している
- ✅ コードレビュー必須
- ❌ 直接プッシュ禁止

#### 2. **develop ブランチ**
```bash
# テスト環境にデプロイされるブランチ
# 次のリリースの開発ブランチ
```

**ルール**:
- ✅ `feature/*`, `bugfix/*` からのマージ
- ✅ テストが合格している
- ✅ Pull Request経由でのマージ

#### 3. **feature/* ブランチ**
```bash
# 新機能開発用ブランチ
git checkout -b feature/add-quiz-timer develop
```

**命名規則**:
- `feature/リーダーボード機能追加`
- `feature/quiz-timer-implementation`
- `feature/user-profile-enhancement`

**ワークフロー**:
```bash
# 機能開発開始
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 開発
git add .
git commit -m "feat: 新機能を追加"

# developにマージ
git checkout develop
git merge feature/new-feature
git push origin develop

# ブランチ削除
git branch -d feature/new-feature
```

#### 4. **release/* ブランチ**
```bash
# リリース準備用ブランチ
git checkout -b release/1.2.0 develop
```

**目的**:
- バージョン番号の更新
- 軽微なバグ修正
- リリースノート作成

**ワークフロー**:
```bash
# リリース準備
git checkout -b release/1.2.0 develop

# バージョン更新、最終調整
git commit -m "chore: version 1.2.0"

# mainにマージ
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Version 1.2.0"

# developにもマージ
git checkout develop
git merge --no-ff release/1.2.0

# ブランチ削除
git branch -d release/1.2.0
```

#### 5. **hotfix/* ブランチ**
```bash
# 本番環境の緊急バグ修正
git checkout -b hotfix/critical-bug main
```

**ワークフロー**:
```bash
# 緊急修正
git checkout -b hotfix/critical-bug main

# 修正
git commit -m "fix: 緊急バグを修正"

# mainにマージ
git checkout main
git merge --no-ff hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix 1.2.1"

# developにもマージ
git checkout develop
git merge --no-ff hotfix/critical-bug

# ブランチ削除
git branch -d hotfix/critical-bug
```

---

## 環境別設定管理

### Django 設定の分離

#### ディレクトリ構造
```
quiz_project/
├── settings/
│   ├── __init__.py
│   ├── base.py          # 共通設定
│   ├── development.py   # 開発環境
│   ├── staging.py       # テスト環境
│   └── production.py    # 本番環境
├── manage.py
└── wsgi.py
```

#### base.py (共通設定)
```python
# quiz_project/settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 共通設定
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'rest_framework',
    'quiz_api',
]

# 共通ミドルウェア
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ...
]

# データベース設定は環境別に定義
```

#### development.py (開発環境)
```python
# quiz_project/settings/development.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS設定 (開発用)
CORS_ALLOW_ALL_ORIGINS = True

# メール設定 (コンソール出力)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### staging.py (テスト環境)
```python
# quiz_project/settings/staging.py
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['staging.magicalquiz.example.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# CORS設定
CORS_ALLOWED_ORIGINS = [
    'https://staging.magicalquiz.example.com',
]

# 静的ファイル
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# メディアファイル
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

#### production.py (本番環境)
```python
# quiz_project/settings/production.py
from .base import *
import os

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ['magicalquiz.example.com', 'www.magicalquiz.example.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# セキュリティ設定
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS設定
CORS_ALLOWED_ORIGINS = [
    'https://magicalquiz.example.com',
    'https://www.magicalquiz.example.com',
]

# 静的ファイル (S3やCDNを使用)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# ロギング設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 設定の使い分け

#### manage.py で環境を指定
```python
# manage.py
import os
import sys

def main():
    # 環境変数から設定を選択
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'quiz_project.settings.development')
    # ...
```

#### 起動時に環境指定
```bash
# 開発環境
export DJANGO_SETTINGS_MODULE=quiz_project.settings.development
python manage.py runserver

# テスト環境
export DJANGO_SETTINGS_MODULE=quiz_project.settings.staging
python manage.py runserver

# 本番環境
export DJANGO_SETTINGS_MODULE=quiz_project.settings.production
gunicorn quiz_project.wsgi:application
```

---

## 環境変数管理

### .env ファイルの使用

#### 開発環境 (.env.development)
```bash
# .env.development
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (開発用)
STRIPE_TEST_KEY=sk_test_xxxxx
EMAIL_HOST_USER=test@example.com
```

#### テスト環境 (.env.staging)
```bash
# .env.staging
DEBUG=False
SECRET_KEY=staging-secret-key-change-in-production
DATABASE_URL=postgresql://user:pass@db-staging.example.com:5432/quiz_db
ALLOWED_HOSTS=staging.magicalquiz.example.com

# API Keys (テスト用)
STRIPE_TEST_KEY=sk_test_xxxxx
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=staging@magicalquiz.example.com
EMAIL_HOST_PASSWORD=staging_password
```

#### 本番環境 (.env.production)
```bash
# .env.production
DEBUG=False
SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY
DATABASE_URL=postgresql://user:pass@db-prod.example.com:5432/quiz_db
ALLOWED_HOSTS=magicalquiz.example.com,www.magicalquiz.example.com

# API Keys (本番用)
STRIPE_LIVE_KEY=sk_live_xxxxx
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply@magicalquiz.example.com
EMAIL_HOST_PASSWORD=secure_production_password

# AWS (本番環境)
AWS_ACCESS_KEY_ID=AKIAXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_STORAGE_BUCKET_NAME=magicalquiz-media
```

### python-decouple の使用

#### インストール
```bash
pip install python-decouple
```

#### 使用方法
```python
# settings/base.py
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

### .gitignore に追加
```gitignore
# .gitignore
.env
.env.*
*.env
!.env.example

# 環境別設定ファイル
/quiz_project/settings/local.py
```

### .env.example を作成
```bash
# .env.example (テンプレート)
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## デプロイメントフロー

### 1. 機能開発からテスト環境へ

```bash
# 1. 機能ブランチ作成
git checkout develop
git checkout -b feature/new-quiz-mode

# 2. 開発
# ... コーディング ...
git add .
git commit -m "feat: 新しいクイズモードを追加"

# 3. テストを実行
./run_tests.sh

# 4. developにマージ
git checkout develop
git merge feature/new-quiz-mode

# 5. テスト環境にデプロイ
git push origin develop
# → CI/CDが自動的にテスト環境にデプロイ
```

### 2. テスト環境から本番環境へ

```bash
# 1. リリースブランチ作成
git checkout -b release/1.3.0 develop

# 2. バージョン更新
# - package.json のバージョン更新
# - CHANGELOG.md の更新
git commit -m "chore: bump version to 1.3.0"

# 3. mainにマージ
git checkout main
git merge --no-ff release/1.3.0
git tag -a v1.3.0 -m "Release version 1.3.0"

# 4. 本番環境にデプロイ
git push origin main
git push origin v1.3.0
# → CI/CDが自動的に本番環境にデプロイ

# 5. developにもマージ (最新状態を保つ)
git checkout develop
git merge --no-ff release/1.3.0
git push origin develop

# 6. リリースブランチ削除
git branch -d release/1.3.0
```

### 3. 緊急修正 (Hotfix)

```bash
# 1. hotfixブランチ作成 (mainから)
git checkout main
git checkout -b hotfix/critical-security-fix

# 2. 修正
# ... バグ修正 ...
git commit -m "fix: セキュリティ脆弱性を修正"

# 3. テスト
./run_tests.sh

# 4. mainにマージ
git checkout main
git merge --no-ff hotfix/critical-security-fix
git tag -a v1.3.1 -m "Hotfix 1.3.1 - Security fix"

# 5. 本番環境に即座にデプロイ
git push origin main
git push origin v1.3.1

# 6. developにもマージ
git checkout develop
git merge --no-ff hotfix/critical-security-fix
git push origin develop

# 7. hotfixブランチ削除
git branch -d hotfix/critical-security-fix
```

---

## データベース管理

### マイグレーションの管理

#### 開発環境
```bash
# マイグレーション作成
python manage.py makemigrations

# マイグレーション適用
python manage.py migrate
```

#### テスト環境
```bash
# テスト環境にSSH
ssh user@staging-server

# アプリケーションディレクトリに移動
cd /var/www/magicalquiz

# マイグレーション適用
source venv/bin/activate
python manage.py migrate --settings=quiz_project.settings.staging

# サーバー再起動
sudo systemctl restart gunicorn
```

#### 本番環境
```bash
# バックアップを取る
pg_dump quiz_db > backup_$(date +%Y%m%d_%H%M%S).sql

# マイグレーション適用
python manage.py migrate --settings=quiz_project.settings.production

# ロールバック用にマイグレーション履歴を保存
python manage.py showmigrations > migrations_applied.txt
```

### データベースバックアップ戦略

#### 自動バックアップスクリプト
```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/var/backups/magicalquiz"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="quiz_db"
DB_USER="quiz_user"

# バックアップ作成
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# 7日以上古いバックアップを削除
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

#### Crontabに追加
```bash
# 毎日午前3時にバックアップ
0 3 * * * /usr/local/bin/backup_db.sh
```

---

## CI/CD パイプライン

### GitHub Actions 設定例

#### .github/workflows/test.yml
```yaml
name: Tests

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

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
        export DJANGO_SETTINGS_MODULE=quiz_project.settings.development
        python manage.py test quiz_api.tests

    - name: Run linter
      run: |
        cd quiz-frontend
        npm install
        npm run lint
```

#### .github/workflows/deploy-staging.yml
```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Deploy to staging server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USER }}
        key: ${{ secrets.STAGING_SSH_KEY }}
        script: |
          cd /var/www/magicalquiz
          git pull origin develop
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py migrate --settings=quiz_project.settings.staging
          python manage.py collectstatic --noinput --settings=quiz_project.settings.staging
          sudo systemctl restart gunicorn
```

#### .github/workflows/deploy-production.yml
```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Run tests before deployment
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd quiz_project
        python manage.py test quiz_api.tests

    - name: Deploy to production server
      if: success()
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USER }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          cd /var/www/magicalquiz
          git fetch --tags
          git checkout ${{ github.ref_name }}
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py migrate --settings=quiz_project.settings.production
          python manage.py collectstatic --noinput --settings=quiz_project.settings.production
          sudo systemctl restart gunicorn
```

---

## チェックリスト

### デプロイ前チェックリスト

#### テスト環境デプロイ
- [ ] すべてのテストが合格
- [ ] コードレビュー完了
- [ ] マイグレーションファイル確認
- [ ] 環境変数設定確認
- [ ] developブランチにマージ

#### 本番環境デプロイ
- [ ] テスト環境での動作確認完了
- [ ] データベースバックアップ取得
- [ ] リリースノート作成
- [ ] ロールバック手順確認
- [ ] ダウンタイムの通知 (必要な場合)
- [ ] mainブランチにマージ
- [ ] タグ作成 (v1.x.x)

---

## トラブルシューティング

### デプロイ失敗時の対処

#### 1. ロールバック
```bash
# 前のバージョンにロールバック
git checkout v1.2.0
sudo systemctl restart gunicorn
```

#### 2. データベースのロールバック
```bash
# バックアップから復元
psql -U quiz_user -d quiz_db < backup_20250125_030000.sql
```

#### 3. ログ確認
```bash
# Django ログ
tail -f /var/log/django/error.log

# Gunicorn ログ
tail -f /var/log/gunicorn/error.log

# Nginx ログ
tail -f /var/log/nginx/error.log
```

---

## まとめ

このドキュメントに従って環境管理を行うことで:
- ✅ 本番環境とテスト環境を明確に分離
- ✅ Git によるバージョン管理の徹底
- ✅ 環境変数による設定の柔軟な管理
- ✅ CI/CD による自動デプロイ
- ✅ データベースの安全な管理

を実現できます。
