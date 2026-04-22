# デプロイチェックリスト

## 📋 環境準備

### 初回セットアップ

#### ローカル開発環境
```bash
# プロジェクトをクローン
git clone https://github.com/your-org/magical-quiz.git
cd magical-quiz

# バックエンド設定
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集して適切な値を設定

# データベースセットアップ
cd quiz_project
python manage.py migrate
python manage.py createsuperuser

# フロントエンド設定
cd ../quiz-frontend
npm install

# サーバー起動
# Terminal 1: Django
cd quiz_project && python manage.py runserver

# Terminal 2: Vue
cd quiz-frontend && npm run serve
```

---

## 🚀 デプロイ前チェックリスト

### テスト環境へのデプロイ

- [ ] **コード品質**
  - [ ] すべてのテストが合格 (`./run_tests.sh`)
  - [ ] ESLintエラーなし (`npm run lint`)
  - [ ] コードレビュー完了
  - [ ] 新機能のドキュメント更新

- [ ] **Git操作**
  - [ ] `feature/*` ブランチから `develop` にマージ
  - [ ] コンフリクト解消
  - [ ] コミットメッセージが明確

- [ ] **環境設定**
  - [ ] テスト環境の環境変数確認
  - [ ] データベース接続設定確認
  - [ ] CORS設定確認

- [ ] **データベース**
  - [ ] マイグレーションファイル確認
  - [ ] テスト環境DBバックアップ取得

- [ ] **通知**
  - [ ] チームへデプロイ通知
  - [ ] ダウンタイムの有無を確認

### 本番環境へのデプロイ

- [ ] **事前確認**
  - [ ] テスト環境での動作確認完了
  - [ ] ユーザー受け入れテスト完了
  - [ ] パフォーマンステスト完了
  - [ ] セキュリティチェック完了

- [ ] **バックアップ**
  - [ ] 本番データベース完全バックアップ
  - [ ] メディアファイルバックアップ
  - [ ] 現在の設定ファイルバックアップ
  - [ ] バックアップの検証

- [ ] **リリース準備**
  - [ ] リリースノート作成
  - [ ] `release/*` ブランチ作成
  - [ ] バージョン番号更新
  - [ ] CHANGELOG.md 更新

- [ ] **本番環境設定**
  - [ ] 環境変数の最終確認
  - [ ] `DEBUG=False` 確認
  - [ ] `SECRET_KEY` が本番用に設定
  - [ ] `ALLOWED_HOSTS` が正しく設定
  - [ ] セキュリティ設定確認
    - [ ] `SECURE_SSL_REDIRECT=True`
    - [ ] `SESSION_COOKIE_SECURE=True`
    - [ ] `CSRF_COOKIE_SECURE=True`

- [ ] **デプロイ実行**
  - [ ] メンテナンスモード有効化 (必要な場合)
  - [ ] コードデプロイ
  - [ ] 依存関係インストール
  - [ ] データベースマイグレーション実行
  - [ ] 静的ファイル収集
  - [ ] サービス再起動

- [ ] **デプロイ後確認**
  - [ ] サービスが正常に起動
  - [ ] ログにエラーなし
  - [ ] 主要機能の動作確認
    - [ ] ログイン/ログアウト
    - [ ] クイズ実行
    - [ ] 結果保存
    - [ ] リーダーボード表示
  - [ ] パフォーマンス確認
  - [ ] メンテナンスモード解除

- [ ] **事後処理**
  - [ ] `main` ブランチにマージ
  - [ ] タグ作成 (`v1.x.x`)
  - [ ] `develop` にマージバック
  - [ ] リリースノート公開
  - [ ] ユーザーへの通知
  - [ ] チームへの完了報告

---

## 🔥 ホットフィックスデプロイ

### 緊急バグ修正手順

- [ ] **準備**
  - [ ] 問題の特定と影響範囲確認
  - [ ] ロールバックプラン作成
  - [ ] チームへの緊急通知

- [ ] **修正**
  - [ ] `main` から `hotfix/*` ブランチ作成
  - [ ] 最小限の修正実装
  - [ ] テスト実行
  - [ ] コードレビュー (可能な限り)

- [ ] **デプロイ**
  - [ ] 本番データベースバックアップ
  - [ ] `main` にマージ
  - [ ] タグ作成 (パッチバージョンアップ)
  - [ ] 即座にデプロイ実行
  - [ ] 動作確認

- [ ] **事後処理**
  - [ ] `develop` にもマージ
  - [ ] インシデントレポート作成
  - [ ] 再発防止策の検討

---

## 🔄 ロールバック手順

### 問題発生時の対処

#### 1. コードのロールバック
```bash
# 前のバージョンに戻る
git checkout v1.2.0  # 前の安定バージョン
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

#### 2. データベースのロールバック
```bash
# バックアップから復元
sudo systemctl stop gunicorn

# 最新のバックアップを確認
ls -lt /var/backups/magicalquiz/

# 復元
psql -U quiz_user -d quiz_db < backup_20250125_030000.sql

# サービス再起動
sudo systemctl start gunicorn
```

#### 3. 確認
```bash
# ログ確認
tail -f /var/log/gunicorn/error.log
tail -f /var/log/nginx/error.log

# サービス状態確認
sudo systemctl status gunicorn
sudo systemctl status nginx

# 動作確認
curl https://magicalquiz.example.com/api/categories/
```

---

## 📊 デプロイ後の監視

### 監視項目

#### 即座に確認 (デプロイ後5分以内)
- [ ] サービスの起動状態
- [ ] エラーログ
- [ ] 主要ページのレスポンスタイム
- [ ] APIエンドポイントの応答

#### 短期監視 (デプロイ後1時間)
- [ ] ユーザーからの問い合わせ
- [ ] エラー率の変化
- [ ] レスポンスタイムの変化
- [ ] データベース接続数

#### 中期監視 (デプロイ後24時間)
- [ ] ユーザーアクティビティ
- [ ] サーバーリソース使用率
- [ ] データベースパフォーマンス
- [ ] エラーの傾向

---

## 🛠️ トラブルシューティング

### よくある問題と対処法

#### サービスが起動しない
```bash
# ログ確認
journalctl -u gunicorn -n 50
journalctl -u nginx -n 50

# 設定ファイルの確認
sudo nginx -t
sudo systemctl status gunicorn
```

#### データベース接続エラー
```bash
# 接続テスト
psql -U quiz_user -d quiz_db -h localhost

# Django設定確認
python manage.py dbshell

# 環境変数確認
echo $DB_NAME
echo $DB_USER
```

#### 静的ファイルが表示されない
```bash
# 静的ファイル収集
python manage.py collectstatic --noinput

# Nginx設定確認
sudo nginx -t
sudo cat /etc/nginx/sites-available/magicalquiz

# パーミッション確認
ls -la /var/www/magicalquiz/staticfiles/
```

---

## 📞 緊急連絡先

### エスカレーション手順

1. **レベル1**: 開発チームリード
   - 軽微な問題、予期された動作

2. **レベル2**: プロジェクトマネージャー
   - サービス停止、データ損失の可能性

3. **レベル3**: 経営層
   - 重大なセキュリティ問題、長期のサービス停止

---

## 📝 デプロイ記録

### デプロイ履歴テンプレート

```markdown
## デプロイ: v1.3.0 → v1.4.0

**日時**: 2025-01-25 15:00 JST
**担当者**: 山田太郎
**環境**: 本番環境

### 変更内容
- 新機能: クイズタイマー機能追加
- 改善: リーダーボードのパフォーマンス向上
- 修正: ログイン時のバグ修正

### デプロイ手順
1. データベースバックアップ: ✅ 完了 (15:00)
2. メンテナンスモード: ✅ 有効化 (15:05)
3. コードデプロイ: ✅ 完了 (15:10)
4. マイグレーション: ✅ 完了 (15:15)
5. サービス再起動: ✅ 完了 (15:18)
6. 動作確認: ✅ 完了 (15:25)
7. メンテナンスモード解除: ✅ (15:30)

### 確認項目
- [x] ログイン/ログアウト
- [x] クイズ実行
- [x] タイマー機能
- [x] リーダーボード表示
- [x] パフォーマンス正常

### 問題点
- なし

### 備考
- 予定通り30分でデプロイ完了
- ユーザー影響なし
```

---

## ✅ 完了!

すべてのチェック項目を確認したら、デプロイは完了です。

**お疲れさまでした! 🎉**
